import argparse
import csv
import getpass
import mimetypes
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from typing import Iterable, List, Optional, Tuple


DEFAULT_SMTP_HOST = 'smtp.gmail.com'
DEFAULT_SMTP_PORT = 587


def build_message(
    from_email: str,
    to_emails: Iterable[str],
    subject: str,
    body_text: Optional[str] = None,
    body_html: Optional[str] = None,
    attachments: Optional[Iterable[str]] = None,
) -> EmailMessage:
    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = subject

    if body_html and body_text:
        msg.set_content(body_text)
        msg.add_alternative(body_html, subtype='html')
    elif body_html:
        msg.add_alternative(body_html, subtype='html')
    else:
        msg.set_content(body_text or '')

    if attachments:
        for path in attachments:
            add_attachment(msg, path)

    return msg


def add_attachment(msg: EmailMessage, filepath: str) -> None:
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)

    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'

    maintype, subtype = ctype.split('/', 1)

    with open(filepath, 'rb') as f:
        msg.add_attachment(
            f.read(),
            maintype=maintype,
            subtype=subtype,
            filename=os.path.basename(filepath),
        )


def open_smtp(
    smtp_host: str,
    smtp_port: int,
    timeout: int,
) -> smtplib.SMTP:
    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=timeout)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    return server


def send_via_smtp(
    from_email: str,
    password: str,
    message: EmailMessage,
    smtp_host: str,
    smtp_port: int,
    timeout: int = 30,
    to_addrs: Optional[List[str]] = None,
) -> None:
    try:
        with open_smtp(smtp_host, smtp_port, timeout) as server:
            server.login(from_email, password)
            if to_addrs is None:
                server.send_message(message)
            else:
                server.send_message(message, to_addrs=to_addrs)
    except Exception as exc:
        print(f'전송 실패: {exc}', file=sys.stderr)
        raise


def send_multiple_messages(
    from_email: str,
    password: str,
    messages: Iterable[EmailMessage],
    smtp_host: str,
    smtp_port: int,
    timeout: int = 30,
) -> None:
    try:
        with open_smtp(smtp_host, smtp_port, timeout) as server:
            server.login(from_email, password)
            for message in messages:
                server.send_message(message)
    except Exception as exc:
        print(f'전송 실패: {exc}', file=sys.stderr)
        raise


def load_targets(csv_path: str) -> List[Tuple[str, str]]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    targets: List[Tuple[str, str]] = []

    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('이름') or '').strip()
            email = (row.get('이메일') or '').strip()
            if email:
                targets.append((name, email))

    if not targets:
        raise ValueError('수신자 없음')

    return targets


def load_target_emails(csv_path: str) -> List[str]:
    targets = load_targets(csv_path)
    recipients: List[str] = []
    for name, email in targets:
        recipients.append(f'{name} <{email}>' if name else email)
    return recipients


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('--from-email', required=True)
    parser.add_argument('--to', nargs='+')
    parser.add_argument('--target-csv', default='mail_target_list.csv')
    parser.add_argument('--send-mode', choices=['bulk', 'single'], default='single')
    parser.add_argument('--subject', required=True)
    parser.add_argument('--body', default='')
    parser.add_argument('--html', default='')
    parser.add_argument('--attachments', nargs='*', default=[])
    parser.add_argument('--smtp-host', default=DEFAULT_SMTP_HOST)
    parser.add_argument('--smtp-port', type=int, default=DEFAULT_SMTP_PORT)
    parser.add_argument('--password', default='')
    parser.add_argument('--timeout', type=int, default=30)

    return parser.parse_args(argv)


def resolve_password(passed: str) -> str:
    if passed:
        return passed

    env_pw = os.getenv('GMAIL_APP_PASSWORD', '')
    if env_pw:
        return env_pw

    return getpass.getpass('비밀번호 입력: ')


def resolve_recipients(args: argparse.Namespace) -> List[str]:
    if args.target_csv and os.path.exists(args.target_csv):
        return load_target_emails(args.target_csv)
    if args.to:
        return args.to
    raise ValueError('수신자 정보 없음')


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    password = resolve_password(args.password)

    body_text = args.body or None
    body_html = args.html or None
    recipients = resolve_recipients(args)
    attachments = args.attachments or None

    try:
        if args.send_mode == 'bulk':
            targets = load_targets(args.target_csv)
            bcc_emails = [email for _, email in targets]

            message = build_message(
                from_email=args.from_email,
                to_emails=[args.from_email],
                subject=args.subject,
                body_text=body_text,
                body_html=body_html,
                attachments=attachments,
            )
            message['Bcc'] = ', '.join(bcc_emails)

            send_via_smtp(
                from_email=args.from_email,
                password=password,
                message=message,
                smtp_host=args.smtp_host,
                smtp_port=args.smtp_port,
                timeout=args.timeout,
                to_addrs=bcc_emails,
            )
        else:
            messages: List[EmailMessage] = []
            for r in recipients:
                msg = build_message(
                    args.from_email,
                    [r],
                    args.subject,
                    body_text,
                    body_html,
                    attachments,
                )
                messages.append(msg)

            send_multiple_messages(
                args.from_email,
                password,
                messages,
                args.smtp_host,
                args.smtp_port,
                args.timeout,
            )

        print('메일 전송 완료')

    except Exception:
        sys.exit(1)


if __name__ == '__main__':
    main()
