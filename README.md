> note: if this broke then please open an issue and lmk, i'll fix it (likely)

# google-search-scraper

tiny python thing that scrapes google search results, including ai overviews and videos  
fairly fast, no chromium work (except for cookies which you can get externally and it lasts 6 months \:D)

stop paying for serp services omg

## what all it can do

* get a google `NID` cookie (the only required cookie)
* scrape normal search results
* extract youtube video results
* detect AI Overview responses
* fetch the complete AI Overview result

## usage

```python
from gss import get_nid, get_results, get_ai

nid = get_nid(146)

for result in get_results("[test query]", nid):
    if result["type"] == "ai": print(get_ai(result["url"], nid))
    else: print(result)
```

## example outputs

```python
{
    "type": "normal",
    "title": "Wikipedia - Cat",
    "url": "https://en.wikipedia.org/wiki/Cat",
    "snippet": "The cat is a domestic species..."
}
```

```python
{
    "type": "video",
    "title": "cat compilation",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

```python
{
    "type": "ai",
    "title": "AI Overview",
    "url": "https://www.google.com/async/folsrch?..."
}
```

## functions

`get_nid(chrome_version=None, wait_s=3)`: launches a chrome and gets a `NID` cookie from google.

`get_results(query, nid)`: returns a list of search results. possible result types so far: `normal`, `video`, `ai`

`get_ai(url, nid, timeout=None)`: waits for completion and extracts the response from a google AI overview endpoint.

## notes

* relies on google's current HTML structure, may break some day
* i tried to be as general / less-fragile as possible though
* ai overview response formatting is ass
* dont try to use headless for getting the cookie, i tried it, it doesnt work, and because its headless, i cant know why it didnt work

## license

do whatever you want with it.
