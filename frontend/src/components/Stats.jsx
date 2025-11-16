import { useState, useEffect } from 'react'
import { getStats } from '../api'

function Stats() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getStats()
      setStats(data)
    } catch (err) {
      setError(err.message || 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">
          Database Statistics
        </h2>
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">
          Database Statistics
        </h2>
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    )
  }

  if (!stats) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-slate-800">
          Database Statistics
        </h2>
        <button
          onClick={loadStats}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-slate-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-slate-800">
            {stats.total_files || 0}
          </div>
          <div className="text-sm text-slate-600 mt-1">Total Files</div>
        </div>
        <div className="bg-slate-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-slate-800">
            {stats.total_chunks || 0}
          </div>
          <div className="text-sm text-slate-600 mt-1">Total Chunks</div>
        </div>
      </div>

      {stats.topics && stats.topics.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-slate-700 mb-2">Topics</h3>
          <div className="flex flex-wrap gap-2">
            {stats.topics.map((topic) => (
              <span
                key={topic}
                className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {stats.projects && stats.projects.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-slate-700 mb-2">Projects</h3>
          <div className="flex flex-wrap gap-2">
            {stats.projects.map((project) => (
              <span
                key={project}
                className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full"
              >
                {project}
              </span>
            ))}
          </div>
        </div>
      )}

      {stats.files && stats.files.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Indexed Files ({stats.files.length})
          </h3>
          <div className="max-h-40 overflow-y-auto bg-slate-50 rounded-lg p-3">
            <ul className="space-y-1">
              {stats.files.slice(0, 10).map((file, index) => (
                <li key={index} className="text-sm text-slate-600 flex items-center gap-2">
                  <span className="text-slate-400">•</span>
                  {file}
                </li>
              ))}
              {stats.files.length > 10 && (
                <li className="text-sm text-slate-500 italic">
                  ... and {stats.files.length - 10} more
                </li>
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default Stats


