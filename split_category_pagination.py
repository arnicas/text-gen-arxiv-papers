#!/usr/bin/env python3
"""
Split a category page into current + historical pages for pagination.

Usage:
    python split_category_pagination.py --category story --keep-recent 150

This will:
- Keep the 150 most recent papers on the current page
- Move older papers to a new historical page
- Set up pagination links between them
"""

import argparse
import pandas as pd
import os
from datetime import datetime
from build_pages import write_all_md_files, make_entry_for_md

def split_category(category, keep_recent_count):
    """
    Split a category's most recent page into current + historical.

    Args:
        category: Category name (e.g., 'story', 'games')
        keep_recent_count: Number of recent papers to keep on current page
    """

    # 1. Load tracking file
    written_df = pd.read_json('_data/files_written.jsonl', orient='records', lines=True)

    # 2. Find the most recent entry for this category
    category_entries = written_df[written_df['category'] == category]
    most_recent_entry = category_entries[category_entries['most_recent'] == True]

    if len(most_recent_entry) == 0:
        print(f"ERROR: No most_recent entry found for category '{category}'")
        return

    most_recent_entry = most_recent_entry.iloc[0]

    # 3. Load the papers from the current page
    current_data_file = most_recent_entry['data_file']

    if not os.path.exists(current_data_file):
        print(f"ERROR: Data file not found: {current_data_file}")
        return

    all_papers = pd.read_csv(current_data_file)
    all_papers['pubdate'] = pd.to_datetime(all_papers['pubdate'], utc=True)
    all_papers = all_papers.sort_values(by='pubdate', ascending=False)

    total_papers = len(all_papers)

    if total_papers <= keep_recent_count:
        print(f"Category '{category}' only has {total_papers} papers.")
        print(f"Not enough to split (requested to keep {keep_recent_count} recent)")
        return

    print(f"\nCategory: {category}")
    print(f"Total papers: {total_papers}")
    print(f"Will keep {keep_recent_count} recent papers on current page")
    print(f"Will move {total_papers - keep_recent_count} older papers to historical page")

    # 4. Split the papers
    recent_papers = all_papers.iloc[:keep_recent_count]  # Most recent
    older_papers = all_papers.iloc[keep_recent_count:]   # Older

    # Add displaydate if not present
    if 'displaydate' not in recent_papers.columns:
        recent_papers['displaydate'] = recent_papers['pubdate'].dt.strftime('%Y-%m-%d')
    if 'displaydate' not in older_papers.columns:
        older_papers['displaydate'] = older_papers['pubdate'].dt.strftime('%Y-%m-%d')

    recent_date = recent_papers.iloc[0]['displaydate']  # Newest paper date
    older_date = older_papers.iloc[0]['displaydate']    # Newest of the older papers

    print(f"\nRecent page: {keep_recent_count} papers, newest from {recent_date}")
    print(f"Historical page: {len(older_papers)} papers, newest from {older_date}")

    # 5. Create data files
    print("\nCreating data files...")

    # Historical data file
    historical_csv = f"_data/{category}/{older_date}-{category}-{len(older_papers)}.csv"
    older_papers.to_csv(historical_csv, index=False)
    print(f"✓ Created {historical_csv}")

    # Updated current data file
    current_csv = f"_data/{category}/{recent_date}-{category}-{len(recent_papers)}.csv"
    recent_papers.to_csv(current_csv, index=False)
    print(f"✓ Created {current_csv}")

    # 6. Create tracking entries
    print("\nUpdating tracking file...")

    # Get the current entry's prev_link (we'll use it for historical page)
    current_prev_link = most_recent_entry['prev_link']
    if pd.isna(current_prev_link):
        current_prev_link = None

    # Historical entry
    historical_entry = {
        'date': older_date,
        'category': category,
        'md_filename': f'categories/{category}/_posts/{older_date}-{category}.md',
        'generated_file': make_entry_for_md(older_date, category),
        'data_file': historical_csv,
        'most_recent': False,
        'count': len(older_papers),
        'delete': False,
        'prev_link': current_prev_link,  # Inherits current's prev_link
        'next_link': make_entry_for_md(recent_date, category)  # Points to new current
    }

    # Updated current entry
    updated_current_entry = {
        'date': recent_date,
        'category': category,
        'md_filename': f'categories/{category}/_posts/{recent_date}-{category}.md',
        'generated_file': make_entry_for_md(recent_date, category),
        'data_file': current_csv,
        'most_recent': True,
        'count': len(recent_papers),
        'delete': False,
        'prev_link': make_entry_for_md(older_date, category),  # Points back to historical
        'next_link': None  # Most recent has no next
    }

    # 7. Update files_written.jsonl

    # Mark old entry for deletion
    written_df.loc[
        (written_df['category'] == category) & (written_df['most_recent'] == True),
        'delete'
    ] = True

    # Add new entries
    written_df = pd.concat([
        written_df,
        pd.DataFrame([historical_entry, updated_current_entry])
    ], ignore_index=True)

    # Remove deleted entries
    written_df = written_df[~written_df['delete']]

    # Update any references to old page in other entries' next_link
    old_generated_file = most_recent_entry['generated_file']
    new_generated_file = updated_current_entry['generated_file']
    written_df['next_link'] = written_df['next_link'].replace(
        old_generated_file,
        new_generated_file
    )

    # Save tracking file
    written_df.to_json('_data/files_written.jsonl', orient='records', lines=True)
    print("✓ Updated files_written.jsonl")

    # 8. Regenerate all markdown files
    print("\nRegenerating markdown files...")
    written_df['date'] = pd.to_datetime(written_df['date']).dt.strftime('%Y-%m-%d')
    write_all_md_files(written_df)
    print("✓ Markdown files regenerated")

    # 9. Report old files to delete
    print("\n" + "="*60)
    print("SUCCESS! Pagination created.")
    print("="*60)
    print(f"\nOld files to delete manually:")
    print(f"  - {current_data_file}")
    print(f"  - {most_recent_entry['md_filename']}")

    print(f"\nNew pagination chain for {category}:")
    if current_prev_link:
        print(f"  [...] ← {current_prev_link}")
    print(f"  {historical_entry['generated_file']} (historical, {len(older_papers)} papers)")
    print(f"    ↕")
    print(f"  {updated_current_entry['generated_file']} (current, {len(recent_papers)} papers)")

    print(f"\nVerify:")
    print(f"  - Historical page should have [Next >] link")
    print(f"  - Current page should have [< Previous] link")
    print(f"  - Main {category}.md page should have [< Previous] link")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Split a category page into current + historical for pagination'
    )
    parser.add_argument(
        '--category',
        required=True,
        help='Category name (e.g., story, games, poetry, creativity)'
    )
    parser.add_argument(
        '--keep-recent',
        type=int,
        required=True,
        help='Number of recent papers to keep on current page (e.g., 150)'
    )

    args = parser.parse_args()

    split_category(args.category, args.keep_recent)
