import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime

def get_page_links(url):
    # gets links to each individual currency page
    baseurl = 'https://ca.finance.yahoo.com/'
    r = requests.get(url)
    sp = bs(r.text, 'html.parser')
    links = sp.select('td a[data-test=quoteLink]')
    return [baseurl + link.attrs['href'] for link in links]

print(get_page_links('https://ca.finance.yahoo.com/currencies/'))

def currency_page_data(url):
    # PROBLEM currencies page is not allowing scraping
    # gets bid/ask/dayRange data from each individual currency page and stores in dictionary obj
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/107.0.0.0 Safari/537.36"}
    r = requests.get(url,headers=headers)
    sp = bs(r.text, 'html.parser')

    currency = {
        'bid': sp.find('td', {'data-test':'BID-value'}).text,     # find() has same function as select_one css selector
        'ask': sp.find('td', {'data-test':'ASK-value'}).text,
        'dayRange': sp.find('td', {'data-test':'DAYS_RANGE-value'}).text
    }

    return currency

def main():
    url = 'https://ca.finance.yahoo.com/currencies/'
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')

    bids = []             # within href
    asks = []             # within href
    dayRanges = []            # within href

    for href in get_page_links(url):
        bids.append(currency_page_data(href)['bid'])
        asks.append(currency_page_data(href)['ask'])
        dayRanges.append(currency_page_data(href)['dayRange'])

    # soup objects of strings
    name_soup = soup.select('td[aria-label=Name]')
    last_price_soup = soup.select('td[aria-label="Last Price"]')
    change_soup = soup.select('td[aria-label="% Change"] span')

    def get_text_list(sp):
        for el in range(len(sp)):
            sp[el] = sp[el].text
        return list(sp)

    # make soup objects into lists
    names = get_text_list(name_soup)
    lastPrices = get_text_list(last_price_soup)
    changesPerc = get_text_list(change_soup)

    # pass in lists into dataframe
    df = pd.DataFrame({'Curr Name':names, 'Last Price':lastPrices, '% Change':changesPerc,
                       'bid':bids, 'ask':asks, 'Day Range':dayRanges})
    today = datetime.date.today()
    print("Currencies have been scraped")
    return df.to_csv(f'yahoo_curr_scraped_{today}.csv', index=False, encoding='utf-8')

main()
