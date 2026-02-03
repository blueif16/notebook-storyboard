import { Page } from "@/types/storybook-state";
import { Loader2 } from "lucide-react";

interface PagesReviewContentProps {
  pages: Page[];
}

export function PagesReviewContent({ pages }: PagesReviewContentProps) {
  return (
    <div className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        已生成 {pages.length} 页
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {pages.map((page, i) => (
          <div key={i} className="border rounded-lg p-3 bg-white">
            {/* Page Image */}
            {page.image_url ? (
              <img
                src={page.image_url}
                alt={`第 ${page.page_number} 页`}
                className="w-full aspect-video object-cover rounded-lg mb-2"
              />
            ) : (
              <div className="w-full aspect-video bg-gray-100 rounded-lg mb-2 flex items-center justify-center">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
              </div>
            )}

            {/* Page Info */}
            <div className="text-sm font-semibold mb-1">
              第 {page.page_number} 页
            </div>
            {page.plot && (
              <p className="text-xs text-gray-600 line-clamp-2">
                {page.plot}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
