def process_logs():
    # 로그 파일 경로 설정
    log_file = 'mission_computer_main.log'  # 원본 로그 파일
    error_log_file = 'error_logs.txt'  # 문제 로그를 저장할 파일

    try:
        # 로그 파일 읽기 (UTF-8 인코딩)
        with open(log_file, 'r', encoding='utf-8') as file:
            logs = file.readlines()  # 모든 로그를 리스트로 저장

        # 첫 번째 줄(헤더) 제거
        logs = logs[1:]

        # 로그를 시간 역순으로 정렬 (최근 로그가 위로 오도록)
        logs.reverse()

        # 정렬된 로그를 콘솔에 출력
        print('\n[전체 로그 목록 (시간 역순)]')
        for line in logs:
            print(line.strip())  # 각 로그의 앞뒤 공백 제거 후 출력

        # 특정 키워드("unstable" 또는 "explosion")를 포함하는 문제 로그 필터링
        error_logs = [line for line in logs if 'unstable' in line.lower() or 'explosion' in line.lower()]

        # 필터링된 문제 로그를 콘솔에 출력
        print('\n[*문제 로그 목록*]')
        for line in error_logs:
            print(line.strip())

        # 문제 로그를 파일로 저장
        with open(error_log_file, 'w', encoding='utf-8') as file:
            file.writelines(error_logs)  # 필터링된 로그를 파일에 저장

    # 로그 파일이 존재하지 않을 경우 예외 처리
    except FileNotFoundError:
        print(f'Error: {log_file} 파일을 찾을 수 없습니다.')

    # 기타 예외 발생 시 오류 메시지 출력
    except Exception as e:
        print(f'Error: {e}')

# 프로그램이 직접 실행될 경우 process_logs() 함수 호출
if __name__ == '__main__':
    process_logs()
