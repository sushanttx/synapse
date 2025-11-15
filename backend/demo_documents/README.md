# Demo Documents Folder

This folder contains sample marketing documents that will be indexed by the Synapse ingestion pipeline.

## Supported File Types

- **PDF** (`.pdf`) - Reports, briefs, strategy documents
- **Word Documents** (`.docx`) - Drafts, proposals, content plans
- **Text Files** (`.txt`) - Notes, summaries, plain text documents
- **Markdown** (`.md`) - Documentation, blog drafts, formatted text

## Recommended Structure

For a good demo/test setup, include **5-15 documents** with a mix of:

### Minimum Setup (5-7 documents)
- 2-3 PDF reports (e.g., "Q3_Campaign_Report.pdf", "Marketing_Strategy_2024.pdf")
- 2-3 Word documents (e.g., "Content_Plan.docx", "Project_Brief.docx")
- 1-2 Markdown or text files (e.g., "Meeting_Notes.md", "Summary.txt")

### Recommended Setup (10-15 documents)
- **Reports** (4-5 PDFs):
  - Quarterly campaign reports
  - Performance analytics
  - Market research summaries
  
- **Strategy Documents** (3-4 DOCX):
  - Marketing strategy plans
  - Content calendars
  - Campaign briefs
  
- **Content** (2-3 files):
  - Blog post drafts (MD or TXT)
  - Social media content plans
  - Email campaign outlines

- **Internal Docs** (2-3 files):
  - Meeting notes
  - Project summaries
  - Team briefs

## Example File Names

```
demo_documents/
├── Q3_2024_Campaign_Report.pdf
├── Marketing_Strategy_2024.pdf
├── Social_Media_Content_Plan.docx
├── Project_X_Brief.docx
├── Blog_Post_Draft.md
├── Email_Campaign_Q4.md
├── Team_Meeting_Notes.txt
├── Market_Research_Summary.pdf
└── Content_Calendar_2024.docx
```

## Content Suggestions

To make the demo more effective, ensure documents contain:

1. **Diverse Topics**: Mix of strategy, content, reports, and briefs
2. **Project References**: Mention different projects (Project X, Project Y, Internal)
3. **Keywords**: Include marketing terms like "campaign", "ROI", "engagement", "conversion"
4. **Dates/Timeframes**: Q3, Q4, 2024, etc. for temporal search
5. **Real Content**: At least 2-3 pages of text per document for meaningful chunks

## File Size Guidelines

- **PDFs**: 1-10 pages each (enough for 3-10 chunks)
- **DOCX**: 500-3000 words each
- **TXT/MD**: 200-2000 words each

## Testing Different Scenarios

Include documents that test:

- **Semantic Search**: "What were our Q3 results?" → Should find Q3 report
- **Project Filtering**: Documents mentioning "Project X" vs "Project Y"
- **Topic Categorization**: Strategy docs, content docs, reports
- **Cross-Document References**: Multiple docs mentioning the same campaign

## Quick Start

1. Create this folder: `mkdir demo_documents`
2. Add 5-10 sample documents (PDF, DOCX, TXT, or MD)
3. Run `python ingest.py` to index them
4. Test searches like:
   - "What were our campaign results?"
   - "Tell me about Project X"
   - "Show me strategy documents"

## Note

The ingestion script will:
- Recursively search all subfolders
- Process all supported file types
- Skip files it can't read (with warnings)
- Create multiple chunks per document (based on size)

