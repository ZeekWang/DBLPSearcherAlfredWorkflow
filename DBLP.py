# coding=utf8
#!/usr/bin/env python

#################################
#
# DBLP searcher for Alfred Wordflows
# Authors: Zeek Wang
#
#################################

import urllib
import urllib2
import json
import sys
import alfred
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

def item(title, sub_title = "", for_next = None, icon="icon.png"):
    for_next = for_next or title;
    return alfred.Item({"arg": for_next}, title, sub_title, icon);

def query_paper(query, for_bib=False):
    url = "http://dblp.uni-trier.de/search/publ/inc?q=" + urllib.quote(query);
    html = pq(urllib2.urlopen(url).read());
    article_eles = html(".article");
    output = [];

    for i in range(len(article_eles)):
        id = article_eles.eq(i).attr("id");
        title = article_eles.eq(i).find(".title").text();
        author_names = [];
        author_eles = article_eles.eq(i).find("span[itemprop=author]");
        for j in range(len(author_eles)):
            author_names.append(author_eles.eq(j).text());
        authors = ", ".join(author_names);
        if for_bib == True:
            output.append(item(title, authors, id));
        else:
            output.append(item(title, authors));
    xml = alfred.xml(output)
    return xml;


def query_bib(id):
    url = "http://dblp.uni-trier.de/rec/bibtex/" + id;
    html = pq(urllib2.urlopen(url).read());    
    elements = html("#bibtex-section .verbatim");
    bib_text = "";
    if len(elements) > 0:
        bib_text = elements.eq(0).text();
    return bib_text;

if __name__ == '__main__':
    query_paper("seam carving", True);
    # query_bib("conf/edbt/Sellam0KA16")