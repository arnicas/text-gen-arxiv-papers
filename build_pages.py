
import argparse
from datetime import datetime
import numpy as np
from pathlib import Path
import os
import pickle
import pandas as pd
import time
import shutil

PICK_PATH = './pickles/'
FILES_WRITTEN_DATA = "_data/files_written.jsonl"

today = datetime.today().strftime('%Y-%m-%d')

def create_df_from_new_vals(vals):
    # scraped new data
    df = pd.DataFrame(vals)
    df['pubdate'] = pd.to_datetime(df['pubdate'], utc=True)
    df.sort_values(by=["pubdate", "title"], ascending=False, inplace=True)
    df['displaydate'] = df['pubdate'].dt.strftime('%Y-%m-%d')
    return df


def write_new_df_data(df, categ, tag=None):
    df['pubdate'] = pd.to_datetime(df['pubdate'], utc=True)
    df.sort_values(by="pubdate", ascending=False, inplace=True)
    df['displaydate'] = df['pubdate'].dt.strftime('%Y-%m-%d')
    date = df.iloc[0]['displaydate']
    print("Writing new data file", date, categ)
    if tag:
        filename = f"_data/{categ}/{tag}-{date}-{categ}-{str(len(df))}.csv"
        df.to_csv(filename, index=None)
    else:
        filename = f"_data/{categ}/{date}-{categ}-{str(len(df))}.csv"
        df.to_csv(filename, index=None)
    return date, filename


def make_date_path(date):
    return date.replace('-', '/') + '/'


# where the page ends up published by category
def make_entry_for_md(date, categ):
    """ actually creates the html link for a date categ page """
    filepath = 'categories/' + categ + '/' + make_date_path(date) + categ + '.html'
    return filepath


def most_recent_data_file(categ, written_df) -> dict:
    subset = written_df[written_df['category']==categ]
    row = subset[subset['most_recent']]
    return row.to_dict(orient="records")[0]


def write_table_in_md(df, handle):
    df = df[['title', 'authors', 'categories', 'id', 'displaydate']]
    headers = list(df.columns)
    headers.remove('id')
    handle.write("\n")
    handle.write(f"*written on {today}*\n\n")
    handle.write('| ' + ' | '.join(headers) + " |\n")
    handle.write('| ' + ' | '.join(['-----' for x in range(len(headers))]) + ' |\n')
    for i, row in df.iterrows():
        title = row['title'].replace('\n','')
        titlelink = f"[{title}]({row['id']})"
        authors = row['authors']
        categories = row['categories']
        ddate = row['displaydate']
        items = [titlelink, authors, categories, ddate]
        handle.write('| ' + ' | '.join(items) + ' |\n')
    handle.write('\n')
    return


def write_table_md(df, date, categ, prevlink, nextlink=None, most_recent=False):
    if type(prevlink) is str:
        prevlink = "{{site.url}}" + prevlink
    if type(nextlink) is str:
        nextlink = "{{site.url}}" + nextlink
    md_filename = 'categories/' + categ + '/_posts/' + str(date) + '-' + categ + '.md'
    with open(md_filename, 'w') as handle:
        handle.write("---\n")
        handle.write('category: ' + categ + '\n')
        handle.write('layout: post\n')
        handle.write('sidebar:\n')
        handle.write('  nav: contents\n')
        handle.write('---\n\n')
        write_table_in_md(df, handle)
        if type(prevlink) is str:
            handle.write(f'[< Previous]({prevlink})\n')
        if type(nextlink) is str:
            handle.write(f'[Next >]({nextlink})\n')
    if most_recent:
        # write the main page too
        top_page_md = 'categories/' + categ + '/' + categ + '.md'
        with open(top_page_md, 'w') as handle:
            handle.write("---\n")
            handle.write('category: ' + categ + '\n')
            handle.write('layout: page\n')
            handle.write('title: ' + categ + '\n')
            handle.write('sidebar:\n')
            handle.write('  nav: contents\n')
            handle.write('---\n\n')
            write_table_in_md(df, handle)
            if type(prevlink) is str:
                handle.write(f'[< Previous]({prevlink})\n')
    print("Wrote ", md_filename)


def delete_old_files(files):
    for file in files:
        path = Path(file)
        try:
            shutil.copy(str(path), 'old_files/' + str(path.name))
            os.remove(file)
            print("Deleted file", file)
        except:
            print("No such file to delete:", file)


def get_new_data_as_df(arts2, categ):
    print(len(arts2[categ]))
    return create_df_from_new_vals(arts2[categ])


def update_files_written_df(written_df, newrow, prev_datafile):
    """Adds row and deletes previous related one. Fixes old link to the new file. """
    written_df = written_df.append(newrow, ignore_index=True)
    old_one = written_df.loc[written_df['data_file'] == prev_datafile]
    try:
        old_gen_file = old_one['generated_file'].values[0]
    except:
        print("error with build files:", old_one['generated_file'])
        exit()
    new_gen_file = newrow['generated_file'] # str already
    print(old_gen_file, new_gen_file)
    written_df.replace({old_gen_file: new_gen_file}, regex=False, inplace=True)   # but those rows need to be rewritten
    written_df.loc[written_df['data_file'] == prev_datafile, 'delete'] = True # mark to delete
    written_df = written_df[~written_df['delete']] # could do in one line
    return written_df
    

def handle_new_data(categ, written_df, newdata):
    """
     The file list of data and pages generated and links is written_df.  The new data is what was scraped.
     This is specific to a category - we do it for each category of results found.
     Have to also rewrite the md for the previous page, so the 'next' link points to correct current one.
     """
    old_record_row = most_recent_data_file(categ, written_df)
    old_record_row_datafile = old_record_row['data_file']
    old_record_row_mdfile = old_record_row['md_filename']
    old_record_row_gen_file = old_record_row['generated_file']
    old_records = pd.read_csv(old_record_row['data_file'])
    old_records.sort_values(by="pubdate", ascending=False, inplace=True)
    newdf = get_new_data_as_df(newdata, categ)
    newdf.sort_values(by="pubdate", ascending=False, inplace=True)
    old_pubdate = old_records.iloc[0]['pubdate']
    maybenew = newdf[newdf['pubdate'] > old_pubdate]
    if len(maybenew) > 0:
        combo = pd.concat([maybenew, old_records], ignore_index=True)
        combo = combo.drop_duplicates(subset=["id"])
        if len(combo) == len(old_records):
            print("nothing to update.")
        else:
            print("Update needed, new articles since last date for", categ, len(combo) - len(old_records))
            date, datafile = write_new_df_data(combo, categ)
            count = len(combo)
            prev_link = old_record_row['prev_link']
            next_link = None
            md_filename = f"categories/{categ}/_posts/{date}-{categ}.md"
            generated_file = make_entry_for_md(date, categ) # html filename
            new_row = {'date': date, 'category': categ, 'md_filename': md_filename,
                'generated_file': generated_file, 'data_file': datafile, 'most_recent': True, 
                'count': count, 'delete': False, 'prev_link': prev_link, 'next_link': next_link}
            written_df = update_files_written_df(written_df, new_row, old_record_row_datafile)
            #write_table_md(combo, date, categ, prev_link, nextlink=next_link, most_recent=True) # actually create page
            write_all_md_files(written_df)
            delete_old_files([old_record_row_datafile, old_record_row_gen_file, old_record_row_mdfile])
    return written_df


def write_all_md_files(written_df):
    for key, vals in written_df.groupby('category'):
        ecs = vals.sort_values('date').to_dict(orient="records")
        for rec in recs:
            row = rec.copy()
            df = pd.read_csv(row['data_file'])
            categ = row['category']
            date = row['date'].strftime('%Y-%m-%d')  # make sure it's a string for filenames
            prevlink = row['prev_link']
            nextlink = row['next_link']
            most_recent = row['most_recent']
            write_table_md(df, date, categ, prevlink, nextlink=nextlink, most_recent=most_recent)

def write_new_files_after_scrape(newdata):
    written_df = pd.read_json(FILES_WRITTEN_DATA, orient="records", lines=True)
    written_df['date'] = written_df['date'].dt.strftime('%Y-%m-%d')

    categs = newdata.keys()
    today = datetime.today().strftime('%Y-%m-%d')
    shutil.copy(FILES_WRITTEN_DATA, 'old_files/files_written-backup-' + today + '.jsonl')
    for categ in categs:
        print("Looking at category", categ)
        new_written = handle_new_data(categ, written_df, newdata)
        new_written.to_json(FILES_WRITTEN_DATA, orient="records", lines=True)
        written_df = pd.read_json(FILES_WRITTEN_DATA, orient="records", lines=True)
        written_df['date'] = written_df['date'].dt.strftime('%Y-%m-%d')
    return

def get_latest_pickle():
    latest = max(Path(PICK_PATH).glob(r'*.p'), key=lambda f: f.stat().st_ctime)
    return str(latest)

def main(pickfile):
    artsfound = None
    if not pickfile:
        pickfile = get_latest_pickle()
        print("Using latest pickle file", pickfile)
    if '/' not in pickfile:
        pickfile = PICK_PATH + pickfile
    try: 
        artsfound = pickle.load(open(pickfile, 'rb'))
    except:
        print("error with pickle file name or path?")
        exit()
    if artsfound:
        print("loaded data, processing....")
        write_new_files_after_scrape(artsfound)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pickle', type=str, default=None)
    args = parser.parse_args()
    main(args.pickle)
