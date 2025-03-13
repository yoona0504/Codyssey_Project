def process_logs():
    log_file = 'mission_computer_main.log'
    error_log_file = 'error_logs.txt'

    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            logs = file.readlines()

        # 헤더 제거
        logs = logs[1:]

        # 시간 역순 정렬 후 출력
        logs.reverse()
        print('\n[전체 로그 목록 (시간 역순)]')
        for line in logs:
            print(line.strip())

        # 문제 로그 필터링
        error_logs = [line for line in logs if 'unstable' in line.lower() or 'explosion' in line.lower()]

        # 문제 로그 출력
        print('\n[*문제 로그 목록*]')
        for line in error_logs:
            print(line.strip())

        # 문제 로그 저장
        with open(error_log_file, 'w', encoding='utf-8') as file:
            file.writelines(error_logs)

    except FileNotFoundError:
        print(f'Error: {log_file} 파일을 찾을 수 없습니다.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    process_logs()
