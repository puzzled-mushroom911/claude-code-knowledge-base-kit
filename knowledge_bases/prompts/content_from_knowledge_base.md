# Content Generation from Knowledge Base

## Purpose
Transform knowledge base content (video transcripts, documents, books) into polished content pieces that capture your voice and expertise.

## Content Types

### Blog Post from Video Transcript
1. **Voice Analysis**: Read the transcript and identify speaking style, recurring phrases, argument structure, level of technical detail
2. **Content Extraction**: Main thesis, 3-5 key subtopics, data points, stories, questions addressed, CTAs
3. **Research Enhancement**: Web search for 3-5 supporting sources and current data
4. **SEO Structure**: Title (50-60 chars), meta description (150-160 chars), H2/H3 hierarchy, FAQ section
5. **Output**: 1,500-2,500 word markdown with YAML frontmatter

### Email Sequence (Nurture)
- **Framework**: Russell Brunson's Daily Seinfeld Method
- **Structure**: Subject line (curiosity-driven) → Opening (mid-story) → Micro-story (100-150 words) → Pivot → Soft CTA → Sign-off → P.S.
- **Rules**: Max 200 words, plain text, one topic per email, real stories only
- **Welcome sequence**: 5 emails over 10 days (origin story → common mistake → spotlight → pattern → direct value)

### Social Media Clips
- Extract 3-5 standalone moments from transcripts
- Each with: timestamp, quote, hook text, platform recommendation
- Prioritize: surprising data, honest takes, relatable stories

### Lead Magnet / Guide
- Query knowledge base across multiple topics
- Structure as a comprehensive guide
- Use `[DATA_NEEDED]` placeholders for statistics not in KB
- Include your perspective and expertise woven throughout

## Process

### 1. Query Knowledge Base
```
python3 tools/rag_tools/rag_query.py "[topic]" --db-path knowledge_bases/vectors/[your_db]
```

### 2. Cross-Reference
```
python3 tools/rag_tools/rag_query_multi.py "[topic]" --all
```

### 3. Generate Content
Use the retrieved context to generate content that:
- Maintains your voice (match transcript speaking style)
- Includes specific details from your experience
- Cites data accurately
- Adds value beyond what's in the transcript alone

## Rules
- Never fabricate data. If it's not in the KB, mark as [DATA_NEEDED]
- Maintain the speaker's natural voice — don't over-formalize
- Include specific names, numbers, examples (not generic language)
- Every piece should have a clear next step or CTA
