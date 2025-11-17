from __future__ import annotations

import argparse
import getpass
import mimetypes
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from typing import Iterable, List


DEFAULT_SMTP_HOST = 'smtp.gmail.com'
DEFAULT_SMTP_PORT = 587  # STARTTLS (권장)


def build_message(
    from_email: str,
    to_emails: Iterable[str],
    subject: str,
    body_text: str | None = None,
    body_html: str | None = None,
    attachments: Iterable[str] | None = None,
) -> EmailMessage:
    """
    EmailMessage 객체를 생성한다.

    :param from_email: 보내는 사람 이메일
    :param to_emails: 받는 사람 이메일 리스트
    :param subject: 제목
    :param body_text: 텍스트 본문
    :param body_html: HTML 본문
    :param attachments: 첨부파일 경로 리스트
    :return: EmailMessage
    """
    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = subject

    # 본문 구성: 텍스트와 HTML 동시 제공 시 멀티파트/알터너티브
    if body_html and body_text:
        msg.set_content(body_text)
        msg.add_alternative(body_html, subtype='html')
    elif body_html:
        # 텍스트 대체가 없더라도 HTML만 전송 가능
        msg.add_alternative(body_html, subtype='html')
    else:
        msg.set_content(body_text or '')

    # 첨부파일 처리
    if attachments:
        for path in attachments:
            add_attachment(msg, path)

    return msg


def add_attachment(msg: EmailMessage, filepath: str) -> None:
    """
    파일 경로를 받아 EmailMessage에 첨부한다.

    :param msg: EmailMessage 객체
    :param filepath: 파일 경로
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'첨부 파일을 찾을 수 없습니다: {filepath}')

    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'

    maintype, subtype = ctype.split('/', 1)

    with open(filepath, 'rb') as f:
        file_data = f.read()

    filename = os.path.basename(filepath)
    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=filename)


def send_via_gmail_smtp(
    from_email: str,
    password: str,
    message: EmailMessage,
    smtp_host: str = DEFAULT_SMTP_HOST,
    smtp_port: int = DEFAULT_SMTP_PORT,
    timeout: int = 30,
) -> None:
    """
    Gmail SMTP 서버로 메시지를 전송한다.

    :param from_email: 보내는 사람 이메일(로그인 계정)
    :param password: 비밀번호(앱 비밀번호 권장)
    :param message: EmailMessage
    :param smtp_host: SMTP 호스트
    :param smtp_port: SMTP 포트(587 권장)
    :param timeout: 연결 타임아웃(초)
    """
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as server:
            # 서버 인사
            server.ehlo()
            # 보안 연결(STARTTLS)
            server.starttls(context=context)
            server.ehlo()

            # 로그인
            server.login(from_email, password)

            # 전송
            server.send_message(message)

    except smtplib.SMTPAuthenticationError as exc:
        print(
            '인증 실패: 아이디/비밀번호가 올바른지, '
            '또는 앱 비밀번호 사용이 필요한지 확인하세요.',
            file=sys.stderr,
        )
        raise exc
    except smtplib.SMTPRecipientsRefused as exc:
        print('수신자 주소가 거부되었습니다. 주소를 확인하세요.', file=sys.stderr)
        raise exc
    except smtplib.SMTPSenderRefused as exc:
        print('발신자 주소가 거부되었습니다. 발신 주소 설정을 확인하세요.', file=sys.stderr)
        raise exc
    except smtplib.SMTPDataError as exc:
        print('SMTP 데이터 전송 중 오류가 발생했습니다.', file=sys.stderr)
        raise exc
    except smtplib.SMTPConnectError as exc:
        print('SMTP 서버 연결에 실패했습니다. 네트워크를 확인하세요.', file=sys.stderr)
        raise exc
    except OSError as exc:
        print('입출력 오류가 발생했습니다. 파일/네트워크 상태를 확인하세요.', file=sys.stderr)
        raise exc
    except Exception as exc:
        print('알 수 없는 오류가 발생했습니다.', file=sys.stderr)
        raise exc


def parse_args(argv: List[str]) -> argparse.Namespace:
    """
    명령행 인자를 파싱한다.
    """
    parser = argparse.ArgumentParser(
        description='Gmail SMTP를 사용하여 메일을 전송합니다.',
    )

    parser.add_argument(
        '--from-email',
        required=True,
        help='보내는 사람 지메일 주소(로그인 계정)',
    )
    parser.add_argument(
        '--to',
        nargs='+',
        required=True,
        help='받는 사람 이메일 주소(여러 명 가능, 공백으로 구분)',
    )
    parser.add_argument(
        '--subject',
        required=True,
        help='메일 제목',
    )
    parser.add_argument(
        '--body',
        default='',
        help='텍스트 본문(기본값: 빈 문자열)',
    )
    parser.add_argument(
        '--html',
        default='',
        help='HTML 본문(선택)',
    )
    parser.add_argument(
        '--attachments',
        nargs='*',
        default=[],
        help='첨부 파일 경로(여러 개 가능)',
    )
    parser.add_argument(
        '--smtp-host',
        default=DEFAULT_SMTP_HOST,
        help=f'SMTP 호스트 (기본값: {DEFAULT_SMTP_HOST})',
    )
    parser.add_argument(
        '--smtp-port',
        type=int,
        default=DEFAULT_SMTP_PORT,
        help=f'SMTP 포트 (기본값: {DEFAULT_SMTP_PORT})',
    )
    parser.add_argument(
        '--password',
        default='',
        help='지메일 비밀번호 또는 앱 비밀번호(권장). 제공하지 않으면 환경변수나 프롬프트로 입력.',
    )

    return parser.parse_args(argv)


def resolve_password(passed: str) -> str:
    """
    비밀번호 입력 우선순위:
    1) --password 인자
    2) 환경변수 GMAIL_APP_PASSWORD
    3) 프롬프트 입력(getpass)
    """
    if passed:
        return passed

    env_pw = os.getenv('GMAIL_APP_PASSWORD', '')
    if env_pw:
        return env_pw

    return getpass.getpass('Gmail 비밀번호(또는 앱 비밀번호)를 입력하세요: ')


def main(argv: List[str] | None = None) -> None:
    """
    엔트리 포인트.
    """
    args = parse_args(argv or sys.argv[1:])
    password = resolve_password(args.password)

    try:
        msg = build_message(
            from_email=args.from_email,
            to_emails=args.to,
            subject=args.subject,
            body_text=args.body if args.body else None,
            body_html=args.html if args.html else None,
            attachments=args.attachments if args.attachments else None,
        )

        send_via_gmail_smtp(
            from_email=args.from_email,
            password=password,
            message=msg,
            smtp_host=args.smtp_host,
            smtp_port=args.smtp_port,
        )

        print('메일이 성공적으로 전송되었습니다.')
    except Exception as exc:
        # 상세 스택은 필요 시 출력하도록 하고, 사용자 메시지는 한 줄로 요약
        print(f'전송 실패: {exc.__class__.__name__}: {exc}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
