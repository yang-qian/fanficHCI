# fanficHCI

This repo analyzes an [AO3](http://archiveofourown.org) fanfiction corpus.

### Usage

* ```ao3_fandom_ranker.ipynb```
    * ranks the fandoms (across AO3 categories e.g., movie, book, anime) by popularity (in terms of the number of fanfics)
* ```find_author_of_stories.py```
    * takes in fanfic stories ```ao3_harrypotter/text_stories.csv```
    * profiles the authors and their pseudonyms ```stories_authors.csv ``` and ```stories_pseudos.csv```

* FOLDER ```dataviz_character```
    * visualizes ```relationship_tsne_embed.csv``` with d3.js

### Task List

- [x] visualize relationship_tsne_embed.csv
- [ ] update fandom list
- [ ] join author bio and relationship_tsne_embed
- [ ] visualize author trajectory
- [ ] visualize protagonist embeddings, and protagonist-antagonist relationships 