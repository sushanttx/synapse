import { useState, useEffect } from 'react'
import { searchDocuments, getTopics, getProjects } from './api'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [totalResults, setTotalResults] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedTopic, setSelectedTopic] = useState('')
  const [selectedProject, setSelectedProject] = useState('')
  const [topics, setTopics] = useState([])
  const [projects, setProjects] = useState([])

  // Load topics and projects on mount
  useEffect(() => {
    const loadFilters = async () => {
      const [topicsData, projectsData] = await Promise.all([
        getTopics(),
        getProjects(),
      ])
      setTopics(topicsData)
      setProjects(projectsData)
    }
    loadFilters()
  }, [])

  const handleSearch = async (e) => {
    e.preventDefault()
    
    if (!query.trim()) {
      return
    }

    setLoading(true)
    setError(null)
    setResults([])
    setTotalResults(0)

    try {
      const response = await searchDocuments(query, {
        topic: selectedTopic || null,
        project: selectedProject || null,
      })
      setResults(response.results || [])
      setTotalResults(response.total_results || 0)
    } catch (err) {
      setError(err.message || 'Failed to search documents. Please try again.')
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatSimilarity = (similarity) => {
    // Similarity is already a percentage (0-100) from the backend
    return typeof similarity === 'number' ? Math.round(similarity) : similarity
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-slate-800">
            Synapse: Marketing Search
          </h1>
          <p className="text-slate-600 mt-1">
            Smart semantic search for your marketing documents
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="relative mb-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question... (e.g., 'What were our Q3 campaign results for Project X?')"
              className="w-full px-6 py-4 text-lg border-2 border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all shadow-sm"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          {/* Filters */}
          {(topics.length > 0 || projects.length > 0) && (
            <div className="flex flex-wrap gap-4">
              {topics.length > 0 && (
                <select
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white text-slate-700"
                  disabled={loading}
                >
                  <option value="">All Topics</option>
                  {topics.map((topic) => (
                    <option key={topic} value={topic}>
                      {topic}
                    </option>
                  ))}
                </select>
              )}
              {projects.length > 0 && (
                <select
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value)}
                  className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white text-slate-700"
                  disabled={loading}
                >
                  <option value="">All Projects</option>
                  {projects.map((project) => (
                    <option key={project} value={project}>
                      {project}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}
        </form>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-slate-600">Searching your documents...</p>
          </div>
        )}

        {/* Results */}
        {!loading && results.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-slate-800">
                Search Results ({totalResults})
              </h2>
            </div>
            {results.map((result, index) => (
              <div
                key={result.id || index}
                className="bg-white rounded-lg shadow-md border border-slate-200 p-6 hover:shadow-lg transition-shadow"
              >
                {/* Source File */}
                <div className="mb-3 flex items-start justify-between gap-4">
                  <a
                    href={`#${result.source}`}
                    className="text-lg font-semibold text-blue-600 hover:text-blue-800 hover:underline inline-flex items-center gap-2"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    {result.source}
                  </a>
                  {(result.topic || result.project) && (
                    <div className="flex gap-2 flex-shrink-0">
                      {result.topic && (
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                          {result.topic}
                        </span>
                      )}
                      {result.project && (
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                          {result.project}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Content Chunk */}
                <p className="text-slate-700 mb-4 leading-relaxed">
                  {result.content}
                </p>

                {/* Similarity Score */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                  <span className="text-sm text-slate-500">
                    Similarity: <span className="font-semibold text-slate-700">
                      {formatSimilarity(result.similarity)}%
                    </span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && results.length === 0 && query && !error && (
          <div className="text-center py-12">
            <p className="text-slate-600 text-lg">
              No results found. Try rephrasing your query.
            </p>
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && !query && !error && (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 mx-auto text-slate-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <p className="text-slate-600 text-lg">
              Enter a question above to search your marketing documents
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-6 border-t border-slate-200 bg-white">
        <div className="max-w-6xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>Synapse - Powered by Semantic Vector Search</p>
        </div>
      </footer>
    </div>
  )
}

export default App


