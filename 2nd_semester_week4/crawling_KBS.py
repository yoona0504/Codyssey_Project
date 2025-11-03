# crawling_KBS.py
# -*- coding: utf-8 -*-
"""
Naver crawling assignment script.

Features
- Compare content when logged out vs. logged in.
- Preselected login-only content: Naver Mail inbox subjects.
- Selenium is required (install separately), no 3rd-party libs besides 'requests' and 'selenium'.
- Saves results to Python lists and prints them.
- PEP 8 style, single quotes for strings by default.
"""

import os
import sys
import time
import argparse
import getpass
import unicodedata
import re
from typing import List

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


NAVER_HOME = 'https://www.naver.com/'
NAVER_LOGIN = 'https://nid.naver.com/nidlogin.login'
NAVER_MAIL = 'https://mail.naver.com/'

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
)


def clean_space(text: str) -> str:
    return ' '.join(text.split()).strip()


def normalize_title(s: str) -> str:
    """메일 제목 텍스트 정규화: 유니코드/공백/접두사 제거."""
    if not s:
        return ''
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('\u200b', '').replace('\u200c', '').replace('\ufeff', '')
    s = s.replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    # 화면 리더용/접근성 접두 제거 (필요시 확장)
    s = re.sub(r'^(메일\s*제목\s*:?\s*)', '', s, flags=re.IGNORECASE)
    return s


def make_driver(browser: str = 'chrome', headless: bool = False) -> webdriver.Remote:
    browser = browser.lower()
    if browser not in {'chrome', 'edge'}:
        raise ValueError('browser must be one of: chrome, edge')

    if browser == 'chrome':
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.chrome.service import Service as ChromeService

        options = ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1280,1600')
        options.add_argument(f'user-agent={USER_AGENT}')
        service = ChromeService()  # chromedriver는 PATH에 있어야 합니다.
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService

    options = EdgeOptions()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1280,1600')
    options.add_argument(f'user-agent={USER_AGENT}')
    service = EdgeService()  # msedgedriver는 PATH에 있어야 합니다.
    driver = webdriver.Edge(service=service, options=options)
    return driver


def get_public_home_snippets(driver: webdriver.Remote, limit: int = 15) -> List[str]:
    driver.get(NAVER_HOME)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(1.0)

    candidates: List[str] = []
    seen = set()

    def add_item(text: str) -> None:
        t = clean_space(text)
        key = t.lower()
        if t and key not in seen:
            seen.add(key)
            candidates.append(t)

    selectors = [
        'a.nav',
        'a.link_news',
        'strong.title',
        'a.media_end_head_headline',
        'a.cluster_text_headline',
        'a.link_issue',
        'a.itm',
        'a[href*="news.naver.com"]',
    ]

    for css in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, css)
        for el in elements:
            text = clean_space(el.text or '')
            if len(text) >= 6:
                add_item(text)
                if len(candidates) >= limit:
                    return candidates

    anchors = driver.find_elements(By.TAG_NAME, 'a')
    for a in anchors:
        text = clean_space(a.text or '')
        if len(text) >= 8:
            add_item(text)
            if len(candidates) >= limit:
                break
    return candidates[:limit]


def login_naver(driver: webdriver.Remote, user_id: str, user_pw: str) -> None:
    driver.get(NAVER_LOGIN)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    auto_ok = True
    try:
        id_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'id')))
        pw_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'pw')))
        id_input.clear()
        id_input.send_keys(user_id)
        pw_input.clear()
        pw_input.send_keys(user_pw)
        pw_input.send_keys(Keys.ENTER)
    except TimeoutException:
        auto_ok = False

    if auto_ok:
        try:
            # 로그인 처리 후 리다이렉트/세션 유효성 확인
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.url_contains('mail.naver.com'),
                    EC.url_contains('www.naver.com'),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="mail.naver.com"]'))
                )
            )
            if 'www.naver.com' not in driver.current_url:
                driver.get(NAVER_HOME)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        except TimeoutException:
            auto_ok = False

    if not auto_ok:
        sys.stdout.write(
            '\n[안내] 자동 로그인 실패 또는 추가 인증 필요.\n'
            '브라우저에서 로그인 후, 터미널에 ENTER를 누르세요... '
        )
        sys.stdout.flush()
        try:
            input()
        except KeyboardInterrupt:
            raise SystemExit('사용자 중단')
        driver.get(NAVER_HOME)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))


def get_mail_subjects(driver: webdriver.Remote, limit: int = 20) -> List[str]:
    """중복 제거/정규화 적용된 메일 제목 수집."""
    driver.get(NAVER_MAIL)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(1.0)

    subjects: List[str] = []
    seen = set()

    def add_unique(raw: str) -> None:
        t = normalize_title(raw)
        key = t.lower()
        if t and key not in seen:
            seen.add(key)
            subjects.append(t)

    # 1) 우선 셀렉터 (신 UI에서 비교적 안정적)
    primary = 'div.mail_title a.mail_title_link span.text, a.mail_title_link > span'
    elems = driver.find_elements(By.CSS_SELECTOR, primary)
    for el in elems:
        add_unique(el.text)
        if len(subjects) >= limit:
            return subjects[:limit]

    # 2) 스크롤 한 번 → 추가 로딩 유도
    if len(subjects) < limit:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(0.8)
        elems = driver.find_elements(By.CSS_SELECTOR, primary)
        for el in elems:
            add_unique(el.text)
            if len(subjects) >= limit:
                return subjects[:limit]

    # 3) 보조 셀렉터 (구/대체 레이아웃)
    if len(subjects) < limit:
        backups = [
            'strong.mail_title',
            'a.subject',
            'div.subject strong',
            'span.mail_title',
            'div.mTitle > strong',
        ]
        for css in backups:
            for el in driver.find_elements(By.CSS_SELECTOR, css):
                add_unique(el.text)
                if len(subjects) >= limit:
                    return subjects[:limit]

    return subjects[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description='Naver crawling (public vs. logged-in mail).')
    parser.add_argument('--max', type=int, default=15)
    parser.add_argument('--browser', type=str, default='chrome')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--id', dest='user_id', type=str, default=os.environ.get('NAVER_ID', ''))
    parser.add_argument('--pw', dest='user_pw', type=str, default=os.environ.get('NAVER_PW', ''))
    args = parser.parse_args()

    if not args.user_id:
        args.user_id = input('Naver ID: ').strip()
    if not args.user_pw:
        args.user_pw = getpass.getpass('Naver Password: ').strip()

    driver = make_driver(browser=args.browser, headless=args.headless)
    driver.implicitly_wait(2)

    public_items: List[str] = []
    mail_subjects: List[str] = []

    try:
        # 1) 비로그인 공개 스니펫
        public_items = get_public_home_snippets(driver, limit=args.max)
        # 2) 로그인
        login_naver(driver, user_id=args.user_id, user_pw=args.user_pw)
        # 3) 로그인 전용: 메일 제목
        mail_subjects = get_mail_subjects(driver, limit=args.max)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    print('[비로그인 상태: 네이버 메인 콘텐츠 스니펫]')
    if public_items:
        for i, line in enumerate(public_items, 1):
            print(f'{i:02d}. {line}')
    else:
        print('수집된 공개 항목이 없습니다.')

    print('\n[로그인 상태 전용: 네이버 메일 제목 목록]')
    if mail_subjects:
        for i, subj in enumerate(mail_subjects, 1):
            print(f'{i:02d}. {subj}')
    else:
        print('메일 제목을 찾지 못했습니다.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n사용자 중단', file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f'오류: {exc}', file=sys.stderr)
        sys.exit(1)
