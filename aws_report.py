import psycopg2
import re
import nltk
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter
import operator
from delete_words import Delete_words

from dee import production_word
from jing import jing_word
from ying import ying_word


# query data from database
def get_records():
    """ query data from the results table """
    data_records = []
    conn = None
    try:
        conn = psycopg2.connect("dbname=project user=postgres password=postgres")
        cur = conn.cursor()
        cur.execute(
            "SELECT article_title,link,attitude,content FROM results where time>CURRENT_DATE-INTERVAL'1 month'")  # records within recent MONTH
        row = cur.fetchone()

        while row is not None:
            data_records.append(row)
            row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return data_records


def remove_words(text_string, delete_words=Delete_words):
    for word in delete_words:
        text_string = text_string.replace(word, '')  # .encode('utf-8')
    return text_string


def getWordsList(text):
    text_string = remove_words(text)
    content_text_tokens = nltk.word_tokenize(text_string)
    content_text = nltk.Text(content_text_tokens)
    content_text_nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in content_text if content_text_nonPunct.match(w)]
    no_stop_words = [w.lower() for w in raw_words if w.lower() not in list(stopwords.words('english'))]
    # one word
    one_word_count = Counter(no_stop_words)
    one_dict = {}
    for x, z in one_word_count.items():
        one_dict[''.join(x)] = z
    # two words
    bigrams = ngrams(no_stop_words, 2)
    two_word_count = Counter(bigrams)
    two_dict = {}
    for x, z in two_word_count.items():
        two_dict[''.join(x)] = z
    # three words
    trigrams = ngrams(no_stop_words, 3)
    three_word_count = Counter(trigrams)
    three_dict = {}
    for s, t in three_word_count.items():
        three_dict[''.join(s)] = t
    total_dict = dict(Counter(one_dict) + Counter(two_dict) + Counter(three_dict))
    words_list = sorted(total_dict.items(), key=operator.itemgetter(1), reverse=True)
    return words_list


def getNewResults(results):
    new_results = []
    # filter keyword and calculate production tendency
    keyword_list = jing_word + ying_word
    for result in results:
        words_list = getWordsList(result[3])
        frequent_word_list = []
        production_word_list = []
        production_score = 0
        for x in words_list:
            if x[0] in keyword_list:
                frequent_word_list.append(x)
            if x[0] in production_word:
                production_word_list.append(x)
                production_score += x[1]
        production_word_list.append(production_score)
        if frequent_word_list:
            if len(frequent_word_list) < 10:
                word_list = []
                for element in frequent_word_list:
                    word_list.append(element[0])
                num = 10 - len(frequent_word_list)
                for w in words_list:
                    if w[0] not in word_list:
                        frequent_word_list.append(w)
                    num -= 1
                    if num == 0:
                        break
            new_results.append([result[0], result[1], result[2], frequent_word_list, production_word_list])
    return new_results


def getPDF(result):
    # render html
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("myreport2.html")
    template_vars = {"results": result}
    html_out = template.render(template_vars)
    # generate pdf
    HTML(string=html_out).write_pdf("report.pdf", stylesheets=["typography.css"])


def main():
    results = get_records()
    new_results = getNewResults(results)
    getPDF(new_results)


main()
