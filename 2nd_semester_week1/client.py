#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import threading

HOST = '127.0.0.1'
PORT = 50000
ENCODING = 'utf-8'
RECV_BUF = 4096


def recv_loop(sock: socket.socket) -> None:
    """서버 메시지 수신/출력."""
    try:
        while True:
            data = sock.recv(RECV_BUF)
            if not data:
                break
            print(data.decode(ENCODING, errors='ignore'), end='')
    except OSError:
        pass


def send_loop(sock: socket.socket) -> None:
    """사용자 입력 송신."""
    try:
        while True:
            msg = input()
            sock.sendall((msg + '\n').encode(ENCODING))
            if msg.strip() == '/종료':
                break
    except OSError:
        pass


def main() -> None:
    nickname = input('닉네임: ').strip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall((nickname + '\n').encode(ENCODING))

        t_recv = threading.Thread(target=recv_loop, args=(sock,), daemon=True)
        t_recv.start()

        send_loop(sock)
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass


if __name__ == '__main__':
    main()
