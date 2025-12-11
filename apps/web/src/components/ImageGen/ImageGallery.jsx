/**
 * Image Gallery Component
 * Displays generated images in a grid
 */

import { useImageStore } from '@/lib/state.js';
import { Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';

export function ImageGallery() {
  const { images } = useImageStore();

  if (images.length === 0) {
    return (
      <div className="text-center text-muted-foreground py-12">
        <p>まだ画像が生成されていません</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-6xl px-4 py-6">
      <h3 className="text-xl font-semibold mb-4">生成済み画像</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {images.map((image) => (
          <div
            key={image.id}
            className="group relative aspect-square overflow-hidden rounded-lg border bg-muted"
          >
            <img
              src={image.url}
              alt={image.prompt}
              className="w-full h-full object-cover"
            />
            
            {/* Overlay with actions */}
            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
              <Button
                size="icon"
                variant="secondary"
                onClick={() => {
                  const a = document.createElement('a');
                  a.href = image.url;
                  a.download = `oreza-${image.id}.png`;
                  a.click();
                }}
              >
                <Download className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Prompt overlay at bottom */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3">
              <p className="text-white text-sm line-clamp-2">{image.prompt}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
