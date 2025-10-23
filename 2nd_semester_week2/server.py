#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from ipaddress import ip_address, IPv4Address, IPv6Address
from pathlib import Path
from typing import Tuple, Union
import json
import sys
import urllib.request


PORT: int = 8080
INDEX_FILE: Path = Path('index.html')

# 보너스 과제: IP → 위치 조회 사용 여부
BONUS_ENABLE: bool = True


def is_private_ip(addr: str) -> bool:
    """사설(내부) IP 여부를 반환한다."""
    try:
        ip = ip_address(addr)
    except ValueError:
        return True
    return ip.is_private or ip.is_loopback or ip.is_link_local


def geolocate_ip(addr: str, timeout: float = 2.5) -> dict:
    """
    표준 라이브러리(urllib)만으로 공개 API를 호출해 대략적인 위치를 조회한다.
    - 외부 서비스 품질/정책에 따라 실패할 수 있으므로 항상 예외를 삼킨다.
    - 사설/로컬 IP는 조회하지 않는다.
    """
    if is_private_ip(addr):
        return {}

    url = f'http://ip-api.com/json/{addr}?fields=status,message,country,regionName,city,lat,lon'
    req = urllib.request.Request(url, headers={'User-Agent': 'stdlib-client'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception:
        return {}

    if data.get('status') != 'success':
        return {}

    return {
        'country': data.get('country'),
        'region': data.get('regionName'),
        'city': data.get('city'),
        'lat': data.get('lat'),
        'lon': data.get('lon'),
    }


class SpacePirateHandler(BaseHTTPRequestHandler):
    server_version = 'SimpleHTTP/0.1'

    def log_request_info(self) -> None:
        """요청 수신 시 콘솔에 접속 시간과 클라이언트 IP, 위치(보너스)를 출력한다."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0] if self.client_address else 'unknown'

        print(f'[ACCESS] time={now} ip={client_ip}', flush=True)

        if BONUS_ENABLE:
            info = geolocate_ip(client_ip)
            if info:
                where = f"{info.get('country')}, {info.get('region')}, {info.get('city')}"
                coords = f"({info.get('lat')}, {info.get('lon')})"
                print(f'         geo={where} {coords}', flush=True)

    def send_index(self) -> None:
        """index.html을 읽어 200 OK로 전송한다. 없으면 404."""
        if not INDEX_FILE.exists():
            self.send_error(404, 'index.html not found')
            return

        try:
            content = INDEX_FILE.read_bytes()
        except OSError:
            self.send_error(500, 'failed to read index.html')
            return

        self.send_response(200)  # 헤더에 200 상태코드 명시
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler 규약)
        self.log_request_info()
        # 경로에 상관없이 index.html 제공
        self.send_index()

    # 불필요한 서버 로그(기본 access log)를 줄이고 과제 요구 로그만 남김
    def log_message(self, format: str, *args) -> None:
        return


def run_server() -> None:
    address: Tuple[str, int] = ('', PORT)
    httpd = HTTPServer(address, SpacePirateHandler)
    print(f'Serving on http://127.0.0.1:{PORT} (Ctrl+C to quit)')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run_server()
