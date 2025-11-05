#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from ipaddress import ip_address
from pathlib import Path
import json
import urllib.request

PORT = 8080
INDEX_FILE = Path('index.html')
BONUS_ENABLE = True


def is_private_ip(addr: str) -> bool:
    try:
        ip = ip_address(addr)
    except ValueError:
        return True
    return ip.is_private or ip.is_loopback or ip.is_link_local


def geolocate_ip(addr: str, timeout: float = 2.5) -> dict:
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
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0] if self.client_address else 'unknown'
        print(f'[ACCESS] time={now} ip={client_ip}', flush=True)
        if BONUS_ENABLE:
            info = geolocate_ip(client_ip)
            if info:
                where = f"{info.get('country')}, {info.get('region')}, {info.get('city')}"
                coords = f"({info.get('lat')}, {info.get('lon')})"
                print(f'         geo={where} {coords}', flush=True)

    def do_GET(self) -> None:  # noqa: N802
        self.log_request_info()

        if not INDEX_FILE.exists():
            self.send_error(404, 'index.html not found')
            return
        try:
            content = INDEX_FILE.read_bytes()
        except OSError:
            self.send_error(500, 'failed to read index.html')
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args) -> None:
        return


def run_server() -> None:
    httpd = HTTPServer(('', PORT), SpacePirateHandler)
    print(f'Serving on http://127.0.0.1:{PORT} (Ctrl+C to quit)')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run_server()
