import requests
from bs4 import BeautifulSoup


def fetch_html(url: str) -> str:
    '''URL에서 HTML 소스를 가져온다.'''
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/119.0 Safari/537.36'
        )
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or 'utf-8'
    return resp.text


def get_headlines(html_text: str) -> list[str]:
    '''
    BeautifulSoup으로 헤드라인 텍스트를 추출한다.

    1차: kbs 기준 고유 셀렉터
         a.in-news.box-content p.title
    2차: 혹시 구조가 조금 바뀌면 대비한 안전한 폴백 셀렉터들
    '''
    soup = BeautifulSoup(html_text, 'html.parser')
    headlines: list[str] = []

    selectors = [
        'a.in-news.box-content p.title',
        # 폴백(구조 변화 대비)
        'div.main-news-wrapper a.in-news.box-content p.title',
        'div.box-contents a.in-news.box-content p.title',
        # 아주 보수적 폴백(노이즈 조금 가능)
        'a[href*="/news/"] p.title',
        'a[href*="/news/"]',
    ]

    seen: set[str] = set()
    for sel in selectors:
        for node in soup.select(sel):
            text = node.get_text(strip=True)
            if not text:
                continue
            # 너무 짧은/잡링크 필터
            if len(text) < 6:
                continue
            if text in seen:
                continue
            seen.add(text)
            headlines.append(text)

        if headlines:
            break  # 1차 셀렉터로 충분히 뽑히면 종료

    return headlines


def main() -> None:
    url = 'https://news.kbs.co.kr'
    html_text = fetch_html(url)
    headlines = get_headlines(html_text)

    #  List 객체를 화면에 출력
    print(headlines)

    # 가독성용 번호 목록도 함께 출력
    print('\n[KBS 주요 헤드라인]')
    for idx, title in enumerate(headlines, 1):
        print(f'{idx:02d}. {title}')


if __name__ == '__main__':
    main()
