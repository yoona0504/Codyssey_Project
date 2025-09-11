import socket
import threading

HOST = '127.0.0.1'
PORT = 50000
ENCODING = 'utf-8'
RECV_BUF = 4096


def recv_loop(sock):
    while True:
        try:
            data = sock.recv(RECV_BUF)
            if not data:
                break
            print(data.decode(ENCODING), end='')
        except:
            break


def send_loop(sock):
    while True:
        try:
            msg = input()
            sock.sendall((msg + '\n').encode(ENCODING))
            if msg.strip() == '/종료':
                break
        except:
            break


def main():
    nickname = input('닉네임: ').strip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall((nickname + '\n').encode(ENCODING))

        t_recv = threading.Thread(target=recv_loop, args=(sock,), daemon=True)
        t_recv.start()

        send_loop(sock)


if __name__ == '__main__':
    main()
