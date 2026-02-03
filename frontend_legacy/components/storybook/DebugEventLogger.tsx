"use client";

import { useEffect } from "react";
import { useCoAgent } from "@copilotkit/react-core";
import { StorybookState } from "@/types/storybook-state";

/**
 * Debug component to log all agent events and state changes
 */
export function DebugEventLogger() {
  const { state } = useCoAgent<StorybookState>({
    name: "storybookAgent",
  });

  useEffect(() => {
    console.log("[DEBUG LOGGER] State changed:", state);
  }, [state]);

  useEffect(() => {
    console.log("[DEBUG LOGGER] Component mounted - listening for events");
    
    return () => {
      console.log("[DEBUG LOGGER] Component unmounting");
    };
  }, []);

  return null; // This component doesn't render anything
}
