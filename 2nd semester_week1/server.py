#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
멀티스레드 TCP/IP 채팅 서버.

요구사항
- 여러 클라이언트 동시 접속 처리 (threading).
- 접속 시 '~~님이 입장하셨습니다.' 전체 방송.
- '/종료' 입력 시 접속 종료.
- 일반 메시지는 '사용자> 메시지' 형태로 전체 방송.
- 보너스: 귓속말 기능 지원. ('/w 대상닉 메시지' 또는 '/귓속말 대상닉 메시지')

제약
- 표준 라이브러리만 사용.
- PEP 8 스타일 준수, 문자열은 기본적으로 단일 인용부호 사용.
"""

import socket
import threading
from typing import Dict, Tuple

HOST = '0.0.0.0'
PORT = 50000
ENCODING = 'utf-8'
RECV_BUF = 4096

# 소켓 -> (닉네임, 주소) 매핑
clients: Dict[socket.socket, Tuple[str, Tuple[str, int]]] = {}
clients_lock = threading.Lock()


def broadcast(message: str, exclude_sock: socket.socket | None = None) -> None:
    """모든 클라이언트에게 메시지를 전송한다."""
    with clients_lock:
        dead_socks: list[socket.socket] = []
        for sock in clients.keys():
            if exclude_sock is not None and sock is exclude_sock:
                continue
            try:
                sock.sendall(message.encode(ENCODING))
            except OSError:
                dead_socks.append(sock)
        for dead in dead_socks:
            _remove_client(dead)


def send_private(target_name: str, message: str, sender_sock: socket.socket) -> bool:
    """특정 닉네임을 가진 사용자에게만 메시지를 전송한다. 성공 여부 반환."""
    with clients_lock:
        for sock, (name, _) in clients.items():
            if name == target_name:
                try:
                    sock.sendall(message.encode(ENCODING))
                    return True
                except OSError:
                    _remove_client(sock)
                    return False
    return False


def _remove_client(sock: socket.socket) -> None:
    """클라이언트를 목록에서 제거하고 소켓을 닫는다."""
    try:
        name = clients[sock][0]
    except KeyError:
        name = ''
    clients.pop(sock, None)
    try:
        sock.close()
    except OSError:
        pass
    if name:
        notice = f'[SYSTEM] {name}님이 퇴장하셨습니다.\n'
        broadcast(notice)


def handle_client(conn: socket.socket, addr: Tuple[str, int]) -> None:
    """개별 클라이언트 스레드 함수."""
    try:
        # 1) 첫 메시지는 닉네임
        raw = conn.recv(RECV_BUF)
        if not raw:
            conn.close()
            return
        nickname = raw.decode(ENCODING).strip()
        if not _is_valid_name(nickname):
            conn.sendall('[SYSTEM] 닉네임이 유효하지 않습니다.\n'.encode(ENCODING))
            conn.close()
            return

        with clients_lock:
            # 닉네임 중복 방지
            if any(nickname == n for (n, _) in clients.values()):
                conn.sendall('[SYSTEM] 이미 사용 중인 닉네임입니다.\n'.encode(ENCODING))
                conn.close()
                return
            clients[conn] = (nickname, addr)

        # 입장 방송
        broadcast(f'[SYSTEM] {nickname}님이 입장하셨습니다.\n', exclude_sock=None)
        # 환영 메시지
        conn.sendall('[SYSTEM] 귓속말: /w 대상닉 메시지  또는  /귓속말 대상닉 메시지\n'.encode(ENCODING))
        conn.sendall('[SYSTEM] 종료: /종료\n'.encode(ENCODING))

        # 2) 메시지 루프
        while True:
            data = conn.recv(RECV_BUF)
            if not data:
                break
            text = data.decode(ENCODING).strip()
            if not text:
                continue

            if text == '/종료':
                conn.sendall('[SYSTEM] 연결을 종료합니다.\n'.encode(ENCODING))
                break

            # 귓속말 파싱: '/w 닉 메시지...' 또는 '/귓속말 닉 메시지...'
            if text.startswith('/w ') or text.startswith('/귓속말 '):
                parts = text.split(maxsplit=2)
                if len(parts) < 3:
                    conn.sendall('[SYSTEM] 사용법: /w 대상닉 메시지\n'.encode(ENCODING))
                    continue
                _, target, msg_body = parts
                sender = clients.get(conn, ('', addr))[0]
                formatted = f'(귓속말){sender}> {msg_body}\n'
                ok = send_private(target, formatted, conn)
                if ok:
                    # 보낸 사람에게도 확인용 출력
                    conn.sendall(f'(귓속말)->{target}: {msg_body}\n'.encode(ENCODING))
                else:
                    conn.sendall('[SYSTEM] 대상 사용자를 찾을 수 없습니다.\n'.encode(ENCODING))
                continue

            # 일반 방송
            sender = clients.get(conn, ('', addr))[0]
            broadcast(f'{sender}> {text}\n')

    except ConnectionResetError:
        # 클라이언트 비정상 종료
        pass
    except Exception as exc:
        try:
            conn.sendall(f'[SYSTEM] 서버 오류: {exc}\n'.encode(ENCODING))
        except OSError:
            pass
    finally:
        _remove_client(conn)


def _is_valid_name(name: str) -> bool:
    """닉네임 유효성 간단 점검."""
    if not name:
        return False
    if len(name) > 24:
        return False
    if any(ch.isspace() for ch in name):
        return False
    if name.startswith('/'):
        return False
    return True


def serve_forever() -> None:
    """메인 서버 루프."""
    print(f'[SYSTEM] Chat server starting on {HOST}:{PORT}')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        # 빠른 재시작을 위한 옵션
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print('[SYSTEM] Waiting for clients...')

        while True:
            conn, addr = srv.accept()
            th = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            th.start()


if __name__ == '__main__':
    serve_forever()
