# scrape information
import re
import nltk
import psycopg2
import requests
from delete_words import Delete_words


# from crawlweb.nature import nature_scrape
# from crawlweb.additive_manufacturing import additive_manufacturing
# from crawlweb.spectrum_ieee_computing import spectrum_ieee_computing_scrape
# from crawlweb.spectrum_ieee_biomedical import spectrum_ieee_biomedical_scrape
# from crawlweb.spectrum_ieee_energy import spectrum_ieee_energy_scrape
# from crawlweb.spectrum_ieee_robotics import spectrum_ieee_robotics_scrape
# from crawlweb.spectrum_ieee_semiconductors import spectrum_ieee_semiconductors_scrape
# from crawlweb.spectrum_ieee_telecom import spectrum_ieee_telecom_scrape
# from crawlweb.spectrum_ieee_transportation import spectrum_ieee_transportation_scrape
from crawlweb.threeders import threeders
# from crawlweb.materialstoday import materialstoday
# from crawlweb.popsci_health import popsci_health
# from crawlweb.popsci_science import popsci_science
# from crawlweb.popsci_technology import popsci_technology


# python 2 version:
# import sys
# sys.path.append('crawlweb')


def getResultList():
    # result_list = nature_scrape()
    # result_list = spectrum_ieee_computing_scrape()
    # result_list = spectrum_ieee_transportation_scrape()
    # result_list = spectrum_ieee_telecom_scrape()
    # result_list = spectrum_ieee_semiconductors_scrape()
    # result_list = spectrum_ieee_robotics_scrape()
    # result_list = spectrum_ieee_biomedical_scrape()
    # result_list = spectrum_ieee_energy_scrape()
    result_list = threeders()
    # result_list = additive_manufacturing()
    # result_list = materialstoday()
    # result_list = popsci_health()
    # result_list = popsci_science()
    # result_list = popsci_technology()
    return result_list


def get_words(url):
    words = requests.get(url).content.decode('latin-1')  # .encode('utf-8')
    word_list = words.split('\n')
    index = 0
    while index < len(word_list):
        word = word_list[index]
        if ';' in word or not word:
            word_list.pop(index)
        else:
            index += 1
    return word_list


def remove_words(text_string, delete_words=Delete_words):
    for word in delete_words:
        text_string = text_string.replace(word, ' ')  # .encode('utf-8')
    return text_string


def getAttitudeWordList(result_list):
    attitude_list = []
    p_url = 'http://ptrckprry.com/course/ssd/data/positive-words.txt'
    n_url = 'http://ptrckprry.com/course/ssd/data/negative-words.txt'
    positive_words = get_words(p_url)
    negative_words = get_words(n_url)
    for element in result_list:
        article_content = element[4]
        text_string = remove_words(article_content)
        content_text_tokens = nltk.word_tokenize(text_string)
        content_text = nltk.Text(content_text_tokens)
        content_text_nonPunct = re.compile('.*[A-Za-z].*')
        raw_words = [w for w in content_text if content_text_nonPunct.match(w)]
        cpos = 0
        cneg = 0
        for word in raw_words:
            if word in positive_words:
                cpos += 1
            if word in negative_words:
                cneg += 1
        if cpos == 0 and cneg == 0:
            attitude_list.append(0)
        elif cneg == 0:
            attitude_list.append(0.01)
        elif cpos == 0:
            attitude_list.append(-0.01)
        else:
            attitude_list.append(round(float(cpos) / cneg, 2))
    return attitude_list


def insert_record(result_list):
    # prepare input: list of tuples
    input_value = []
    attitude_list = getAttitudeWordList(result_list)
    for element, attitude in zip(result_list, attitude_list):
        input_value.append((element[0], element[1], element[2], element[3], element[4], attitude))
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO results(url,article_title,time,link,content,attitude)
             VALUES(%s,%s,%s,%s,%s,%s) RETURNING id;"""
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect("dbname=project user=postgres password=postgres")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        success = fail = 0
        for record in input_value:
            try:
                cur.execute(sql, record)
                conn.commit()
                success += 1
            except:
                conn.rollback()
                fail += 1
        # close communication with the database
        print('adding to database, success %d, fail %d' % (success, fail))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def main():
    result_list = getResultList()
    insert_record(result_list)


main()
