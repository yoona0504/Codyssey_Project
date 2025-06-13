import zipfile
import string
import itertools
import time
import os

def fast_unlock_zip(zip_path='emergency_storage_key.zip'):
    if not os.path.exists(zip_path):
        print('에러: ZIP 파일이 존재하지 않습니다.')
        return

    start_time = time.time()
    attempt = 0

    # 1단계: 우선 시도할 흔한 비밀번호
    priority_passwords = [
        'abc123', '123456', 'a1b2c3', 'qwerty', '000000',
        '111111', 'asdfgh', 'coffee1', 'ilovey', 'passwd1'
    ]

    charset = string.ascii_lowercase + string.digits

    def try_password(zf, pwd, namelist):
        nonlocal attempt
        attempt += 1
        try:
            zf.extractall(pwd=pwd.encode('utf-8'))
            if all(os.path.exists(name) for name in namelist):
                elapsed = time.time() - start_time
                print(f'\n[성공] 비밀번호: {pwd}')
                print(f'시도 횟수: {attempt}, 시간: {elapsed:.2f}초')
                with open('password.txt', 'w') as f:
                    f.write(pwd)
                return True
        except (RuntimeError, zipfile.BadZipFile, Exception):
            return False
        return False

    with zipfile.ZipFile(zip_path) as zf:
        namelist = zf.namelist()

        # 우선순위 비번 먼저
        for pw in priority_passwords:
            if try_password(zf, pw, namelist):
                return

        # 숫자 6자리 먼저
        for pw in itertools.product(string.digits, repeat=6):
            if try_password(zf, ''.join(pw), namelist):
                return
            if attempt % 10000 == 0:
                print(f'{attempt}회 시도 중...')

        # 전체 문자조합
        for pw in itertools.product(charset, repeat=6):
            if try_password(zf, ''.join(pw), namelist):
                return
            if attempt % 10000 == 0:
                print(f'{attempt}회 시도 중...')

    print('\n비밀번호를 찾지 못했습니다.')

if __name__ == '__main__':
    fast_unlock_zip()
