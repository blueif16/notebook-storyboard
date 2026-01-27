import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

// Service adapter for CopilotKit (required parameter)
const serviceAdapter = new ExperimentalEmptyAdapter();

// Create agent - connects to AG-UI backend
const storybookAgent = new HttpAgent({
  url: process.env.STORYBOOK_API_URL || "http://127.0.0.1:8001/storybook",
});

const runtime = new CopilotRuntime({
  agents: {
    storybookAgent,
  },
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
  
  try {
    return await handleRequest(req);
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
