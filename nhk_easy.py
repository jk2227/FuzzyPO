# This Python file uses the following encoding: utf-8
# encoding: utf-8

import requests
import json
import codecs
import re
from Article import Article

def read_text_from_web():

    news_root_url = 'http://www3.nhk.or.jp/news/easy/'

    f = codecs.open('Text/nhk_easy.txt', 'r', 'utf-8')
    old_news = {}
    old_news_ids = []
    line_match = re.compile(r'(k\d{14})\s{4}(.*)\n')
    for line in f:
        match = line_match.match(line)
        if match:
            old_news[match.group(1)] = match.group(2)
            old_news_ids.append(match.group(1))
    f.close()

    f = codecs.open('Text/nhk_easy.txt','w','utf-8')

    for news_id in old_news_ids:
        text = old_news[news_id]
        f.write(news_id + u'    ' + text + '\n')

    news_list_url = news_root_url + 'news-list.json'
    #news_list_url = 'http://web.archive.org/web/20160408041240/http://www3.nhk.or.jp/news/easy/news-list.json'
    #news_list_url = 'http://web.archive.org/web/20160515062441/http://www3.nhk.or.jp/news/easy/news-list.json'
    news_list_json = requests.get(news_list_url).text
    #print news_list_json
    all_list = json.loads(news_list_json)[0]
    all_dates = sorted(all_list.keys())
    for date in all_dates:
        date_list = all_list[date]
        for news in date_list:
            news_id = news["news_id"]
            if old_news.has_key(news_id):
                continue
            title = news["title"]
            try:
                text = json.loads(requests.get(news_root_url + news_id + '/' + news_id + '.out.json').text)["text"]
            except:
                f.write(news_id + u'    ERROR\n')
                print news_id, 'error'
            else:
                text.replace('\n',' ')
                f.write(news_id + u'    ' + text + '\n')
                print news_id, 'OK'
    f.close()


def convert_text_to_articles(fn='Text/nhk_easy.txt', if_article=True, if_para=True, if_sentence=True):

    #old_articles = read_articles()
    old_articles = {}

    f = open(fn)
    articles = {}
    line_match = re.compile(r'(k\d{14})\s{4}(.*)\n')
    for line in f:
        match = line_match.match(line)
        if match:
            news_id = match.group(1)
            text = match.group(2)
            if if_article:
                articles[news_id] = Article(news_id, text)
            if not if_para:
                continue
            paras = re.split(' ', text)
            for pid in xrange(1, len(paras)):
                news_para_id = news_id + '_para' + str(pid)
                if len(paras[pid].strip()) > 0:
                    articles[news_para_id] = Article(news_para_id, paras[pid].strip())
                    # print news_para_id, paras[pid]
                    if not if_sentence:
                        continue
                    sentences = re.split('。', paras[pid].strip())
                    # if only one sentence in this paragraph
                    if len(sentences) <= 1 or (len(sentences) == 2 and len(sentences[1].strip()) == 0):
                        #print paras[pid].strip()
                        continue
                    for sid in xrange(len(sentences)):
                        news_para_sentence_id = news_para_id + '_s' + str(sid + 1)
                        if (len(sentences[sid].strip())) > 0:
                            # TODO: May encounter problems when last character is not '。'
                            articles[news_para_sentence_id] = Article(news_para_sentence_id,
                                                                      sentences[sid].strip() + '。')
                            # print news_para_sentence_id, sentences[sid].strip()
        else:
            print "ERROR in Article JSON: ", line

    ##############################################
    # Keep old_articles, combine them into new one
    for doc_id in old_articles.keys():
        if not articles.has_key(doc_id):
            articles[doc_id] = old_articles[doc_id]
    ##############################################

    f = codecs.open('Text/nhk_easy_articles.txt','w','utf-8')

    for article in articles.values():
        f.write(json.dumps(article.__dict__)+'\n')
    f.close()

def read_article_list(): # Keep the order
    try:
        f = open('Text/nhk_easy_articles.txt')
    except:
        return {}
    article_list = []
    for line in f:
        article_list.append(json.loads(line[:-1], object_hook=
                        lambda s:Article(s["doc_id"], s["text"], s["wordlist"], s["uniq_wordlist"])))
    return article_list

def read_articles(): # Order might be different in different OS
    article_list = read_article_list()
    articles = {a.doc_id:a for a in article_list}
    return articles

####################################################################################################################

#read_text_from_web()
#convert_text_to_articles()


#
#articles = read_articles()
