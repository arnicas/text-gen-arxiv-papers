
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
FILES_WRITTEN_DATA = "_data/files_written.csv"

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
    print("writing new data file", date, categ)
    if tag:
        filename = f'_data/{categ}/{tag}-' + date + '-' + categ + '-' + str(len(df)) + '.csv'
        df.to_csv(filename, index=None)
    else:
        filename = f'_data/{categ}/' + date + '-' + categ + '-' + str(len(df)) + '.csv'
        df.to_csv(filename, index=None)
    return date, filename


def add_to_record_get_prevlink(newdate, categ):
    df = pd.read_csv("_data/files_written.csv")
    subset = df[df['category'] == categ]
    subset.sort_values(by="date", ascending=False)
    prevlink = subset.iloc[0]['generated_file']
    generated_file = make_entry_for_md(newdate, categ)
    md_filename = f"{newdate}-{categ}.md"
    print('Adding to record file', newdate, categ, md_filename, generated_file)
    df = df.append({'date': newdate, 'category': categ, 'md_filename': md_filename, 'generated_file': generated_file},
             ignore_index=True)
    df.to_csv("_data/files_written.csv", index=None)


def make_date_path(date):
    return date.replace('-', '/') + '/'


# where the page ends up published by category - add to a data file?
def make_entry_for_md(date, categ):
    filepath = 'categories/' + categ + '/' + make_date_path(date) + categ + '.html'
    return filepath


def most_recent_data_file(categ, written_df):
    subset = written_df[written_df['category']==categ]
    row = subset[subset['most_recent']==True]
    return row


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


def write_table_md(df, date, categ, prevlink, most_recent=False):
    if type(prevlink) == str:
        prevlink = "{{site.url}}" + prevlink
    with open('categories/' + categ + '/_posts/' + date + '-' + categ + '.md', 'w') as handle:
        handle.write("---\n")
        handle.write('category: ' + categ + '\n')
        handle.write('layout: post\n')
        handle.write('sidebar:\n')
        handle.write('  nav: contents\n')
        handle.write('---\n\n')
        write_table_in_md(df, handle)
        if type(prevlink) == str:
            handle.write(f'[Previous]({prevlink})\n')
    if most_recent:
        # write the main page too
        with open('categories/' + categ + '/' + categ + '.md', 'w') as handle:
            handle.write("---\n")
            handle.write('category: ' + categ + '\n')
            handle.write('layout: page\n')
            handle.write('title: ' + categ + '\n')
            handle.write('sidebar:\n')
            handle.write('  nav: contents\n')
            handle.write('---\n\n')
            write_table_in_md(df, handle)
            if type(prevlink) == str:
                handle.write(f'[Previous]({prevlink})\n')
    print("Wrote ", 'categories/' + categ + '/_posts/' + date + '-' + categ + '.md')


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


def handle_new_data(categ, written_df, arts2):
    old_record_row = most_recent_data_file(categ, written_df)
    old_record_row_datafile = old_record_row['data_file'].values[0]
    old_record_row_mdfile = old_record_row['md_filename'].values[0]
    old_record_row_gen_file = old_record_row['generated_file'].values[0]
    old_records = pd.read_csv(old_record_row['data_file'].values[0])
    old_records.sort_values(by="pubdate", ascending=False, inplace=True)
    newdf = get_new_data_as_df(arts2, categ)
    newdf.sort_values(by="pubdate", ascending=False, inplace=True)
    old_pubdate = old_records.iloc[0]['pubdate']
    maybenew = newdf[newdf['pubdate'] > old_pubdate]
    if len(maybenew) > 0:
        combo = pd.concat([maybenew, old_records], ignore_index = True)
        combo = combo.drop_duplicates(subset=["id"])
        if len(combo) == len(old_records):
            print("nothing to update.")
        else:
            print("Update needed, new articles since last date for", categ, len(combo) - len(old_records))
            date, datafile = write_new_df_data(combo, categ)
            count = len(combo)
            md_filename = f"categories/{categ}/_posts/{date}-{categ}.md"
            generated_file = make_entry_for_md(date, categ)
            prev_link = old_record_row['prev_link'].values[0]
            next_link = None
            #print("len of written df", len(written_df))
            newrow = {'date': date, 'category': categ, 'md_filename': md_filename, 
                      'generated_file': generated_file, 'data_file': datafile, 'most_recent': True, 
                      'count': count, 'delete': False, 'prev_link': prev_link, 'next_link': next_link}
            newrowdf = pd.DataFrame(newrow, index=[0])
            written_df = written_df.append(newrowdf, ignore_index=True)
            #print("len of written df", len(written_df))
            written_df.loc[written_df['data_file'] == old_record_row_datafile, 'delete'] = True
            written_df = written_df[~written_df['delete']]
            #print("len of written df", len(written_df))
            write_table_md(combo, date, categ, prev_link, most_recent=True)
            delete_old_files([old_record_row_datafile, old_record_row_gen_file, old_record_row_mdfile])
    return written_df


def write_new_files_after_scrape(arts2):
    written_df = pd.read_csv("_data/files_written.csv")
    categs = arts2.keys()
    today = datetime.today().strftime('%Y-%m-%d')
    shutil.copy('_data/files_written.csv', 'old_files/files_written-backup-' + today + '.csv')
    for categ in categs:
        print("looking at category", categ)
        new_written = handle_new_data(categ, written_df, arts2)
        new_written.to_csv("_data/files_written.csv", index=None)
        written_df = pd.read_csv("_data/files_written.csv")

def get_latest_pickle():
    latest = max(Path(PICK_PATH).glob(r'*.p'), key=lambda f: f.stat().st_ctime)
    return str(latest)

def main(pickfile):
    arts2 = None
    if not pickfile:
        pickfile = get_latest_pickle()
        print("Using latest pickle file", pickfile)
    if '/' not in pickfile:
        pickfile = PICK_PATH + pickfile
    try: 
        arts2 = pickle.load(open(pickfile, 'rb'))
    except:
        print("error with pickle file name or path?")
        exit()
    if arts2:
        print("loaded data, processing....")
        write_new_files_after_scrape(arts2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pickle', type=str, default=None)
    args = parser.parse_args()
    main(args.pickle)
