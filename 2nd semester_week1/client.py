#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
단순 TCP/IP 채팅 클라이언트.

기능
- 접속 즉시 닉네임 1회 전송.
- 송신/수신을 별도 스레드로 처리.
- '/종료' 입력 시 종료.
- 귓속말: '/w 대상닉 메시지' 또는 '/귓속말 대상닉 메시지'
"""

import socket
import threading

ENCODING = 'utf-8'
RECV_BUF = 4096


def recv_loop(sock: socket.socket) -> None:
    """서버로부터 수신한 메시지를 출력한다."""
    try:
        while True:
            data = sock.recv(RECV_BUF)
            if not data:
                print('[SYSTEM] 서버 연결이 종료되었습니다.')
                break
            print(data.decode(ENCODING), end='')
    except OSError:
        pass
    finally:
        try:
            sock.close()
        except OSError:
            pass


def send_loop(sock: socket.socket) -> None:
    """사용자 입력을 읽어 서버로 전송한다."""
    try:
        while True:
            try:
                line = input()
            except EOFError:
                line = '/종료'
            if not line:
                continue
            sock.sendall((line.strip() + '\n').encode(ENCODING))
            if line.strip() == '/종료':
                break
    except OSError:
        pass
    finally:
        try:
            sock.close()
        except OSError:
            pass


def main() -> None:
    """사용자로부터 접속 정보와 닉네임을 입력받아 서버와 통신한다."""
    host = input('서버 호스트(기본: 127.0.0.1): ').strip() or '127.0.0.1'
    port_text = input('서버 포트(기본: 50000): ').strip() or '50000'
    nickname = input('닉네임(공백/슬래시 금지, 최대 24자): ').strip()

    try:
        port = int(port_text)
    except ValueError:
        print('[SYSTEM] 포트는 숫자여야 합니다.')
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
        except OSError as exc:
            print(f'[SYSTEM] 서버 연결 실패: {exc}')
            return

        # 접속 직후 닉네임 1회 전송
        try:
            sock.sendall((nickname + '\n').encode(ENCODING))
        except OSError as exc:
            print(f'[SYSTEM] 닉네임 전송 실패: {exc}')
            return

        # 수신/송신 스레드 시작
        t_recv = threading.Thread(target=recv_loop, args=(sock,), daemon=True)
        t_recv.start()

        # 메인 스레드는 송신 담당
        send_loop(sock)

        # 종료 대기
        t_recv.join(timeout=1.0)


if __name__ == '__main__':
    main()
