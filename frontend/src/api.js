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
        match_threshold: options.match_threshold || 0.5,
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


