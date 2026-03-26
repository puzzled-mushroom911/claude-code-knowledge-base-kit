# Claude Code Knowledge Base Kit

Build a local, searchable knowledge base from your YouTube channel, books, PDFs, and documents -- then use it with Claude Code to generate content, answer questions, and run your business smarter. Works for any industry.

Everything runs on your computer. No data leaves your machine.

---

## What This Does

1. **Ingests your YouTube channel** -- downloads transcripts, chunks them, and stores searchable embeddings locally
2. **Indexes books and documents** -- PDFs, Word docs, markdown, and text files become a queryable knowledge base
3. **Lets Claude Code search it all** -- ask questions in plain English across all your knowledge bases
4. **Powers content generation** -- Claude uses your knowledge base to write in your voice with your expertise
5. **Tracks competitors** -- ingest competitor YouTube channels to find content gaps and opportunities

### Use Cases

| Use Case | How It Works |
|---|---|
| "What have I said about [topic]?" | Semantic search across your video transcripts |
| Content planning | Analyze competitor coverage, find gaps, plan differentiation |
| Blog posts from videos | Turn any video transcript into an SEO blog post in your voice |
| Email sequences | Generate nurture emails grounded in your actual expertise |
| Customer responses | Draft replies using your knowledge base for accurate, on-brand answers |
| Lead magnets | Turn your video content into guides, reports, or downloadable resources |
| Strategy research | Query marketing books (Hormozi, Brunson) for frameworks and tactics |

---

## Quick Start

### Step 1: Prerequisites

```bash
brew install python@3.12 node yt-dlp ffmpeg
```

- **Python 3.10+** -- powers the data processing
- **Node.js** -- connects Claude Code to your tools via MCP
- **yt-dlp** -- downloads YouTube transcripts (free)
- **ffmpeg** -- handles audio/video files

### Step 2: Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Then run `claude` to log in.

### Step 3: Clone This Repo

```bash
cd ~/
git clone <this-repo-url> knowledge-base-kit
cd knowledge-base-kit
```

### Step 4: Run Setup

```bash
bash scripts/setup.sh
```

This installs Python packages, builds the MCP server, and downloads the AI embedding model. Takes 2-5 minutes.

### Step 5: Configure Your Profile

Edit `config/profile.yaml` with your info:

```yaml
profile:
  name: "Your Name"
  business: "Your Business Name"
  website: "https://www.yourbusiness.com"
  youtube_handle: "@YourChannel"
  industry: "real estate"  # your industry
```

Edit `config/channels.yaml` with your YouTube channels:

```yaml
channels:
  - handle: "@YourChannel"
    name: "Your Channel"
    category: "own"

  # Add competitors or strategy channels:
  # - handle: "@CompetitorChannel"
  #   name: "Competitor Name"
  #   category: "competitor"
```

### Step 6: Ingest Your YouTube Channel

```bash
bash scripts/ingest-channel.sh @YourChannelHandle
```

This downloads your transcripts and makes them searchable. Takes a few minutes depending on how many videos you have.

### Step 7: Connect the MCP Server

Add the following to your `~/.mcp.json`:

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "node",
      "args": ["/path/to/knowledge-base-kit/mcp_server/dist/index.js"]
    }
  }
}
```

Replace `/path/to/` with the actual path where you cloned the repo.

### Step 8: Try It

```bash
claude
```

Then ask:
```
> Search my knowledge base for what I've said about [topic from your videos]
> What do my competitors cover about [topic]?
> Help me outline content about [topic] based on my existing videos
```

---

## Building Your Knowledge Base

### YouTube Channels

```bash
# Ingest a single channel
bash scripts/ingest-channel.sh @YourChannel

# Ingest with custom settings
bash scripts/ingest-channel.sh @YourChannel --days 90 --max 100

# Build everything from config/channels.yaml
bash scripts/build-knowledge-base.sh
```

### Documents (PDFs, Word, Markdown, Text)

Drop files into `knowledge_bases/documents/`, then:

```bash
python3 tools/rag_tools/create_knowledge_base.py knowledge_bases/documents/ \
    --db-dir knowledge_bases/vectors/my_documents
```

### Books (Pre-loaded)

The kit ships with 12 marketing and strategy books already in `knowledge_bases/books/`:

| Book / Framework | Author |
|---|---|
| $100M Offers | Alex Hormozi |
| $100M Leads | Alex Hormozi |
| Pricing Playbook | Alex Hormozi |
| Ad Framework | Alex Hormozi |
| New vs Old Framework | Alex Hormozi |
| "Why You Will Never" Framework | Alex Hormozi |
| DotCom Secrets | Russell Brunson |
| Traffic Secrets | Russell Brunson |
| Lead Magnet & Squeeze Page Strategy | Russell Brunson |
| Backyard Blueprint | Russell Brunson |

To index them:

```bash
python3 tools/rag_tools/create_knowledge_base.py knowledge_bases/books/ \
    --db-dir knowledge_bases/vectors/marketing_books
```

### Channel Junkies (Pre-built)

A pre-vectorized YouTube strategy database is included at `knowledge_bases/vectors/youtube_channel_junkies/`. It's ready to query immediately -- no ingestion needed.

---

## Querying Your Knowledge Base

### From the Command Line

```bash
# Search a single database
python3 tools/rag_tools/rag_query.py "best content strategy" \
    --db-path knowledge_bases/vectors/youtube_yourchannel

# Search multiple databases
python3 tools/rag_tools/rag_query_multi.py "lead generation tips" --all

# List all registered databases
python3 tools/rag_tools/rag_system_manager.py list

# Analyze your channel content
python3 tools/youtube_tools/analyze_channels.py topics --database youtube_yourchannel
python3 tools/youtube_tools/analyze_channels.py top --database youtube_yourchannel
python3 tools/youtube_tools/analyze_channels.py gaps --database youtube_yourchannel --compare-db youtube_competitor
```

### From Claude Code

With the MCP server connected, just ask naturally:

```
> Search my knowledge base for [topic]
> What have I covered about [topic] in my videos?
> Compare my content coverage with [competitor] on [topic]
> Find content gaps between my channel and competitors
```

---

## How It Works

1. **YouTube transcripts** are downloaded via yt-dlp (auto-generated captions)
2. Text is split into overlapping chunks (~500-1,000 characters)
3. Each chunk gets a vector embedding using a local AI model (sentence-transformers/all-MiniLM-L6-v2) -- nothing sent to the internet
4. Embeddings are stored in ChromaDB, a local vector database on your hard drive
5. When you ask a question, it's embedded the same way and matched against stored chunks by semantic similarity
6. Claude gets the relevant text, source, date, and a confidence score

Each YouTube channel and document set gets its own database. You can search one or all.

---

## Directory Structure

```
knowledge-base-kit/
|-- config/                        # Your profile, channels, env vars
|-- knowledge_bases/
|   |-- books/                     # Marketing & strategy books (Hormozi, Brunson)
|   |-- documents/                 # Drop your files here to index them
|   |-- prompts/                   # Prompt templates for content generation
|   |-- vectors/                   # Searchable databases (auto-created)
|       |-- youtube_channel_junkies/  # Pre-built strategy DB
|-- tools/
|   |-- rag_tools/                 # Knowledge base create, query, manage
|   |-- youtube_tools/             # Transcript fetch, ingest, analyze
|-- mcp_server/                    # Connects Claude Code to your tools
|-- scripts/                       # Setup and ingestion scripts
|-- examples/                      # Sample configurations
|-- .claude/                       # Claude Code config
|   |-- agents/                    # Knowledge base builder agent
|   |-- rules/                     # Coding conventions
```

---

## Customization

### Adding Your Own Prompts

Drop markdown files into `knowledge_bases/prompts/`. These give Claude templates for how to use your knowledge base. Three examples are included:

- `competitive_analysis.md` -- Research competitor coverage before creating content
- `content_from_knowledge_base.md` -- Generate blogs, emails, or guides from your KB
- `email_sequence.md` -- Write nurture emails grounded in your expertise

### Making It Your Own

Edit `.claude/CLAUDE.md` to add your business-specific instructions, brand voice guidelines, or content rules. Claude reads this file at the start of every session.

### Creating Agents

Add `.md` files to `.claude/agents/` to create specialized Claude Code agents. See the included `knowledge-base-builder.md` for the format.

---

## FAQ

**Is my data private?**
Yes. Everything runs locally. The only external connection is to YouTube for downloading public transcripts.

**Do I need API keys?**
No. The core knowledge base features run entirely on your machine with no API keys needed.

**What if I don't have a YouTube channel?**
The document indexing works without YouTube. Drop PDFs, Word docs, or text files into `knowledge_bases/documents/` and index them.

**Can I use this for any industry?**
Yes. Edit `config/profile.yaml` with your industry, topics, and voice. The tools are industry-agnostic.

**How do I update my knowledge base?**
Run the ingest command again -- it automatically skips videos already in the database and only adds new ones.

---

## Tech Stack

| Component | Technology |
|---|---|
| Vector Database | ChromaDB (local, no cloud) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (local) |
| Text Splitting | LangChain RecursiveCharacterTextSplitter |
| Transcript Download | yt-dlp |
| MCP Server | Node.js + @modelcontextprotocol/sdk |
| Python Tools | Python 3.10+ with chromadb, langchain |

---

## Credits

Built by [Aaron Chand](https://www.youtube.com/@livinginst-pete) using:
- **Channel Junkies** -- YouTube lead generation methodology
- **Russell Brunson** -- Epiphany Bridge and Daily Seinfeld email frameworks
- **Alex Hormozi** -- Lead magnet, offer, and ad frameworks
- **LangChain + ChromaDB** -- Local AI search infrastructure
- **Model Context Protocol (MCP)** -- Claude Code tool integration

## License

MIT License. Use it, modify it, share it.
