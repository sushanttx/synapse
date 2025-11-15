# Frontend Implementation Guide

This guide outlines what the frontend needs to implement for the Synapse Marketing Search application.

## Required Features

### 1. **Search Interface** (Main Feature)
- Large, centered search input
- Search button or auto-search on enter
- Display loading state while searching
- Show search results with:
  - File name (clickable/link)
  - Matching text chunks
  - Similarity score
  - Topic and project tags

### 2. **File Upload** (New Feature)
- File upload button/area
- Drag & drop support (optional but nice)
- Show upload progress
- Display success/error messages
- Optionally allow manual topic/project selection

### 3. **Results Display**
- Group results by file (use the `files` array from API)
- Show individual chunks (use the `results` array)
- Display similarity scores
- Show source file names prominently
- Make file names clickable (if you want to link to files)

### 4. **Filters** (Optional Enhancement)
- Dropdown for topics (from `/topics` endpoint)
- Dropdown for projects (from `/projects` endpoint)
- Apply filters to search queries

### 5. **Stats/Info** (Optional)
- Show total documents indexed (from `/stats` endpoint)
- Display available topics and projects

## API Endpoints to Use

### Search
```javascript
POST http://localhost:8000/search
Body: {
  "query": "What were our Q3 campaign results?",
  "match_threshold": 0.5,
  "match_count": 10,
  "topic": null,  // Optional
  "project": null  // Optional
}

Response: {
  "results": [...],  // Individual chunks
  "files": [...],     // Grouped by file
  "query": "...",
  "total_results": 5,
  "total_files": 2
}
```

### Upload
```javascript
POST http://localhost:8000/upload
FormData: {
  file: File,
  topic: "Report",  // Optional
  project: "Project X"  // Optional
}

Response: {
  "success": true,
  "filename": "document.pdf",
  "chunks_created": 5,
  "topic": "Report",
  "project": "Project X",
  "message": "..."
}
```

### Stats
```javascript
GET http://localhost:8000/stats

Response: {
  "total_chunks": 50,
  "total_files": 13,
  "files": ["file1.pdf", "file2.docx", ...],
  "topics": ["Report", "Strategy", ...],
  "projects": ["Project X", "Project Y", ...]
}
```

### Topics
```javascript
GET http://localhost:8000/topics

Response: {
  "topics": ["Strategy", "Content", "Report", "Brief"]
}
```

### Projects
```javascript
GET http://localhost:8000/projects

Response: {
  "projects": ["Project X", "Project Y", "Internal"]
}
```

## UI Components Needed

### 1. Search Bar Component
```jsx
// Features:
- Large input field
- Search button
- Loading spinner
- Clear button
```

### 2. Results Component
```jsx
// Features:
- Display files grouped together
- Show chunks within each file
- Similarity score badges
- Topic/project tags
- Empty state when no results
```

### 3. File Upload Component
```jsx
// Features:
- File input or drag & drop zone
- Progress indicator
- Success/error messages
- Optional topic/project selectors
```

### 4. Filter Component (Optional)
```jsx
// Features:
- Topic dropdown
- Project dropdown
- Clear filters button
```

## Example React Component Structure

```jsx
// App.jsx structure
function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);

  const handleSearch = async () => {
    setLoading(true);
    const response = await fetch('http://localhost:8000/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        topic: selectedTopic,
        project: selectedProject
      })
    });
    const data = await response.json();
    setResults(data);
    setLoading(false);
  };

  const handleUpload = async (file, topic, project) => {
    const formData = new FormData();
    formData.append('file', file);
    if (topic) formData.append('topic', topic);
    if (project) formData.append('project', project);

    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData
    });
    return await response.json();
  };

  return (
    <div>
      <Header />
      <SearchBar 
        query={query}
        onQueryChange={setQuery}
        onSearch={handleSearch}
        loading={loading}
      />
      <Filters 
        topic={selectedTopic}
        project={selectedProject}
        onTopicChange={setSelectedTopic}
        onProjectChange={setSelectedProject}
      />
      <FileUpload onUpload={handleUpload} />
      <Results results={results} />
    </div>
  );
}
```

## Design Recommendations

### Layout
- **Header**: "Synapse: Marketing Search" with logo
- **Search Section**: Centered, prominent search bar
- **Upload Section**: Top right or below search bar
- **Results Section**: Below search, full width
- **Filters**: Sidebar or above results

### Styling (Tailwind CSS)
- Clean, modern design
- Use cards for results
- Color code similarity scores (green = high, yellow = medium, red = low)
- Show file names prominently
- Use badges for topics/projects

### User Experience
- Show loading states
- Display helpful error messages
- Auto-focus search input
- Keyboard shortcuts (Enter to search)
- Responsive design (mobile-friendly)

## Example Result Card Design

```jsx
// File Result Card
<div className="border rounded-lg p-4 mb-4 shadow-sm">
  <div className="flex justify-between items-start mb-2">
    <h3 className="text-lg font-semibold text-blue-600">
      {file.file_name}
    </h3>
    <span className="badge bg-green-100 text-green-800">
      {file.best_similarity}% match
    </span>
  </div>
  
  {file.topic && (
    <span className="badge bg-purple-100 text-purple-800 mr-2">
      {file.topic}
    </span>
  )}
  {file.project && (
    <span className="badge bg-blue-100 text-blue-800">
      {file.project}
    </span>
  )}
  
  <div className="mt-3">
    {file.chunks.map((chunk, idx) => (
      <div key={idx} className="mb-2 p-2 bg-gray-50 rounded">
        <p className="text-sm">{chunk.content}</p>
        <span className="text-xs text-gray-500">
          Similarity: {chunk.similarity}%
        </span>
      </div>
    ))}
  </div>
</div>
```

## Implementation Priority

### Phase 1 (MVP - Required)
1. ✅ Search bar with results display
2. ✅ File upload functionality
3. ✅ Basic result cards showing files and chunks

### Phase 2 (Enhancements)
4. Filters (topic/project dropdowns)
5. Stats display
6. Better loading states
7. Error handling

### Phase 3 (Polish)
8. Drag & drop file upload
9. Keyboard shortcuts
10. Advanced search options
11. Export results

## Testing Checklist

- [ ] Search returns results
- [ ] Upload works for PDF, DOCX, TXT, MD
- [ ] Uploaded files appear in search immediately
- [ ] Filters work correctly
- [ ] Loading states display properly
- [ ] Error messages are user-friendly
- [ ] Mobile responsive
- [ ] Empty states handled gracefully

## API Base URL

For development: `http://localhost:8000`

For production: Update to your deployed backend URL (e.g., Render, Railway, etc.)

## CORS

The backend already has CORS enabled for all origins (`*`). For production, update `main.py` to allow only your frontend domain.

