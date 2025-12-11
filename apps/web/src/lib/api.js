/**
 * API Client for Oreza Backend
 * Handles all communication with FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };
  
  const response = await fetch(url, { ...defaultOptions, ...options });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}

/**
 * Health check
 */
export async function checkHealth() {
  return apiFetch('/healthz');
}

/**
 * Chat completion
 * @param {Array} messages - Chat messages in OpenAI format
 * @param {object} options - Additional options (model, stream, etc.)
 */
export async function chatComplete(messages, options = {}) {
  return apiFetch('/chat/complete', {
    method: 'POST',
    body: JSON.stringify({
      messages,
      ...options,
    }),
  });
}

/**
 * Generate image via ComfyUI
 * @param {object} params - Generation parameters
 */
export async function generateImage(params) {
  const { prompt, workflow_id, seed, highres, mj_mode, ...rest } = params;
  
  return apiFetch('/image/generate', {
    method: 'POST',
    body: JSON.stringify({
      workflow_id,
      prompt: {
        text: prompt,
        ...rest,
      },
      seed,
      highres,
      mj_mode,
    }),
  });
}

/**
 * Check image generation status
 * @param {string} jobId - Job ID from generateImage
 */
export async function getImageStatus(jobId) {
  return apiFetch(`/image/status/${jobId}`);
}

/**
 * Web search
 * @param {string} query - Search query
 * @param {number} topK - Number of results
 */
export async function webSearch(query, topK = 5) {
  return apiFetch('/search', {
    method: 'POST',
    body: JSON.stringify({
      q: query,
      top_k: topK,
    }),
  });
}

/**
 * Upload camera frame
 * @param {Blob} imageBlob - Image blob from canvas
 */
export async function uploadFrame(imageBlob) {
  const formData = new FormData();
  formData.append('file', imageBlob, 'frame.jpg');
  
  return apiFetch('/media/frame', {
    method: 'POST',
    headers: {}, // Let browser set Content-Type for FormData
    body: formData,
  });
}
