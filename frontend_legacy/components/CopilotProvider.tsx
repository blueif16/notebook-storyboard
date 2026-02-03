"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { useState, useEffect, ReactNode } from "react";

interface CopilotProviderProps {
  children: ReactNode;
}

export function CopilotProvider({ children }: CopilotProviderProps) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    console.log("[CopilotProvider] Initialized on client");
  }, []);

  // Show loading state while initializing on client
  if (!isClient) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse text-gray-500">Loading...</div>
      </div>
    );
  }

  console.log("[CopilotProvider] Rendering CopilotKit");

  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="storybookAgent"
      publicApiKey={process.env.NEXT_PUBLIC_COPILOTKIT_LICENSE_KEY}
    >
      {children}
    </CopilotKit>
  );
}
