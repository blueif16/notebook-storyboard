"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { useState, useEffect, ReactNode } from "react";

interface CopilotProviderProps {
  children: ReactNode;
}

export function CopilotProvider({ children }: CopilotProviderProps) {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    
    // Generate or retrieve threadId on client side
    let id = sessionStorage.getItem('storybook-thread-id');
    if (!id) {
      id = crypto.randomUUID();
      sessionStorage.setItem('storybook-thread-id', id);
      console.log("[CopilotProvider] Generated new threadId:", id);
    } else {
      console.log("[CopilotProvider] Retrieved existing threadId:", id);
    }
    setThreadId(id);
  }, []);

  // Show loading state while initializing on client
  if (!isClient || !threadId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse text-gray-500">Loading...</div>
      </div>
    );
  }

  console.log("[CopilotProvider] Rendering CopilotKit with threadId:", threadId);

  return (
    <CopilotKit 
      runtimeUrl="/api/copilotkit" 
      agent="storybookAgent"
      threadId={threadId}
    >
      {children}
    </CopilotKit>
  );
}
