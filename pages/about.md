---
layout: page
title: About
description: "How the searches work"
---

### How the Searches Work

There is limited functionality in the [ArXiv API](https://arxiv.org/help/api/), but it can do these.  But truly, thank you to ArXiv for use of its open access interoperability.

Note: I had a bug in the search for dialogue, so I am going to paste these in as I use them, in order to keep them up to date easier - which means url-encoded. 

* API Search String for Story: 
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"OR+abs:"plot%20generation"OR+abs:"story%20generation"%29+AND+%28abs:narrative+OR+abs:story+OR+abs:fiction+OR+abs:plot%2`
* API Search String for Table2Text:
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"%29+AND+%28abs:tables+OR+abs:data+OR+abs:structured+OR+abs:table-to-text%29`
* API Search String for Games:
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"+OR+abs:"generating%20games"%29+AND+%28abs:games+OR+abs:game%29`
* API Search String for Knowledge:
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"%29+AND+%28abs:knowledge+OR+abs:graphs+OR+abs:semantics%29`
* API Search String for Poetry:
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"+OR+abs:"generating%20poetry"%29+AND+%28abs:poetry+OR+abs:poems+OR+abs:lyrics%29`
* API Search String for Dialogue:
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"+OR+abs:"generating%20dialogue"%29+AND+%28abs:dialogue+OR+abs:agents+OR+abs:conversation%29`
* API Search String for Image2Text:
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"+OR+abs:"generating%20captions"%29+AND+%28abs:images+OR+abs:image2text+OR+abs:description+OR+abs:image-to-text+OR+abs:caption%29`
 
Let me know if you think the searches could be better?

Jekyll isn't good at category indexing etc, so I ended up making a bunch of python scripts to build the pages I needed.  Right now it runs on my laptop a few times a week.  This site makes poor use of the [Hyde theme by Mark Otto](https://github.com/poole/hyde), but I'm grateful for it.

I'm [@arnicas](https://twitter.com/arnicas) (Lynn Cherny) and if you like this you could [buy me a 🍺 beer or ☕ coffee](https://www.buymeacoffee.com/svcB4UR) or a [Kofi](https://ko-fi.com/arnicas).