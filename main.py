import argparse
import configparser
import json
import csv
import requests
import psycopg2
from readability import Document
from bs4 import BeautifulSoup
from multiprocessing import Pool


""" News Scraper
Scott Young AILabs.co
"""


def config():
    """
    Reads settings.ini for API Keys and other stuff (later?)

    :rtype: RawConfigParser object
    :return: configuration settings

    """
    configuration = configparser.RawConfigParser()
    configuration.read('settings.ini')
    return configuration


def parse_args():
    """
    Reads
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scrape', nargs='?', type=int, default=200, help='scrapes bing. add int value to change from default (200)')
    parser.add_argument('--init', action='store_true', help='initializes tables in postgres')
    parser.add_argument('ticker', nargs='?', help='returns all matches for ticker')
    parser.add_argument('-b', '--buffer', action='store_false', help='dumps results to buffer')

    return parser.parse_args()


def postgres():
    """
    Connect to server
    :return: connect object
    """
    conn = psycopg2.connect(dbname=settings.get('SQL', 'dbname'),
                            user=settings.get('SQL', 'user'),
                            password=settings.get('SQL', 'password'),
                            host=settings.get('SQL', 'host'),
                            port=settings.get('SQL', 'port'))

    return conn


def get_json(ticker, count):
    """uses bing API to pull news links

    :param ticker: (string) ticker symbol
    :param count: (int) number of articles to search for
    :rtype: json object
    :return: json response from bing
    """

    response = requests.get('https://api.cognitive.microsoft.com/bing/v5.0/news/search',
                            headers={'Ocp-Apim-Subscription-Key': settings.get('API', 'Microsoft')},
                            params={'q': ticker,
                                    'count': count}
                            )

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()


def get_links(search_json):
    """
    Filters out json for links and descriptions

    :param search_json: json
    :rtype: (list, list)
    :return: lists of all descriptions and urls
    """
    descriptions, urls, published = zip(*((query['description'], query['url'], query['datePublished']) for query in search_json['value']))
    return descriptions, urls, published


def parse_website(url):
    """
    Runs readability-lxml to extract text and soup to clean up

    :param url: (string) url for website to parse
    :return: title and summary of article
    :rtype: (string, string)
    """

    response = requests.get(
                     url,
                     headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'},  # sneaky like a ninja
                     )

    if response.status_code == requests.codes.ok:
        doc = Document(response.text)
        soup = BeautifulSoup(doc.summary(), 'lxml')
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        summary = '\n'.join(line for line in lines if line)

        return doc.title(), summary
    else:
        return None, None


def create_tables():
    connect = postgres()
    cur = connect.cursor()
    cur.execute("""CREATE TABLE articles(
      id          SERIAL      PRIMARY KEY,
      ticker      VARCHAR(10) NULL,
      link        TEXT        NULL,
      title       TEXT        NULL,
      description TEXT        NULL,
      content     TEXT        NULL,
      published   TIMESTAMP   NULL
      )
      ;
    """)
    connect.commit()
    connect.close()


def save_data(datas):
    """
    Saves data from scrape to postgres

    :param datas: list of tuples
    :return:
    """
    connect = postgres()
    cur = connect.cursor()
    for data in datas:
        query = """INSERT INTO articles
      VALUES (DEFAULT, %(ticker)s, %(link)s, %(description)s, %(content)s, %(published)s)
      ;
      """
        cur.execute(query, dict(zip(['ticker', 'link', 'title', 'description', 'content', 'published'], data)))

    connect.commit()
    connect.close()
    print('saved {}'.format(datas[0][0]))


def get_data(ticker, save_csv=True):
    """
    postgres query for a given ticker
    :param ticker: ticker symbol
    :param save_csv: boolean for csv
    :return:
    """
    connect = postgres()
    cur = connect.cursor()
    query = """SELECT * FROM articles WHERE ticker = %(ticker)s;"""
    cur.execute(query, {'ticker': ticker})
    fetches = cur.fetchall()
    connect.close()

    if save_csv:
        with open(ticker + '.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',')
            for fetch in fetches:
                writer.writerow(fetch)
    else:
        print(fetches)


def scrape_bing(count):
    """
    Scrapes Bing News for articles
    :return:
    """
    with open('tickers.json') as f:
        tickers = json.load(f)

    pool = Pool()

    for ticker, company in tickers:
        jsons = get_json(ticker, count)
        descriptions, links, published = get_links(jsons)

       \
        content = pool.map(parse_website, links)
        titles, summaries = zip(*content)

        # dummy to fill all tickers
        scraped = zip((ticker for _ in xrange(0, len(links))), links, titles, descriptions, summaries, published)
        save_data(scraped)


if __name__ == '__main__':
    settings = config()
    args = parse_args()

    if args.ticker:
        get_data(args.ticker, args.buffer)
    elif args.init:
        create_tables()
    elif args.scrape:
        scrape_bing(args.scrape)
