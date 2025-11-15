# Synapse Search Examples

Here are example search queries to test your semantic search functionality:

## Campaign & Performance Queries

1. **"What were our Q3 campaign results?"**
   - Should find: Q3_2024_Campaign_Report, Q3_Campaign_Report.txt
   - Tests: Temporal queries, campaign performance

2. **"Show me campaign performance metrics"**
   - Should find: Campaign reports, performance summaries
   - Tests: General performance queries

3. **"What was the ROI for our recent campaigns?"**
   - Should find: Reports mentioning ROI, campaign results
   - Tests: Financial metrics search

4. **"Tell me about our email campaign results"**
   - Should find: Email_Campaign_Q4.docx, campaign reports
   - Tests: Specific channel queries

## Project-Specific Queries

5. **"What's the status of Project X?"**
   - Should find: Project_X_Brief.docx, documents mentioning Project X
   - Tests: Project filtering

6. **"Show me everything about Project Y"**
   - Should find: All Project Y related documents
   - Tests: Project-specific search

7. **"What are the details for Project X launch?"**
   - Should find: Project briefs, launch plans
   - Tests: Specific project details

## Strategy & Planning Queries

8. **"What's our marketing strategy for 2024?"**
   - Should find: Marketing_Strategy_2024.pdf, strategy documents
   - Tests: Strategy document retrieval

9. **"Show me our content marketing plan"**
   - Should find: Content_Plan_2024.md, content calendars
   - Tests: Content planning queries

10. **"What's our social media strategy?"**
    - Should find: Social_Media_Content_Plan.docx, social media docs
    - Tests: Channel-specific strategy

## Content & Calendar Queries

11. **"What content is planned for Q4?"**
    - Should find: Content calendars, Q4 plans
    - Tests: Calendar and planning queries

12. **"Show me the blog post schedule"**
    - Should find: Content calendars, blog drafts
    - Tests: Content scheduling

13. **"What topics are we covering this month?"**
    - Should find: Content plans, calendars
    - Tests: Topic-based queries

## Research & Analysis Queries

14. **"What market research have we done?"**
    - Should find: Market_Research_Summary.docx, research documents
    - Tests: Research document retrieval

15. **"Show me customer insights"**
    - Should find: Research summaries, analysis documents
    - Tests: Insight queries

16. **"What are the key findings from our research?"**
    - Should find: Research summaries, reports
    - Tests: Analysis queries

## Team & Internal Queries

17. **"What was discussed in the team meeting?"**
    - Should find: Team_Meeting_Notes.txt, meeting notes
    - Tests: Internal document search

18. **"Show me internal briefs"**
    - Should find: Project briefs, internal documents
    - Tests: Document type filtering

## Complex/Multi-Part Queries

19. **"What were the Q3 results for Project X campaign?"**
    - Should find: Q3 reports mentioning Project X
    - Tests: Multi-criteria search

20. **"How did our email campaigns perform compared to social media?"**
    - Should find: Campaign reports, performance comparisons
    - Tests: Comparative queries

21. **"What's the plan for launching Project X in Q4?"**
    - Should find: Launch plans, Q4 calendars, Project X docs
    - Tests: Multi-faceted queries

## Edge Cases & Testing

22. **"campaign"** (single word)
    - Tests: Simple keyword matching

23. **"What were the results?"** (vague query)
    - Tests: Context understanding

24. **"ROI conversion engagement metrics"** (keyword list)
    - Tests: Multiple keyword matching

25. **"Tell me about the thing we did last quarter"** (natural language)
    - Tests: Natural language understanding

## Using Filters (via API)

You can also test with topic and project filters:

```json
{
  "query": "campaign results",
  "topic": "Report",
  "match_count": 5
}
```

```json
{
  "query": "strategy",
  "project": "Project X",
  "match_threshold": 0.6
}
```

## Testing Tips

1. **Start with specific queries** - Test with exact document names/topics first
2. **Try natural language** - The semantic search should understand intent
3. **Test synonyms** - "results" vs "performance" vs "metrics"
4. **Test temporal queries** - "Q3", "2024", "last quarter"
5. **Test project names** - "Project X", "Project Y"
6. **Test vague queries** - See how well it handles ambiguity
7. **Test filters** - Use topic and project filters to narrow results

## Expected Behavior

- **High similarity scores (>80%)** for exact matches
- **Medium scores (50-80%)** for related content
- **Lower scores (<50%)** for less relevant content (adjust threshold as needed)
- **Multiple chunks** from the same document for longer documents
- **Source filenames** should be clearly displayed

## API Testing

Test via curl or Postman:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What were our Q3 campaign results?", "match_count": 5}'
```

Or visit the interactive docs at: `http://localhost:8000/docs`

