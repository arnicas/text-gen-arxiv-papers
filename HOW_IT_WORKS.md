# How This Code Works

This project automatically scrapes arXiv papers related to text generation and builds Jekyll-formatted pages for a website.

## Overview

The system consists of two main scripts that run sequentially:

1. **scrape.py** - Fetches papers from arXiv API
2. **build_pages.py** - Processes the data and generates markdown pages

## Workflow

### 1. Scraping Papers (`scrape.py`)

**What it does:**
- Queries the arXiv API for papers matching specific search criteria
- Searches across multiple categories: story generation, games, dialogue, poetry, and creativity
- Fetches up to 50 most recently updated papers per category
- Filters results to only include relevant CS categories (cs.CL, cs.AI, cs.LG, etc.)

**Active categories:**
- **story** - Story and narrative generation
- **games** - Game-related text generation
- **dialogue** - Dialogue and conversation generation
- **poetry** - Poetry and lyrics generation
- **creativity** - Creative text generation (novelty, originality, imagination, diversity)

**Disabled categories:**
The following categories are no longer actively searched but their historical data is preserved:
- **knowledge** - Knowledge graphs and semantic text generation
- **image2text** - Image captioning and description
- **table2text** - Table-to-text generation

**Search queries:**
Each category has a predefined search query that looks for:
- Base language model terms (e.g., "text generation", "LLM generation", "language model output")
- Category-specific terms (e.g., "story", "dialogue", "poetry", "creative")

**Output:**
- Saves results as a pickle file: `pickles/datadict-YYYY-MM-DD.p`
- Data structure: Dictionary with category keys, each containing a list of paper metadata

**Paper metadata includes:**
- Title
- Authors
- Publication date
- Abstract
- arXiv ID/link
- Categories
- Search type

### 2. Building Pages (`build_pages.py`)

**What it does:**
- Loads the most recent pickle file (or a specified one via `--pickle` argument)
- Compares new papers against existing data to find updates
- Generates markdown files for Jekyll static site
- Updates tracking file to maintain site structure

**Key functions:**

**`handle_new_data(categ, written_df, newdata)`**
- Finds the most recent data file for a category
- Compares publication dates to identify new papers
- Merges new papers with existing ones
- Removes duplicates based on arXiv ID
- Creates updated data CSV files

**`update_files_written_df(written_df, newrow, prev_datafile)`**
- Adds new entry to the tracking file
- Updates "next_link" references in previous pages
- Marks old files for deletion
- Maintains the linked list structure of pages

**`write_table_md(df, date, categ, prevlink, nextlink, most_recent)`**
- Generates Jekyll markdown files with front matter
- Creates navigation links between pages
- Writes markdown tables with paper information
- Updates both the dated post and the main category page

**Output files:**
- Data CSVs: `_data/{category}/{date}-{category}-{count}.csv`
- Markdown posts: `categories/{category}/_posts/{date}-{category}.md`
- Category landing pages: `categories/{category}/{category}.md`
- Tracking file: `_data/files_written.jsonl`

### 3. Tracking System (`files_written.jsonl`)

**Purpose:** Maintains a record of all generated files and their relationships

**Each record contains:**
- `date` - Publication date of the newest paper in the set
- `category` - Paper category (story, dialogue, etc.)
- `md_filename` - Path to the markdown file
- `generated_file` - Path to the generated HTML file
- `data_file` - Path to the CSV data file
- `most_recent` - Boolean flag for the latest entry in each category
- `count` - Number of papers in the dataset
- `prev_link` - Link to the previous page in the category
- `next_link` - Link to the next page in the category

**How it works:**
- Only records with `most_recent: true` are used for comparison when finding new papers
- When new papers are found, the previous "most recent" entry is updated with a next_link
- Old data and markdown files are moved to `old_files/` directory

## Running the Scripts

### Manual execution:
```bash
# Run in conda environment
conda run -n pandasnlp python scrape.py
conda run -n pandasnlp python build_pages.py

# Or specify a pickle file
conda run -n pandasnlp python build_pages.py --pickle pickles/datadict-2025-11-14.p
```

### Automated execution:
```bash
conda run -n pandasnlp bash run_all.sh
```

The `run_all.sh` script:
1. Runs scrape.py to fetch new data
2. Runs build_pages.py to generate pages
3. Stages changes with git
4. Commits with today's date
5. Pushes to remote repository

## Dependencies

- pandas - Data manipulation
- atoma - Atom/RSS feed parsing
- requests - HTTP requests to arXiv API
- feedparser - Alternative feed parsing
- pickle - Data serialization

## Disabled Categories

Categories can be disabled while preserving their historical data. Disabled categories:
- Are commented out in the `queries` dictionary in `scrape.py`
- Are listed in the `DISABLED_CATEGORIES` list in `build_pages.py`
- Display a notice on their pages: "This category is no longer being actively searched"
- Maintain all existing data and pages
- Are still accessible via the navigation menu

To disable a category:
1. Comment out the category in the `queries` dict in `scrape.py` (line ~66-74)
2. Add the category name to `DISABLED_CATEGORIES` in `build_pages.py` (line 14)
3. Run `build_pages.py` to regenerate all pages with the disabled notice

To re-enable a category:
1. Uncomment the category in the `queries` dict in `scrape.py`
2. Remove the category from `DISABLED_CATEGORIES` in `build_pages.py`
3. Run the scraper and build scripts as normal

## Adding New Categories

To add a new category:
1. Define a new search query in `scrape.py` (around line 17-29)
2. Add the category to the `queries` dictionary in `scrape.py` (around line 66-74)
3. Create directory structure: `categories/{category}/`, `categories/{category}/_posts/`, `_data/{category}/`
4. Add navigation entry to `_data/navigation.yml`
5. Run `scrape.py` to fetch initial papers
6. Bootstrap the category with initial data (create CSV, markdown files, and entry in `files_written.jsonl`)
7. Future runs will automatically update the category

## Important Notes

- The code uses `pd.concat()` instead of deprecated `.append()` method (pandas 2.0+ compatible)
- Papers are only added if their publication date is newer than the most recent existing entry
- The system automatically handles duplicate removal based on arXiv ID
- Each category maintains its own chronological chain of pages with prev/next navigation
- The `time.sleep(2)` in scrape.py delays between API requests (not between entries) to be respectful to arXiv's servers
