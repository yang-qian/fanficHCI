# fanficHCI

This repo analyzes the [AO3](http://archiveofourown.org) fanfiction corpus.

### Usage

* ```ao3_fandom_ranker.ipynb```
    * ranks the fandoms (across AO3 categories e.g., movie, book, anime) by popularity (in terms of the number of fanfics)
* ```author_scraper.ipynb```
    * takes in stories of a fandom ```sampledata/ao3_harrypotter_text_stories.csv```
    * outputs a list of authors and a list of their pseudonyms ```sampleoutput/sampleoutput_authors.csv``` and ```sampleoutput/sampleoutput_authors.csv```


* FOLDER ```dataviz_character```
    * visualizes ```relationship_tsne_embed.csv``` with d3.js

### Task List

- [x] visualize relationship_tsne_embed.csv
- [ ] update fandom list
- [ ] join author bio and relationship_tsne_embed
- [ ] visualize author trajectory
- [ ] visualize protagonist embeddings, and protagonist-antagonist relationships 