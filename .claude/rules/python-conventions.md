# Python Conventions

## Style
- snake_case for files, functions, and variables
- Standalone scripts with `if __name__ == "__main__":` guards
- Use pathlib over os.path for all file operations
- Use argparse for CLI tools
- Type hints on all function signatures

## Project Structure
- `tools/` is organized by function: rag_tools/, youtube_tools/
- Each subdirectory contains standalone scripts (not a monolithic package)
- Config files stored in home directory (~/.knowledge_base_ai/)
- Environment variables for credentials -- never hardcode API keys
- `.env` files for local development, never committed to git

## Dependencies
- Python 3.10+
- RAG tools: chromadb, sentence-transformers, langchain
- YouTube tools: yt-dlp (system), ffmpeg (system)
- Install per-project, not globally

## Testing
- test_*.py naming pattern
- Tests live alongside source files
