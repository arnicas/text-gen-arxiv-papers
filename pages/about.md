---
layout: page
title: About
description: "How the searches work"
---

### How the Searches Work

There is limited functionality in the [ArXiv API](https://arxiv.org/help/api/), but it can do these.  But truly, thank you to ArXiv for use of its open access interoperability.

Note: Search strings are shown URL-encoded as they are used in the API calls.

**Active Categories:**

* **Story/Narrative:**
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"OR+abs:"plot%20generation"OR+abs:"story%20generation"OR+abs:"generated%20stories"%29+AND+%28abs:narrative+OR+abs:story+OR+abs:fiction+OR+abs:plot%29`

* **Games:**
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"%29+AND+%28abs:games+OR+abs:game%29`

* **Dialogue:**
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"+OR+abs:"generating%20dialogue"%29+AND+%28abs:dialogue+OR+abs:agents+OR+abs:conversation%29`

* **Poetry/Lyrics:**
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"+OR+abs:"generating%20poetry"%29+AND+%28abs:poetry+OR+abs:poems+OR+abs:lyrics%29`

* **Creativity:**
`%28abs:"LLM%20generation"+OR+abs:"text%20generation"+OR+abs:"LLM%20output"+OR+abs:"LM%20output"+OR+abs:"LM%20generation"+OR+abs:"language%20model%20generation"+OR+abs:"language%20model%20output"%29+AND+%28abs:creative+OR+abs:creativity+OR+abs:creatively+OR+abs:novel+OR+abs:novelty+OR+abs:originality+OR+abs:original+OR+abs:imagination+OR+abs:imaginative+OR+abs:diverse+OR+abs:diversity%29`

**Disabled Categories (no longer actively searched, but historical data preserved):**

* **Knowledge Graphs:**
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"NLG"+OR+abs:"generating%20text"%29+AND+%28abs:knowledge+OR+abs:graphs+OR+abs:semantics%29`

* **Table2Text:**
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"%29+AND+%28abs:tables+OR+abs:data+OR+abs:structured+OR+abs:table-to-text%29`

* **Image2Text:**
`%28abs:"text%20generation"+OR+abs:"natural%20language%20generation"+OR+abs:"generating%20text"+OR+abs:"generating%20captions"%29+AND+%28abs:images+OR+abs:image2text+OR+abs:description+OR+abs:image-to-text+OR+abs:caption%29`

Let me know if you think the searches could be better?

Jekyll isn't good at category indexing etc, so I ended up making a bunch of python scripts to build the pages I needed.  Right now it runs on my laptop a few times a week.  This site makes poor use of the [Hyde theme by Mark Otto](https://github.com/poole/hyde), but I'm grateful for it.

I'm [@arnicas](https://twitter.com/arnicas) (Lynn Cherny) and if you like this you could [buy me a 🍺 beer or ☕ coffee](https://www.buymeacoffee.com/svcB4UR) or a [Kofi](https://ko-fi.com/arnicas).