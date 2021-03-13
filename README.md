# text-gen-arxiv-papers

This is the raw files for the gh pages site: [https://arnicas.github.io/text-gen-arxiv-papers](https://arnicas.github.io/text-gen-arxiv-papers).

Code used is being gradually cleaned up and checked in.  Basically I do most of it manually using pandas, since jekyll is pretty bad at what I needed.

The file scrape.py has the search strings and saves a pickle of the latest data from ArXiv.

The file build_pages.py takes the pickle as an argument and processes it. There are required files and directories etc. I'll try to document more and clean it up for re-use.



