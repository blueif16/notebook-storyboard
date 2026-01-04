import { NextRequest, NextResponse } from "next/server";
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");

export async function POST(req: NextRequest) {
  try {
    const { sources } = await req.json();

    if (!sources || sources.length === 0) {
      return NextResponse.json(
        { error: "No sources provided" },
        { status: 400 }
      );
    }

    // Build context from sources
    const context = sources
      .filter((s: any) => s.status === "success")
      .map((s: any) => `Title: ${s.title}\nContent: ${s.text?.slice(0, 3000)}`)
      .join("\n\n");

    if (!context) {
      return NextResponse.json(
        { error: "No valid source content available" },
        { status: 400 }
      );
    }

    const model = genAI.getGenerativeModel({ model: "gemini-pro" });

    const prompt = `Based on the following content, create a visual storybook with 6-8 pages.
Each page should have descriptive text that tells a story or explains key concepts.

For each page, provide:
1. A detailed image description (for AI image generation)
2. Engaging narrative text (2-3 sentences)

Format your response as a JSON array of pages:
[
  {
    "imagePrompt": "detailed description for image generation",
    "text": "narrative text for this page"
  }
]

Content:
${context}

Create an engaging, visual story that captures the essence of this content.`;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    // Extract JSON from response
    let pages;
    try {
      const jsonMatch = text.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        pages = JSON.parse(jsonMatch[0]);
      } else {
        pages = JSON.parse(text);
      }
    } catch (e) {
      console.error("Failed to parse storybook JSON:", e);
      return NextResponse.json(
        { error: "Failed to parse storybook data" },
        { status: 500 }
      );
    }

    // Transform pages into storybook format
    const storyPages = pages.map((page: any, index: number) => ({
      leftImage: index % 2 === 0 ? `/api/placeholder?text=Page${index + 1}` : undefined,
      rightImage: index % 2 === 1 ? `/api/placeholder?text=Page${index + 1}` : undefined,
      leftText: index % 2 === 0 ? page.text : undefined,
      rightText: index % 2 === 1 ? page.text : undefined,
      imagePrompt: page.imagePrompt,
    }));

    return NextResponse.json({ pages: storyPages });
  } catch (error) {
    console.error("Storybook generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate storybook" },
      { status: 500 }
    );
  }
}

