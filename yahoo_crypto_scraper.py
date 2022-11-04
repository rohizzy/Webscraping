import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime
import time
import re
from itertools import chain
import sys

def get_page_links(url):
    # gets links to each individual currency page
    baseurl = 'https://ca.finance.yahoo.com'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/107.0.0.0 Safari/537.36"}
    r = requests.get(url, headers=headers)
    sp = bs(r.text, 'html.parser')

    # if error found, program stops
    if re.search('2\d\d',str(r.status_code)):
        print('get_page_links HTTP STATUS: ', r.status_code, 'WORKS!')
    else:
        sys.exit('get_page_links HTTP STATUS: ' + str(r.status_code) + ' Failed!')

    links = sp.select('td a[data-test=quoteLink]')
    return [baseurl + link.attrs['href'] for link in links]

# print(get_page_links('https://ca.finance.yahoo.com/crypto?count=25&offset=0'))

def currency_page_data(url):
    # PROBLEM currencies page is not allowing scraping
    # gets bid/ask/dayRange data from each individual currency page and stores in dictionary obj
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
    r = requests.get(url,headers=headers)
    sp = bs(r.text, 'html.parser')

    # if error found, program stops... No success message because this fxn executes constantly
    if not re.search('2\d\d',str(r.status_code)):
        sys.exit('currency_page_data HTTP STATUS: ' + str(r.status_code) + ' Failed!')

    currency = {
        'prevClose': sp.find('td', {'data-test':'PREV_CLOSE-value'}).text,     # find() has same function as select_one css selector
        'open': sp.find('td', {'data-test':'OPEN-value'}).text,
        'yearRange': sp.find('td', {'data-test':'FIFTY_TWO_WK_RANGE-value'}).text
    }
    return currency

def main():
    start = time.time()

    # initialise soup
    url = 'https://ca.finance.yahoo.com/crypto?count=25&offset=0'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/107.0.0.0 Safari/537.36"}
    r = requests.get(url, headers=headers)
    soup = bs(r.text, 'html.parser')

    # if error found, program stops
    # if re.search('2\d\d',str(r.status_code)):
    #     print('main HTTP STATUS: ', r.status_code, 'WORKS!')
    # else:
    #     sys.exit('main HTTP STATUS: ' + str(r.status_code) + ' Failed!')

    results = []            # output results, where each item is a dictionary of the page

    # Pagination (arbitrarily chose 2 pages to scrape through), looking for 9 characteristics per Cryptocurrency
    print('Starting Scrape')
    for x in range(1):

        prevCloses = []             # within href
        openPrices = []             # within href
        yearRanges = []            # within href

        # Lists of characteristics of each currency from each indiv href
        for href in get_page_links(url):
            prevCloses.append(currency_page_data(href)['prevClose'])
            openPrices.append(currency_page_data(href)['open'])
            yearRanges.append(currency_page_data(href)['yearRange'])

        print('prevCloses ', prevCloses)
        print('open ', openPrices)
        print('year ranges ', yearRanges)

        # soup objects of strings taken from main URL
        name_soup = soup.select('td[aria-label=Name]')
        ticker_soup = soup.select('td a[class="Fw(600) C($linkColor)"]')
        price_soup = soup.select('td fin_streamer[data-field=regularMarketPrice]')
        change_soup = soup.select('td[aria-label="% Change"] span')
        mktCap_soup = soup.select('td fin_streamer[data-field=marketCap]')
        circSupp_soup = soup.select('td[aria-label="Circulating Supply"]')

        # def get_text_list(sp):
        #     for el in range(len(sp)):
        #         if sp == name_soup:
        #             sp[el] = sp[el].text.split(' ')[0]    # "Bitcoin CAD" becomes "Bitcoin"
        #         elif sp == ticker_soup:
        #             sp[el] = sp[el].text.split('-')[0]    # "BTC-CAD" becomes "BTC"
        #
        #         sp[el] = sp[el].text
        #     return list(sp)

        def get_text_list(sp):
            for el in range(len(sp)):
                sp[el] = sp[el].text
            return list(sp)

        # make soup objects into lists
        names = get_text_list(name_soup)
        tickers = get_text_list(ticker_soup)
        prices = get_text_list(price_soup)
        changesPerc = get_text_list(change_soup)
        mktCaps = get_text_list(mktCap_soup)
        circSupps = get_text_list(circSupp_soup)

        page = {'Curr Name':names, 'Ticker':tickers, 'Price':prices, '% Change':changesPerc,
                       'Market Cap':mktCaps, 'Circulating Supply':circSupps,
                       'Previous Close':prevCloses, 'Today Open':openPrices, '52 Week Range': yearRanges}
        results.append(page)
        print(f'Page {x+1} completed.')

    end = time.time()
    print('All pages completed in ', end-start)
    # print(results)
    return results

print(main())
df = pd.DataFrame(list(chain.from_iterable(main())))
# print(df)
today = datetime.date.today()
df.to_csv(f'Yahoo_crypto_scraped_{today}.csv', index=False, encoding='utf-8')