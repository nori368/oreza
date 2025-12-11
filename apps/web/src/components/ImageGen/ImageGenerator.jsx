/**
 * Image Generator Component
 * Handles image generation with Midnight Journey mode support
 */

import { useState } from 'react';
import { Wand2, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { Textarea } from '@/components/ui/textarea.jsx';
import { Label } from '@/components/ui/label.jsx';
import { Switch } from '@/components/ui/switch.jsx';
import { useImageStore, useSettingsStore } from '@/lib/state.js';
import { generateImage } from '@/lib/api.js';
import { getThemePromptModifiers } from '@/lib/themes.js';

export function ImageGenerator() {
  const [prompt, setPrompt] = useState('');
  const { isGenerating, addImage, setGenerating } = useImageStore();
  const { theme, mjMode, setMjMode } = useSettingsStore();

  const handleGenerate = async () => {
    if (!prompt.trim() || isGenerating) return;

    setGenerating(true);

    try {
      // Apply theme modifiers if Midnight Journey mode is active
      const effectiveTheme = mjMode ? 'midnight' : theme;
      const { prompt: modifiedPrompt, negativePrompt } = getThemePromptModifiers(
        effectiveTheme,
        prompt
      );

      console.log('Generating with prompt:', modifiedPrompt);

      const response = await generateImage({
        prompt: modifiedPrompt,
        negative_prompt: negativePrompt,
        mj_mode: mjMode,
        highres: true,
      });

      addImage({
        url: response.images[0].url || response.images[0].data,
        prompt: prompt,
        modifiedPrompt: modifiedPrompt,
        jobId: response.job_id,
      });

      // Clear prompt after successful generation
      setPrompt('');
    } catch (error) {
      console.error('Image generation error:', error);
      alert(`画像生成エラー: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="container mx-auto max-w-2xl px-4 py-6 space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">画像生成</h2>
        <p className="text-muted-foreground">
          プロンプトを入力して、AIが画像を生成します
        </p>
      </div>

      {/* Midnight Journey Mode Toggle */}
      <div className="flex items-center justify-between p-4 border rounded-lg">
        <div className="space-y-0.5">
          <Label htmlFor="mj-mode" className="text-base font-medium">
            Midnight Journey モード
          </Label>
          <p className="text-sm text-muted-foreground">
            シネマティックな暗部表現とネオンアクセント
          </p>
        </div>
        <Switch
          id="mj-mode"
          checked={mjMode}
          onCheckedChange={setMjMode}
        />
      </div>

      {/* Prompt Input */}
      <div className="space-y-2">
        <Label htmlFor="prompt">プロンプト</Label>
        <Textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例: 雨の中の少女、傘を持って..."
          className="min-h-[120px]"
          disabled={isGenerating}
        />
      </div>

      {/* Generate Button with proper spacing */}
      <Button
        onClick={handleGenerate}
        disabled={!prompt.trim() || isGenerating}
        className="w-full h-12 text-base font-medium my-4"
        size="lg"
      >
        {isGenerating ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            生成中...
          </>
        ) : (
          <>
            <Wand2 className="mr-2 h-5 w-5" />
            画像を生成
          </>
        )}
      </Button>

      {/* Info text */}
      {mjMode && (
        <div className="text-sm text-muted-foreground p-3 bg-muted/50 rounded-lg">
          <strong>Midnight Journeyモード有効:</strong> プロンプトに自動的にシネマティックな
          ライティング、ネオングロー、ムーディーな雰囲気が追加されます。
        </div>
      )}
    </div>
  );
}
