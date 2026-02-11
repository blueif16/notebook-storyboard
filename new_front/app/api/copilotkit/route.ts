import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8005";

const serviceAdapter = new ExperimentalEmptyAdapter();

const runtime = new CopilotRuntime({
  agents: {
    storybook_agent: new HttpAgent({
      url: `${BACKEND_URL}/storybook`,
    }),
  },
});

function logRequest(label: string, data: any) {
  console.log(`%c[CopilotKit API] ${label}`, 'color: #10b981; font-weight: bold', {
    timestamp: new Date().toISOString(),
    ...data
  })
}

export async function POST(req: NextRequest) {
  logRequest('收到请求', {
    url: req.url,
    method: req.method,
    contentType: req.headers.get('content-type')
  })

  try {
    const body = await req.clone().json()
    logRequest('请求体', {
      messages: body.messages?.map((m: any) => ({
        role: m.role,
        content: typeof m.content === 'string' ? m.content.substring(0, 100) : m.content
      })),
      threadId: body.threadId,
      agentName: body.agentName,
      fullBody: body
    })
  } catch (e) {
    logRequest('无法解析请求体', { error: e })
  }

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  logRequest('转发到后端', {
    backendUrl: `${BACKEND_URL}/storybook`
  })

  const response = await handleRequest(req);

  logRequest('收到后端响应', {
    status: response.status,
    statusText: response.statusText,
    contentType: response.headers.get('content-type')
  })

  return response;
}
