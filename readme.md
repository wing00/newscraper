# newscraper

*   Scrapes Bing News via API for links and descriptions
* Processes links with readability and beautiful soup
* Stores onto a postgres and retrieves as csv or as tuple

Postgres layout

    articles 
    id          | integer               | id number 
    ticker      | character varying(10) | stock ticker
    link        | text                  | url for article
    title       | text                  | title
    description | text                  | bing's description
    content     | text                  | parsed content
    published   | date                  | published date
    
## usage
#### Scrape functions
- Scrape Bing 
>   python main.py
>>
- Scrape more links
> python main.py -s 300
>>

####Ticker Functions
- Get ticker, saves as a csv with ticker name
> python main.py AAPL  
AAPL.csv
>>
- Buffer only (returns tuple)
> python main.py AAPL -b



####Init
-create tables
> python main.py --init
>>
