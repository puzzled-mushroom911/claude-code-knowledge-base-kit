# Knowledge Base Kit

## Overview
This is a Claude Code knowledge base framework. It provides tools to build, query, and use local RAG (Retrieval-Augmented Generation) knowledge bases from YouTube channels, books, and documents. Works for any industry.

## Directory Structure

```
.claude/
  CLAUDE.md              # This file
  rules/
    python-conventions.md # Python coding standards
  agents/
    knowledge-base-builder.md  # Guided KB setup agent
  memory/
    MEMORY.md            # Auto-loaded memory index
```

## Tool Reference

### Knowledge Base Tools (RAG)
- `create_knowledge_base.py` -- Index documents into a searchable vector database
- `rag_query.py` -- Search a single knowledge base
- `rag_query_multi.py` -- Search across multiple knowledge bases
- `rag_system_manager.py` -- Registry for all knowledge bases (list, register, path, summary)

### YouTube Tools
- `fetch_videos.py` -- Download transcripts and metadata from YouTube channels
- `ingest_to_rag.py` -- Embed transcripts into ChromaDB for search
- `analyze_channels.py` -- Topic analysis, top videos, content gaps, recommendations

### MCP Server Tools (when connected)
- `rag_query` -- Query a knowledge base
- `rag_query_multi` -- Query multiple databases
- `rag_list_databases` -- List all registered databases
- `rag_create_knowledge_base` -- Create a new KB from a document directory
- `youtube_fetch_videos` -- Download channel transcripts
- `youtube_ingest` -- Ingest transcripts to RAG
- `youtube_analyze` -- Analyze channel content
- `youtube_strategy` -- Get strategy advice from curated KB

### Media Tools
- `yt-dlp` -- YouTube transcript and audio extraction
- `ffmpeg` -- Audio/video processing

## Conventions
- Python scripts: standalone with `if __name__ == "__main__":` guards
- Use pathlib over os.path
- Type hints on function signatures
- snake_case for files, functions, variables
- ChromaDB for vector storage (local, no cloud dependencies)
- sentence-transformers/all-MiniLM-L6-v2 for embeddings (runs locally)

## Scope Discipline
- When asked to do a simple task, do EXACTLY that -- do not over-engineer
- When asked for plain text output, deliver plain text FIRST
- Ask before expanding scope beyond what was explicitly requested
