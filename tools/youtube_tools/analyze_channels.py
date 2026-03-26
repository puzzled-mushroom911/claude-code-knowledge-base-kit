#!/usr/bin/env python3
"""
Analyze YouTube Channel Content from RAG Databases

Query ChromaDB vector databases for strategic content insights: topic
distribution, top performers, channel comparisons, content gaps, and
recommendations.

Dependencies:
    - chromadb
    - sentence-transformers

Usage:
    python3 analyze_channels.py topics --database my_channel
    python3 analyze_channels.py top --database my_channel --limit 10
    python3 analyze_channels.py compare --database my_channel --compare-db competitor
    python3 analyze_channels.py gaps --database my_channel --compare-db competitor
    python3 analyze_channels.py recommend --database my_channel
    python3 analyze_channels.py search "best practices" --database my_channel
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_DB_DIR = Path("./knowledge_bases/vectors")

# Lazy-loaded globals
_embedding_model = None


# ---------------------------------------------------------------------------
# ChromaDB Helpers
# ---------------------------------------------------------------------------


def get_embedding_model():
    """Lazy-load the sentence-transformers model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer

        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def load_collection(db_path: Path, collection_name: str = "langchain"):
    """Load a ChromaDB collection from disk."""
    import chromadb
    from chromadb.config import Settings

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}", file=sys.stderr)
        return None, None

    try:
        client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = client.get_collection(name=collection_name)
        return client, collection
    except Exception as e:
        try:
            client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False),
            )
            collections = client.list_collections()
            if collections:
                collection = collections[0]
                return client, collection
        except Exception:
            pass
        print(f"ERROR: Cannot open database at {db_path}: {e}", file=sys.stderr)
        return None, None


def get_all_videos(collection) -> list[dict]:
    """Extract unique video metadata from a ChromaDB collection."""
    result = collection.get(include=["metadatas"])
    seen: set[str] = set()
    videos: list[dict] = []

    for meta in result.get("metadatas", []):
        vid = meta.get("video_id", "")
        if vid and vid not in seen:
            seen.add(vid)
            videos.append(meta)

    return videos


def get_all_documents(collection) -> list[dict]:
    """Retrieve all documents with their content and metadata."""
    result = collection.get(include=["documents", "metadatas"])
    documents: list[dict] = []
    for doc, meta in zip(
        result.get("documents", []), result.get("metadatas", [])
    ):
        documents.append({"content": doc, "metadata": meta})
    return documents


# ---------------------------------------------------------------------------
# Analysis Commands
# ---------------------------------------------------------------------------


def cmd_topics(collection, limit: int = 20) -> None:
    """Analyze topic distribution across videos by extracting title keywords."""
    videos = get_all_videos(collection)

    if not videos:
        print("No videos found in database.")
        return

    print(f"\n{'=' * 60}")
    print(f"TOPIC DISTRIBUTION ({len(videos)} videos)")
    print(f"{'=' * 60}\n")

    # Extract meaningful keywords from titles (stop words filtered)
    stop_words = {
        "the", "a", "an", "in", "to", "of", "and", "is", "for", "on",
        "it", "my", "i", "you", "your", "we", "our", "this", "that",
        "with", "from", "at", "by", "or", "not", "are", "was", "be",
        "but", "if", "so", "do", "has", "how", "what", "why", "when",
        "will", "can", "|", "-", "about", "its", "just", "all", "new",
    }

    keyword_counts: Counter = Counter()
    keyword_views: dict[str, int] = defaultdict(int)
    keyword_videos: dict[str, list[str]] = defaultdict(list)

    for v in videos:
        title = v.get("title", "")
        title_lower = title.lower()
        views = v.get("view_count", 0)
        if isinstance(views, str):
            try:
                views = int(views)
            except ValueError:
                views = 0

        words = title_lower.split()
        seen_words: set[str] = set()
        for word in words:
            word = word.strip(",.!?()[]{}\"'#")
            if len(word) > 2 and word not in stop_words and word not in seen_words:
                seen_words.add(word)
                keyword_counts[word] += 1
                keyword_views[word] += views
                keyword_videos[word].append(title[:50])

    # Display results
    print(
        f"{'Keyword':<20} {'Videos':<10} {'Total Views':<15} {'Avg Views':<12}"
    )
    print("-" * 57)

    for keyword, count in keyword_counts.most_common(limit):
        if count < 2:
            continue  # Only show keywords appearing in 2+ videos
        avg_views = keyword_views[keyword] // count if count else 0
        print(
            f"{keyword:<20} {count:<10} {keyword_views[keyword]:>12,}   {avg_views:>9,}"
        )

    # Show top examples per keyword
    print(f"\n{'=' * 60}")
    print("TOP EXAMPLES PER KEYWORD")
    print(f"{'=' * 60}")
    shown = 0
    for keyword, count in keyword_counts.most_common(10):
        if count < 2:
            continue
        if shown >= 5:
            break
        shown += 1
        print(f"\n  {keyword.upper()} ({count} videos):")
        for title in keyword_videos[keyword][:3]:
            print(f"    - {title}")


def cmd_top(collection, limit: int = 10) -> None:
    """Show top-performing videos by view count."""
    videos = get_all_videos(collection)

    if not videos:
        print("No videos found in database.")
        return

    for v in videos:
        views = v.get("view_count", 0)
        if isinstance(views, str):
            try:
                v["_views"] = int(views)
            except ValueError:
                v["_views"] = 0
        else:
            v["_views"] = views or 0

    videos.sort(key=lambda x: x["_views"], reverse=True)

    print(f"\n{'=' * 60}")
    print(f"TOP {limit} VIDEOS BY VIEWS")
    print(f"{'=' * 60}\n")

    for i, v in enumerate(videos[:limit], 1):
        title = v.get("title", "Untitled")
        views = v["_views"]
        duration = v.get("duration_seconds", 0)
        date = v.get("upload_date", v.get("publish_date", ""))
        url = v.get("url", v.get("video_url", ""))
        channel = v.get("channel_name", "")

        print(f"{i:>3}. {title[:55]}")
        print(f"     Views: {views:,}  |  Date: {date}  |  Duration: {duration}s")
        if channel:
            print(f"     Channel: {channel}")
        if url:
            print(f"     {url}")
        print()


def cmd_compare(collection_a, collection_b, name_a: str, name_b: str) -> None:
    """Compare two channels side by side."""
    print(f"\n{'=' * 60}")
    print(f"CHANNEL COMPARISON")
    print(f"{'=' * 60}")

    stop_words = {
        "the", "a", "an", "in", "to", "of", "and", "is", "for", "on",
        "it", "my", "i", "you", "your", "we", "our", "this", "that",
        "with", "from", "at", "by", "or", "not", "are", "was", "be",
        "but", "if", "so", "do", "has", "how", "what", "why", "when",
        "will", "can", "|", "-", "about", "its", "just", "all", "new",
    }

    for name, collection in [(name_a, collection_a), (name_b, collection_b)]:
        videos = get_all_videos(collection)

        total_views = 0
        for v in videos:
            views = v.get("view_count", 0)
            if isinstance(views, str):
                try:
                    views = int(views)
                except ValueError:
                    views = 0
            total_views += views

        avg_views = total_views // len(videos) if videos else 0

        word_counts: Counter = Counter()
        for v in videos:
            title_words = v.get("title", "").lower().split()
            for word in title_words:
                word = word.strip(",.!?()[]{}\"'#")
                if len(word) > 2 and word not in stop_words:
                    word_counts[word] += 1

        top_words = [w for w, _ in word_counts.most_common(8)]

        print(f"\n  {name}")
        print(f"  {'-' * 40}")
        print(f"  Total Videos:      {len(videos)}")
        print(f"  Total Views:       {total_views:,}")
        print(f"  Avg Views/Video:   {avg_views:,}")
        print(f"  Top Keywords:      {', '.join(top_words)}")


def cmd_gaps(
    own_collection, competitor_collection, own_name: str, competitor_name: str
) -> None:
    """Find content gaps: topics the competitor covers that you do not."""
    print(f"\n{'=' * 60}")
    print(f"CONTENT GAPS: What {competitor_name} covers that {own_name} doesn't")
    print(f"{'=' * 60}\n")

    stop_words = {
        "the", "a", "an", "in", "to", "of", "and", "is", "for", "on",
        "it", "my", "i", "you", "your", "we", "our", "this", "that",
        "with", "from", "at", "by", "or", "not", "are", "was", "be",
        "but", "if", "so", "do", "has", "how", "what", "why", "when",
        "will", "can", "|", "-", "about", "its", "just", "all", "new",
    }

    def extract_keywords(collection) -> Counter:
        videos = get_all_videos(collection)
        word_freq: Counter = Counter()
        for v in videos:
            words = v.get("title", "").lower().split()
            for word in words:
                word = word.strip(",.!?()[]{}\"'#")
                if len(word) > 2 and word not in stop_words:
                    word_freq[word] += 1
        return word_freq

    own_keywords = extract_keywords(own_collection)
    competitor_keywords = extract_keywords(competitor_collection)

    gaps: list[tuple[str, int, int]] = []
    for word, comp_count in competitor_keywords.most_common(100):
        own_count = own_keywords.get(word, 0)
        if comp_count >= 2 and own_count <= comp_count // 3:
            gaps.append((word, comp_count, own_count))

    if not gaps:
        print("No significant content gaps found. Good coverage!")
        return

    print(
        f"{'Keyword':<25} {competitor_name + ' count':<20} {own_name + ' count':<20}"
    )
    print("-" * 65)

    for keyword, comp_count, own_count in gaps[:20]:
        print(f"{keyword:<25} {comp_count:<20} {own_count:<20}")

    comp_videos = get_all_videos(competitor_collection)
    print(f"\nSample competitor videos covering gap topics:")
    shown = 0
    for keyword, _, _ in gaps[:5]:
        for v in comp_videos:
            if keyword in v.get("title", "").lower() and shown < 10:
                views = v.get("view_count", 0)
                if isinstance(views, str):
                    try:
                        views = int(views)
                    except ValueError:
                        views = 0
                print(f"  [{keyword}] {v.get('title', '')[:55]} ({views:,} views)")
                shown += 1
                break


def cmd_recommend(collection, limit: int = 10) -> None:
    """Suggest next video topics based on performance patterns."""
    videos = get_all_videos(collection)

    if not videos:
        print("No videos found in database.")
        return

    print(f"\n{'=' * 60}")
    print("CONTENT RECOMMENDATIONS")
    print(f"{'=' * 60}\n")

    stop_words = {
        "the", "a", "an", "in", "to", "of", "and", "is", "for", "on",
        "it", "my", "i", "you", "your", "we", "our", "this", "that",
        "with", "from", "at", "by", "or", "not", "are", "was", "be",
        "but", "if", "so", "do", "has", "how", "what", "why", "when",
        "will", "can", "|", "-", "about", "its", "just", "all", "new",
    }

    keyword_views: dict[str, list[int]] = defaultdict(list)

    for v in videos:
        views = v.get("view_count", 0)
        if isinstance(views, str):
            try:
                views = int(views)
            except ValueError:
                views = 0

        title = v.get("title", "")
        words = title.lower().split()
        for word in words:
            word = word.strip(",.!?()[]{}\"'#")
            if len(word) > 2 and word not in stop_words:
                keyword_views[word].append(views)

    import math

    scored: list[tuple[str, float, int, int]] = []
    for keyword, views_list in keyword_views.items():
        if len(views_list) < 2:
            continue
        avg_views = sum(views_list) // len(views_list)
        frequency = len(views_list)
        score = avg_views * math.log2(frequency + 1)
        scored.append((keyword, score, avg_views, frequency))

    scored.sort(key=lambda x: x[1], reverse=True)

    print("High-performing topic keywords (by views x frequency):\n")
    print(f"{'Keyword':<20} {'Score':<12} {'Avg Views':<12} {'Frequency':<10}")
    print("-" * 54)

    for keyword, score, avg_views, freq in scored[:limit]:
        print(f"{keyword:<20} {score:>10,.0f}  {avg_views:>10,}  {freq:>8}")

    print(f"\nSuggested topic combinations (pair high-performing keywords):\n")
    top_keywords = [k for k, _, _, _ in scored[:8]]
    suggestions_shown = 0
    for i, kw1 in enumerate(top_keywords):
        for kw2 in top_keywords[i + 1 :]:
            combo_exists = False
            for v in videos:
                title_lower = v.get("title", "").lower()
                if kw1 in title_lower and kw2 in title_lower:
                    combo_exists = True
                    break
            if not combo_exists and suggestions_shown < limit:
                print(f"  - {kw1} + {kw2}")
                suggestions_shown += 1


def cmd_search(
    collection, query: str, limit: int = 5
) -> None:
    """Semantic search across channel content."""
    print(f"\n{'=' * 60}")
    print(f"SEARCH: \"{query}\"")
    print(f"{'=' * 60}\n")

    model = get_embedding_model()
    query_embedding = model.encode([query], show_progress_bar=False).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=limit,
        include=["documents", "metadatas", "distances"],
    )

    if not results["documents"] or not results["documents"][0]:
        print("No results found.")
        return

    seen_videos: set[str] = set()
    rank = 0

    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        video_id = meta.get("video_id", "")
        if video_id in seen_videos:
            continue
        seen_videos.add(video_id)
        rank += 1

        title = meta.get("title", "Untitled")
        url = meta.get("url", meta.get("video_url", ""))
        views = meta.get("view_count", 0)
        channel = meta.get("channel_name", "")
        relevance = 1.0 - distance

        print(f"{rank}. {title[:60]}")
        print(f"   Relevance: {relevance:.3f}  |  Views: {views:,}")
        if channel:
            print(f"   Channel: {channel}")
        if url:
            print(f"   URL: {url}")
        preview = doc[:200].replace("\n", " ").strip()
        print(f"   Preview: {preview}...")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def resolve_db_path(db_name: str, db_dir: Path) -> Path:
    """Resolve a database name to a full path."""
    candidate = Path(db_name)
    if candidate.is_absolute() and candidate.exists():
        return candidate
    if candidate.exists():
        return candidate.resolve()
    return db_dir / db_name


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze YouTube channel content from ChromaDB RAG databases.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  topics    - Topic distribution with view counts
  top       - Top performing videos by engagement
  compare   - Compare two channels side by side
  gaps      - Content gaps (competitor topics you haven't covered)
  recommend - Suggest next video topics
  search    - Semantic search across channel content

Examples:
  python3 analyze_channels.py topics --database my_channel
  python3 analyze_channels.py top --database my_channel --limit 20
  python3 analyze_channels.py compare --database my_channel --compare-db competitor
  python3 analyze_channels.py gaps --database my_channel --compare-db competitor
  python3 analyze_channels.py recommend --database my_channel
  python3 analyze_channels.py search "best practices" --database my_channel
        """,
    )

    parser.add_argument(
        "command",
        choices=["topics", "top", "compare", "gaps", "recommend", "search"],
        help="Analysis command to run",
    )
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Search query (required for 'search' command)",
    )
    parser.add_argument(
        "--database",
        type=str,
        required=True,
        help="ChromaDB database name or path",
    )
    parser.add_argument(
        "--compare-db",
        type=str,
        default=None,
        help="Second database for comparison (required for 'compare' and 'gaps')",
    )
    parser.add_argument(
        "--db-dir",
        type=Path,
        default=DEFAULT_DB_DIR,
        help=f"Parent directory for databases (default: {DEFAULT_DB_DIR})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum results to display (default: 10)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (where supported)",
    )

    args = parser.parse_args()

    if args.command == "search" and not args.query:
        parser.error("The 'search' command requires a query argument.")

    if args.command in ("compare", "gaps") and not args.compare_db:
        parser.error(
            f"The '{args.command}' command requires --compare-db."
        )

    db_path = resolve_db_path(args.database, args.db_dir)
    _, collection = load_collection(db_path)
    if collection is None:
        print(f"ERROR: Could not load database: {db_path}", file=sys.stderr)
        sys.exit(1)

    comp_collection = None
    if args.compare_db:
        comp_path = resolve_db_path(args.compare_db, args.db_dir)
        _, comp_collection = load_collection(comp_path)
        if comp_collection is None:
            print(
                f"ERROR: Could not load comparison database: {comp_path}",
                file=sys.stderr,
            )
            sys.exit(1)

    if args.command == "topics":
        cmd_topics(collection, limit=args.limit)
    elif args.command == "top":
        cmd_top(collection, limit=args.limit)
    elif args.command == "compare":
        cmd_compare(
            collection,
            comp_collection,
            name_a=args.database,
            name_b=args.compare_db,
        )
    elif args.command == "gaps":
        cmd_gaps(
            collection,
            comp_collection,
            own_name=args.database,
            competitor_name=args.compare_db,
        )
    elif args.command == "recommend":
        cmd_recommend(collection, limit=args.limit)
    elif args.command == "search":
        cmd_search(collection, query=args.query, limit=args.limit)


if __name__ == "__main__":
    main()
