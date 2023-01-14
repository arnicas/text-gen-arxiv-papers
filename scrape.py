import atoma
import feedparser
import more_itertools
import numpy as np
import os
import pickle
import pandas as pd
import urllib
import requests
import shutil
import time

from collections import defaultdict
from datetime import datetime
from pathlib import Path

search_query_story = '%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"OR+abs:"plot%20generation"OR+abs:"story%20generation"OR+abs:"generated%20stories"%29+AND+%28abs:narrative+OR+abs:story+OR+abs:fiction+OR+abs:plot%29'

search_query_tables = '%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"%29+AND+%28abs:tables+OR+abs:data+OR+abs:structured+OR+abs:table-to-text%29'

search_query_games = '%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"%29+AND+%28abs:games+OR+abs:game%29'

search_query_knowledge = '%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"%29+AND+%28abs:knowledge+OR+abs:graphs+OR+abs:semantics%29'

search_query_poetry = '%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"+OR+abs:"generating%20poetry"%29+AND+%28abs:poetry+OR+abs:poems+OR+abs:lyrics%29'

search_query_dialogue = '%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"+OR+abs:"generating%20dialogue"%29+AND+%28abs:dialogue+OR+abs:agents+OR+abs:conversation%29'

search_query_images = '%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"+OR+abs:"generating%20captions"%29+AND+%28abs:images+OR+abs:image2text+OR+abs:description+OR+abs:image-to-text+OR+abs:caption%29'


base_url = "http://export.arxiv.org/api/query?"


cats_of_interest = [
    "cs.CL",
    "cs.HC",
    "cs.AI",
    "cs.DL",
    "cs.GT",
    "cs.GL",
    "cs.IR",
    "cs.DB",
    "cs.IT",
    "cs.LG",
    "cs.MA",
    "cs.MM",
    "cs.NE",
    "cs.SI",
]


def create_df_from_new_vals(vals):
    # scraped new data
    df = pd.DataFrame(vals)
    df["pubdate"] = pd.to_datetime(df["pubdate"], utc=True)
    df = df.sort_values(by=["pubdate", "title"], ascending=False)
    df["displaydate"] = df["pubdate"].dt.strftime("%Y-%m-%d")
    return df


def get_new():
    arts2 = {}

    queries = {
        "story": search_query_story,
        "table2text": search_query_tables,
        "games": search_query_games,
        "dialogue": search_query_dialogue,
        "knowledge": search_query_knowledge,
        "poetry": search_query_poetry,
        "image2text": search_query_images,
    }

    sort = "&sortBy=lastUpdatedDate&sortOrder=descending"
    start = 0  # retreive the first n results
    max_results = 20

    for searchtype, querystring in queries.items():
        query = "search_query=%s&start=%i&max_results=%i" % (querystring, start, max_results) + sort
        response = requests.get(base_url + query)
        feed = atoma.parse_atom_bytes(response.content)
        arts2[searchtype] = []
        for entry in feed.entries:
            cats = []
            for cat in entry.categories:
                cats.append(cat.term)
            if not set(cats).intersection(set(cats_of_interest)):
                continue
            pubdate = entry.published
            title = entry.title.value
            authors = []
            for author in entry.authors:
                authors.append(author.name)
            abslink = entry.id_
            text = entry.summary.value
            data = {
                "title": title,
                "pubdate": pubdate,
                "id": abslink,
                "authors": ", ".join(authors),
                "categories": ", ".join(cats),
                "search": searchtype,
                "abstract": text,
            }
            arts2[searchtype].append(data)
            time.sleep(2)
    return arts2


def report_dates(datadict):
    for key, vals in datadict.items():
        print(key, len(vals))
        df = create_df_from_new_vals(vals)
        print(df.iloc[0]["pubdate"])


def save_pickle(datadict):
    filename = "./pickles/datadict-" + datetime.today().strftime("%Y-%m-%d") + ".p"
    pickle.dump(datadict, open(filename, "wb"))
    print("wrote file", filename)


datadict = get_new()

report_dates(datadict)

save_pickle(datadict)

