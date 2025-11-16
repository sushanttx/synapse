/**
 * API service for communicating with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Search for documents using semantic search
 * @param {string} query - The search query
 * @param {Object} options - Optional search parameters
 * @param {number} options.match_threshold - Minimum similarity threshold (0-1)
 * @param {number} options.match_count - Maximum number of results
 * @param {string} options.topic - Filter by topic
 * @param {string} options.project - Filter by project
 * @returns {Promise<Object>} Object with results array, query, and total_results
 */
export async function searchDocuments(query, options = {}) {
  if (!query || query.trim() === '') {
    return { results: [], query: '', total_results: 0 };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query.trim(),
        match_threshold: options.match_threshold || 0.1,
        match_count: options.match_count || 10,
        topic: options.topic || null,
        project: options.project || null,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Search failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Search error:', error);
    throw error;
  }
}

/**
 * Get all available topics from the database
 * @returns {Promise<Array>} Array of topic strings
 */
export async function getTopics() {
  try {
    const response = await fetch(`${API_BASE_URL}/topics`);
    if (!response.ok) {
      throw new Error(`Failed to fetch topics: ${response.statusText}`);
    }
    const data = await response.json();
    return data.topics || [];
  } catch (error) {
    console.error('Error fetching topics:', error);
    return [];
  }
}

/**
 * Get all available projects from the database
 * @returns {Promise<Array>} Array of project strings
 */
export async function getProjects() {
  try {
    const response = await fetch(`${API_BASE_URL}/projects`);
    if (!response.ok) {
      throw new Error(`Failed to fetch projects: ${response.statusText}`);
    }
    const data = await response.json();
    return data.projects || [];
  } catch (error) {
    console.error('Error fetching projects:', error);
    return [];
  }
}

/**
 * Upload a file to the system
 * @param {File} file - The file to upload
 * @param {string} topic - Optional topic for the document
 * @param {string} project - Optional project for the document
 * @param {Function} onProgress - Optional progress callback (progress: number)
 * @returns {Promise<Object>} Upload response with success status and details
 */
export async function uploadFile(file, topic = null, project = null, onProgress = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (topic) formData.append('topic', topic);
  if (project) formData.append('project', project);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    if (onProgress) {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          onProgress(percentComplete);
        }
      });
    }

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (e) {
          resolve({ success: true, message: 'File uploaded successfully' });
        }
      } else {
        try {
          const errorData = JSON.parse(xhr.responseText);
          reject(new Error(errorData.detail || `Upload failed: ${xhr.statusText}`));
        } catch (e) {
          reject(new Error(`Upload failed: ${xhr.statusText}`));
        }
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'));
    });

    xhr.addEventListener('abort', () => {
      reject(new Error('Upload cancelled'));
    });

    xhr.open('POST', `${API_BASE_URL}/upload`);
    xhr.send(formData);
  });
}

/**
 * Get statistics about the indexed documents
 * @returns {Promise<Object>} Stats object with total_chunks, total_files, files, topics, projects
 */
export async function getStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    throw error;
  }
}


