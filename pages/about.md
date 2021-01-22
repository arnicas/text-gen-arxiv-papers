---
layout: page
title: About
description: "How the searches work"
---

### How the Searches Work

There is limited functionality in the [ArXiv API](https://arxiv.org/help/api/), but it can do these.  But truly, thank you to arXiv for use of its open access interoperability.

* API Search String for Story: 
`(abs: text generation OR abs: natural language generation) AND (abs: narrative OR abs: story OR abs: fiction OR abs: plot)`
* API Search String for Table2Text:
`(abs: text generation OR abs: natural language generation) AND (abs: tables OR abs: table-to-text OR abs: data OR abs: structured)`
* API Search String for Games:
`(abs: text generation OR abs: natural language generation) AND abs: games`
* API Search String for Knowledge:
`(abs: text generation OR abs: natural language generation) AND (abs: knowledge OR abs: graphs OR abs: semantics)`
* API Search String for Poetry:
`(abs: text generation OR abs: natural language generation) AND (abs: poetry OR abs: lyrics OR abs: poems)`
* API Search String for Dialogue:
`(abs: text generation OR abs: natural language generation) AND (abs: dialogue OR abs: agents OR abs: conversation)`
* API Search String for Image2Text:
`(abs: text generation OR abs: natural language generation) AND (abs: images OR abs: image2text OR abs: descripton OR abs: image to text)`


Jekyll isn't good at category indexing etc, so I ended up making a bunch of python scripts to build the pages I needed.  Right now it runs on my laptop a few times a week.  Let me know if you think the searches could be better?
