# CopilotKit "Run Already Errored" Fix

## Problem

Error message appearing in console:
```
[FRONTEND] Agent execution failed: [Error: Cannot send event type 'RUN_FINISHED': 
The run has already errored with 'RUN_ERROR'. No further events can be sent.]
```

## Root Cause

1. **LangGraph execution fails** during storybook generation (e.g., API timeout, tool error)
2. **AG-UI adapter correctly sends `RUN_ERROR`** event and returns
3. **CopilotKit runtime** tries to send `RUN_FINISHED` after stream ends
4. **AG-UI protocol rejects** `RUN_FINISHED` because run is already in error state
5. **Exception thrown** in CopilotKit runtime, caught in route.ts

## Why This Happens

The AG-UI event protocol has a strict state machine:
- Once `RUN_ERROR` is sent, the run is in "errored" state
- No further events (including `RUN_FINISHED`) can be sent after `RUN_ERROR`
- CopilotKit runtime wasn't aware of this constraint and tried to send `RUN_FINISHED` anyway

## The Fix

### Backend (`backend/app/ag_ui/adapter.py`)

Added extra safety wrapping for event emission in error handler:

```python
try:
    yield encoder.encode(TextMessageEndEvent(...))
except Exception as end_err:
    print(f"[AG-UI Stream] Failed to send TEXT_MESSAGE_END: {end_err}")

try:
    yield encoder.encode(RunErrorEvent(...))
except Exception as error_event_err:
    print(f"[AG-UI Stream] Failed to send RUN_ERROR: {error_event_err}")
```

This prevents cascading errors if event emission itself fails.

### Frontend (`frontend/app/api/copilotkit/route.ts`)

Changed error handling to recognize this as **expected behavior**:

```typescript
// Suppress "run already errored" errors - these are expected
if (errorMessage.includes("run has already errored") || 
    errorMessage.includes("Cannot send event type")) {
  console.log("[COPILOTKIT] Stream ended with error state (expected behavior)");
  return new Response(null, { status: 200 }); // Success, not error
}
```

**Key change**: Returns `200 OK` instead of `500 Error` because:
- The error was properly communicated via `RUN_ERROR` event
- The stream ended cleanly
- The exception is just CopilotKit trying to send a redundant event
- The frontend will display the error from `RUN_ERROR` event

## What Changed for Users

Before:
- Console shows scary error messages
- Looks like something broke
- Status is 500 (confusing since error was handled)

After:
- Console shows: "Stream ended with error state (expected behavior)"
- Status is 200 (correct - error was handled properly)
- User still sees the actual error from the `RUN_ERROR` event

## Testing

1. Start the services:
   ```bash
   # Terminal 1 - Backend
   cd backend
   python run_agui_server.py
   
   # Terminal 2 - Frontend  
   cd frontend
   npm run dev
   ```

2. Trigger an error scenario:
   - Try to generate a storybook with invalid input
   - Or simulate a timeout in the LangGraph

3. Check console output:
   - Should see "Stream ended with error state (expected behavior)"
   - Should NOT see "Agent execution failed"
   - Status should be 200, not 500

## Technical Details

### AG-UI Event Flow (Normal)
```
RUN_STARTED → STATE_SNAPSHOT → TEXT_MESSAGE_START → 
TEXT_MESSAGE_CONTENT → TEXT_MESSAGE_END → RUN_FINISHED
```

### AG-UI Event Flow (Error)
```
RUN_STARTED → STATE_SNAPSHOT → TEXT_MESSAGE_START → 
TEXT_MESSAGE_CONTENT → [ERROR] → TEXT_MESSAGE_END → RUN_ERROR
(No RUN_FINISHED allowed after RUN_ERROR)
```

### The Protocol Rules
- State machine: STARTED → RUNNING → (FINISHED | ERROR)
- ERROR is a terminal state
- Once in ERROR state, no more events accepted
- This ensures consistent error handling across the system

## Related Files

- `backend/app/ag_ui/adapter.py` - Event streaming logic
- `frontend/app/api/copilotkit/route.ts` - API route handler
- `backend/app/graphs/storybook_graph.py` - LangGraph execution
- `backend/app/agents/` - Agent implementations that might error

## Prevention

To avoid errors in the first place:

1. **Add retries** in LangGraph tools (especially API calls)
2. **Add timeouts** to prevent hanging operations
3. **Validate inputs** before passing to agents
4. **Add circuit breakers** for external services
5. **Log detailed errors** to help debug root causes

## Monitoring

Watch for these log patterns:

✅ Good (expected):
```
[AG-UI Stream] Error: <actual error>
[COPILOTKIT] Stream ended with error state (expected behavior)
```

❌ Bad (needs investigation):
```
[AG-UI Stream] Failed to send RUN_ERROR: <error>
[COPILOTKIT] Unexpected agent error
```
