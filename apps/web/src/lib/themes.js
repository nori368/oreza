/**
 * Theme configuration for Oreza AI
 * Supports multiple visual modes including Midnight Journey
 */

export const themes = {
  default: {
    id: 'default',
    name: 'Default',
    description: 'Standard Oreza theme',
    cssVars: {
      '--background': 'oklch(1 0 0)',
      '--foreground': 'oklch(0.145 0 0)',
      '--card': 'oklch(1 0 0)',
      '--card-foreground': 'oklch(0.145 0 0)',
      '--primary': 'oklch(0.205 0 0)',
      '--primary-foreground': 'oklch(0.985 0 0)',
      '--border': 'oklch(0.922 0 0)',
      '--muted': 'oklch(0.97 0 0)',
      '--muted-foreground': 'oklch(0.556 0 0)',
    }
  },
  
  midnight: {
    id: 'midnight',
    name: 'Midnight Journey',
    description: 'Cinematic dark theme with neon accents',
    cssVars: {
      '--background': 'oklch(0.08 0.01 240)', // #0b0f14 equivalent
      '--foreground': 'oklch(0.88 0.01 240)', // #dbe3ec equivalent
      '--card': 'oklch(0.12 0.01 240)',
      '--card-foreground': 'oklch(0.88 0.01 240)',
      '--primary': 'oklch(0.65 0.2 280)', // Neon purple-blue
      '--primary-foreground': 'oklch(0.95 0.01 240)',
      '--border': 'oklch(0.2 0.01 240)', // Subtle borders
      '--muted': 'oklch(0.15 0.01 240)',
      '--muted-foreground': 'oklch(0.6 0.01 240)',
      '--accent': 'oklch(0.5 0.25 320)', // Neon pink accent
      '--accent-foreground': 'oklch(0.95 0.01 240)',
    },
    imagePromptModifiers: {
      prefix: 'cinematic lighting, dramatic shadows, neon glow, moody atmosphere, midnight street, highly detailed, 8k, (masterpiece), reflective surfaces, intricate details,',
      suffix: ', film grain, cyberpunk aesthetic, night scene, atmospheric fog',
      negativePrompt: 'bright daylight, overexposed, washed out, flat lighting, amateur',
    }
  }
};

/**
 * Apply theme to document root
 * @param {string} themeId - Theme identifier ('default' or 'midnight')
 */
export function applyTheme(themeId) {
  const theme = themes[themeId] || themes.default;
  const root = document.documentElement;
  
  // Apply CSS variables
  Object.entries(theme.cssVars).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
  
  // Set data attribute for additional CSS targeting
  root.setAttribute('data-theme', themeId);
  
  // Store preference
  localStorage.setItem('oreza-theme', themeId);
  
  return theme;
}

/**
 * Get current theme from localStorage or default
 */
export function getCurrentTheme() {
  const stored = localStorage.getItem('oreza-theme');
  return themes[stored] || themes.default;
}

/**
 * Get image generation prompt modifiers for current theme
 * @param {string} themeId - Theme identifier
 * @param {string} userPrompt - User's original prompt
 * @returns {object} Modified prompts
 */
export function getThemePromptModifiers(themeId, userPrompt) {
  const theme = themes[themeId] || themes.default;
  
  if (!theme.imagePromptModifiers) {
    return {
      prompt: userPrompt,
      negativePrompt: ''
    };
  }
  
  const { prefix, suffix, negativePrompt } = theme.imagePromptModifiers;
  
  return {
    prompt: `${prefix} ${userPrompt}${suffix}`,
    negativePrompt: negativePrompt || ''
  };
}
