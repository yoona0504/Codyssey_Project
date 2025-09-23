#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import threading
from typing import Dict, Optional

HOST = '0.0.0.0'
PORT = 50000
ENCODING = 'utf-8'
RECV_BUF = 4096

clients: Dict[socket.socket, str] = {}
clients_lock = threading.Lock()


def broadcast(message: str, exclude_sock: Optional[socket.socket] = None) -> None:
    """모든 클라이언트에게 메시지 전송."""
    data = message.encode(ENCODING, errors='ignore')
    with clients_lock:
        targets = [s for s in clients.keys() if s is not exclude_sock]
    for sock in targets:
        try:
            sock.sendall(data)
        except OSError:
            remove_client(sock)


def send_private(target_name: str, message: str) -> bool:
    """특정 사용자에게 귓속말 전송. 성공 시 True."""
    data = message.encode(ENCODING, errors='ignore')
    with clients_lock:
        for sock, name in clients.items():
            if name == target_name:
                try:
                    sock.sendall(data)
                    return True
                except OSError:
                    remove_client(sock)
                    return False
    return False


def remove_client(sock: socket.socket) -> None:
    """클라이언트 제거 및 퇴장 안내."""
    with clients_lock:
        name = clients.pop(sock, None)
    if name:
        broadcast(f'[SYSTEM] {name}님이 퇴장하셨습니다.\n')
    try:
        sock.close()
    except OSError:
        pass


def handle_client(conn: socket.socket, addr) -> None:
    """각 클라이언트 전용 스레드."""
    try:
        nickname = conn.recv(RECV_BUF).decode(ENCODING, errors='ignore').strip()
        if not nickname:
            conn.close()
            return

        with clients_lock:
            if nickname in clients.values():
                conn.sendall('[SYSTEM] 중복된 닉네임 사용 불가.\n'.encode(ENCODING))
                conn.close()
                return
            clients[conn] = nickname

        broadcast(f'[SYSTEM] {nickname}님이 입장하셨습니다.\n')

        while True:
            data = conn.recv(RECV_BUF)
            if not data:
                break

            text = data.decode(ENCODING, errors='ignore').strip()
            if not text:
                continue

            if text == '/종료':
                break

            if text.startswith('/r ') or text.startswith('/귓속말 '):
                parts = text.split(maxsplit=2)
                if len(parts) < 3:
                    conn.sendall('[SYSTEM] 사용법: /r 닉 메시지\n'.encode(ENCODING))
                    continue
                _, target, msg = parts
                sender = clients.get(conn, 'Unknown')
                sent = send_private(target, f'(귓속말){sender}> {msg}\n')
                if sent:
                    conn.sendall(f'(귓속말)->{target}: {msg}\n'.encode(ENCODING))
                else:
                    conn.sendall('[SYSTEM] 대상 없음\n'.encode(ENCODING))
                continue

            sender = clients.get(conn, 'Unknown')
            broadcast(f'{sender}> {text}\n')

    except OSError:
        pass
    finally:
        remove_client(conn)


def main() -> None:
    print(f'[SYSTEM] Chat server starting on {HOST}:{PORT}')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print('[SYSTEM] Waiting for clients...')
        while True:
            conn, addr = srv.accept()
            th = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            th.start()


if __name__ == '__main__':
    main()
