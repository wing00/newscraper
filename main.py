import argparse
import configparser
import requests
import lxml
from bs4 import BeautifulSoup
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
    """ for command line reading

    :rtype: ArgumentParser object
    :return: arguments

    """
    parser = argparse.ArgumentParser(description='Search Bing for News')
    parser.add_argument('ticker', nargs='?', help='tickers')
    parser.add_argument('--count', nargs='?', default=10)
    return parser.parse_args()


def ticker_validation():
    """ Validates stock ticker symbols

    :rtype: boolean
    """
    pass


def get_json(ticker):
    """uses bing API to pull news links

    :param ticker: (string) ticker symbol
    :rtype: json object
    :return: json response
    """

    response = requests.get('https://api.cognitive.microsoft.com/bing/v5.0/news/search',
                            headers={'Ocp-Apim-Subscription-Key': settings.get('API Keys', 'Microsoft')},
                            params={'q': ticker,
                                    'count': args.count}
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
    :return:
    """
    descriptions, urls = zip(*[(query['description'], query['url']) for query in search_json['value']])
    return descriptions, urls


def parse_website(url):
    response = requests.get(url,
                            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                            )
    soup = BeautifulSoup(response.text, "lxml")

    for junk in soup(["script", "style"]):
        junk.decompose()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))      # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    print(text)


if __name__ == '__main__':
    settings = config()
    args = parse_args()

    data = get_json('AAPL')
    descrip, links = get_links(data)

    parse_website(links[0])

