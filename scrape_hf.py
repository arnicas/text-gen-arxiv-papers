"""
Hugging Face Papers search module.
Queries the HF Papers API (semantic + full-text hybrid search) for each category.
Returns data in the same dict-of-lists format as scrape.py.
"""

import requests
import time
from datetime import datetime, timezone


# Semantic search queries per category — simpler than arXiv keyword queries
# since HF does hybrid semantic + full-text search
HF_QUERIES = {
    "story": "story generation narrative fiction plot language model",
    "games": "game text generation NPC dialogue interactive fiction",
    "dialogue": "dialogue generation conversation chatbot characters language model",
    "poetry": "poetry generation poem lyrics language model",
    "creativity": "creative text generation LLM originality novelty imaginative diverse ideation",
}

HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
HF_PAPER_API_URL = "https://huggingface.co/api/papers"


def normalize_arxiv_id(paper_id):
    """Convert a bare arXiv ID like '2603.05890' to the full URL format used by scrape.py."""
    # Strip version suffix for matching but keep full ID for URL
    return f"http://arxiv.org/abs/{paper_id}"


def extract_arxiv_id_bare(id_string):
    """Extract bare arXiv ID (e.g., '2603.05890') from either a full URL or bare ID."""
    if "arxiv.org/abs/" in id_string:
        bare = id_string.split("arxiv.org/abs/")[-1]
    else:
        bare = id_string
    # Remove version suffix for matching (e.g., 'v1', 'v2')
    if bare and bare[-2] == "v" and bare[-1].isdigit():
        bare = bare[:-2]
    elif bare and len(bare) > 2 and bare[-3] == "v" and bare[-2:].isdigit():
        bare = bare[:-3]
    return bare


def search_hf_papers(query, limit=50):
    """Search HF Papers API and return list of paper dicts."""
    params = {"q": query, "limit": limit}
    try:
        response = requests.get(HF_SEARCH_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"HF search error for query '{query}': {e}")
        return []


def hf_result_to_paper_dict(item, searchtype):
    """Convert an HF search result item to a paper dict matching scrape.py format."""
    paper = item["paper"]
    paper_id = paper["id"]

    # Extract author names
    authors = []
    for author in paper.get("authors", []):
        name = author.get("name", "")
        if name:
            authors.append(name)

    # HF doesn't always have arXiv categories in the search result.
    # We'll set a placeholder — the arXiv merge will fill in real categories if matched.
    categories = ""

    # Parse ISO date string to datetime with timezone
    pub_str = paper.get("publishedAt", "")
    if pub_str:
        try:
            pubdate = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pubdate = pub_str
    else:
        pubdate = None

    return {
        "title": paper.get("title", ""),
        "pubdate": pubdate,
        "id": normalize_arxiv_id(paper_id),
        "authors": ", ".join(authors),
        "categories": categories,
        "search": searchtype,
        "abstract": paper.get("summary", ""),
        "hf_upvotes": paper.get("upvotes", 0),
        "source": "hf",
    }


def get_hf_papers():
    """
    Query HF Papers search for all active categories.
    Returns dict matching scrape.py format: {category: [paper_dicts]}
    """
    results = {}

    for searchtype, query in HF_QUERIES.items():
        print(f"HF search: {searchtype} -> '{query}'")
        raw_results = search_hf_papers(query)
        papers = []
        for item in raw_results:
            paper = hf_result_to_paper_dict(item, searchtype)
            papers.append(paper)
        results[searchtype] = papers
        print(f"  Found {len(papers)} papers from HF")
        time.sleep(1)  # Be respectful to HF API

    return results


def merge_arxiv_and_hf(arxiv_data, hf_data):
    """
    Merge arXiv and HF results per category.
    Returns merged dict with 'source' and 'hf_upvotes' fields set.

    - Papers in both: source="both", hf_upvotes from HF
    - Papers in arXiv only: source="arxiv", hf_upvotes=0
    - Papers in HF only: source="hf", hf_upvotes from HF
    """
    merged = {}

    all_categories = set(list(arxiv_data.keys()) + list(hf_data.keys()))

    for categ in all_categories:
        arxiv_papers = arxiv_data.get(categ, [])
        hf_papers = hf_data.get(categ, [])

        # Index HF papers by bare arXiv ID
        hf_by_id = {}
        for p in hf_papers:
            bare_id = extract_arxiv_id_bare(p["id"])
            hf_by_id[bare_id] = p

        result = []
        seen_ids = set()

        # Process arXiv papers first
        for p in arxiv_papers:
            bare_id = extract_arxiv_id_bare(p["id"])
            seen_ids.add(bare_id)
            if bare_id in hf_by_id:
                # Found in both sources
                hf_paper = hf_by_id[bare_id]
                p["source"] = "both"
                p["hf_upvotes"] = hf_paper.get("hf_upvotes", 0)
            else:
                p["source"] = "arxiv"
                p["hf_upvotes"] = 0
            result.append(p)

        # Add HF-only papers
        for bare_id, p in hf_by_id.items():
            if bare_id not in seen_ids:
                # HF-only paper — source already set to "hf"
                result.append(p)

        merged[categ] = result
        both_count = sum(1 for p in result if p["source"] == "both")
        hf_only_count = sum(1 for p in result if p["source"] == "hf")
        arxiv_only_count = sum(1 for p in result if p["source"] == "arxiv")
        print(f"  {categ}: {len(result)} total ({arxiv_only_count} arXiv-only, {both_count} both, {hf_only_count} HF-only)")

    return merged


if __name__ == "__main__":
    # Test run
    hf_data = get_hf_papers()
    for categ, papers in hf_data.items():
        print(f"\n{categ}: {len(papers)} papers")
        for p in papers[:3]:
            print(f"  - {p['title'][:60]}... (upvotes: {p['hf_upvotes']})")
