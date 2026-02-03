import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";
import { config } from "@/lib/config";

// Service adapter for CopilotKit (required parameter)
const serviceAdapter = new ExperimentalEmptyAdapter();

// Create agent - connects to unified backend server
const storybookAgent = new HttpAgent({
  url: config.api.storybookUrl,
});

const runtime = new CopilotRuntime({
  agents: {
    storybookAgent,
  },
});

export const POST = async (req: NextRequest) => {
  console.log("[COPILOTKIT] POST request received");
  
  // Log request body for debugging
  try {
    const body = await req.clone().json();
    console.log("[COPILOTKIT] Request body:", JSON.stringify(body, null, 2));
  } catch (e) {
    console.log("[COPILOTKIT] Could not parse request body:", e);
  }
  
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
  
  try {
    console.log("[COPILOTKIT] Calling handleRequest...");
    const response = await handleRequest(req);
    console.log("[COPILOTKIT] Got response, status:", response.status);
    
    // If it's an SSE stream, log the events
    if (response.headers.get("content-type")?.includes("text/event-stream")) {
      console.log("[COPILOTKIT] Response is SSE stream");
      
      // Clone the response to read it
      const clonedResponse = response.clone();
      const reader = clonedResponse.body?.getReader();
      const decoder = new TextDecoder();
      
      if (reader) {
        (async () => {
          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              
              const chunk = decoder.decode(value, { stream: true });
              const lines = chunk.split('\n');
              
              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const data = JSON.parse(line.substring(6));
                    console.log("[COPILOTKIT] SSE Event:", data);
                    
                    if (data.outcome === 'interrupt') {
                      console.log("[COPILOTKIT] ⚠️ INTERRUPT EVENT DETECTED!");
                      console.log("[COPILOTKIT] Interrupt data:", data.interrupt);
                    }
                  } catch {
                    // Not JSON, skip
                  }
                }
              }
            }
          } catch (e) {
            console.log("[COPILOTKIT] Stream reading ended:", e);
          }
        })();
      }
    }
    
    return response;
  } catch (error) {
    // Handle AG-UI protocol errors gracefully
    console.error("[COPILOTKIT] Agent execution error:", error);
    
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    // Suppress "run already errored" errors - these are expected when RUN_ERROR is sent
    // The frontend will receive the RUN_ERROR event and handle it appropriately
    if (errorMessage.includes("run has already errored") || 
        errorMessage.includes("Cannot send event type")) {
      console.log("[COPILOTKIT] Stream ended with error state (expected behavior)");
      // Return 200 OK since this is expected behavior when an error occurs
      return new Response(null, { status: 200 });
    }
    
    // For unexpected errors, log and return 500
    return new Response(
      JSON.stringify({ error: "Unexpected agent error", details: errorMessage }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};
