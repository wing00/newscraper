# newscraper

*   Scrapes Bing News via API for links and descriptions
* Processes links with readability and beautiful soup
* Stores onto a postgres and retrieves as csv or as tuple

Postgres layout

    articles <br />
    id          | integer               | id number 
    ticker      | character varying(10) | stock ticker
    link        | text                  | url for article
    title       | text                  | title
    description | text                  | bing's description
    content     | text                  | parsed content>
    published   | date                  | published date