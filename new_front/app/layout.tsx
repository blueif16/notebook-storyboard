import type { Metadata } from 'next'
import './globals.css'
import { CopilotKit } from '@copilotkit/react-core'

export const metadata: Metadata = {
  title: 'Storyboard Canvas',
  description: 'AI-powered storyboard creation with infinite canvas',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>
        <CopilotKit
          runtimeUrl="/api/copilotkit"
          agent="storybook_agent"
          publicApiKey={process.env.NEXT_PUBLIC_COPILOTKIT_LICENSE_KEY}
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  )
}
