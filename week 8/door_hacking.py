import zipfile
import string
import itertools
import time
import os

def unlock_zip(zip_path='emergency_storage_key.zip'):
    if not os.path.exists(zip_path):
        print('에러: ZIP 파일이 존재하지 않습니다.')
        return

    start_time = time.time()
    charset = string.ascii_lowercase + string.digits
    attempt = 0

    with zipfile.ZipFile(zip_path) as zf:
        namelist = zf.namelist()

        for pwd in itertools.product(charset, repeat=6):
            password = ''.join(pwd)
            attempt += 1

            try:
                zf.extractall(pwd=password.encode('utf-8'))

                # 압축 해제된 파일이 실제 존재하는지 확인
                if all(os.path.exists(name) for name in namelist):
                    elapsed_time = time.time() - start_time
                    print(f'\n[성공] 비밀번호를 찾았습니다: {password}')
                    print(f'총 시도 횟수: {attempt}')
                    print(f'걸린 시간: {elapsed_time:.2f}초')

                    with open('password.txt', 'w') as f:
                        f.write(password)

                    return

            except (RuntimeError, zipfile.BadZipFile, Exception):
                if attempt % 10000 == 0:
                    elapsed_time = time.time() - start_time
                    print(f'{attempt}회 시도 중... 경과 시간: {elapsed_time:.2f}초')

    print('\n비밀번호를 찾지 못했습니다.')

if __name__ == '__main__':
    unlock_zip()
