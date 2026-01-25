import type { Metadata } from "next";
import { DM_Mono, Manrope } from "next/font/google";
import "./globals.css";
import "@copilotkit/react-ui/styles.css";
import { Toaster } from "@/components/ui/toaster";
import { CopilotKit } from "@copilotkit/react-core";

const manrope = Manrope({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-manrope",
});

const dmMono = DM_Mono({
  subsets: ["latin"],
  display: "swap",
  weight: ["300", "400", "500"],
  variable: "--font-dm-mono",
});

export const metadata: Metadata = {
  title: "HyperbookLM",
  description:
    "Powered by Hyperbrowser + GPT-5.2 - Research notebook with summaries, mindmaps, and media overviews.",
  icons: {
    icon: "/hyperbrowser_symbol-light.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${manrope.variable} ${dmMono.variable}`}>
        <CopilotKit runtimeUrl="/api/copilotkit" agent="storybookAgent">
          {children}
          <Toaster />
        </CopilotKit>
      </body>
    </html>
  );
}
