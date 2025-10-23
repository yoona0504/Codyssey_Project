# crawling_KBS.py
# -*- coding: utf-8 -*-

import re
import json
import sys
import requests
from bs4 import BeautifulSoup

KBS_URL = 'http://news.kbs.co.kr/'
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
)


def get_html(url):
    headers = {'User-Agent': USER_AGENT}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or 'utf-8'
    return r.text


def clean(text):
    return re.sub(r'\s+', ' ', text).strip()


def get_kbs_headlines(html, limit=15):
    soup = BeautifulSoup(html, 'html.parser')
    selectors = ['h1 a', 'h2 a', 'h3 a', 'a.headline', 'div.tit a', 'article a']
    headlines, seen = [], set()

    def add(text):
        t = clean(text)
        if len(t) > 8 and t not in seen:
            seen.add(t)
            headlines.append(t)

    for s in selectors:
        for a in soup.select(s):
            text = a.get_text(strip=True)
            href = a.get('href', '')
            if ('news' in href or 'ncd=' in href) and text:
                add(text)
            if len(headlines) >= limit:
                return headlines
    return headlines


def get_weather(loc='Seoul'):
    return clean(get_html(f'https://wttr.in/{loc}?format=3'))


def get_stock(symbol='AAPL'):
    url = 'https://query1.finance.yahoo.com/v7/finance/quote'
    r = requests.get(url, params={'symbols': symbol}, timeout=10)
    data = r.json()
    try:
        p = data['quoteResponse']['result'][0]['regularMarketPrice']
        return p
    except Exception:
        return None


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=15)
    p.add_argument('--weather', type=str, default='')
    p.add_argument('--stock', type=str, default='')
    args = p.parse_args()

    try:
        html = get_html(KBS_URL)
        headlines = get_kbs_headlines(html, args.limit)
        print('[KBS 헤드라인]')
        for i, h in enumerate(headlines, 1):
            print(f'{i:02d}. {h}')
    except Exception as e:
        print('KBS 크롤링 오류:', e, file=sys.stderr)

    if args.weather:
        print('\n[날씨]', get_weather(args.weather))
    if args.stock:
        p = get_stock(args.stock)
        print('\n[주가]', args.stock, p if p else '확인 불가')


if __name__ == '__main__':
    main()
