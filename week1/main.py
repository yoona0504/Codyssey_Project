def main():
    # 프로그램 시작 메시지 출력
    print('Hello Mars')

    # 로그 파일 및 보고서 파일 정의
    log_file = 'mission_computer_main.log'  # 로그 데이터가 저장된 파일
    report_file = 'log_analysis.md'  # 분석 결과를 저장할 Markdown 파일

    try:
        # 로그 파일을 읽기 모드로 열기 (UTF-8 인코딩 사용)
        with open(log_file, 'r', encoding='utf-8') as file:
            logs = file.readlines()  # 모든 로그 데이터를 리스트로 저장

        # 첫 번째 줄(헤더)을 제거하여 실제 로그 데이터만 남김
        logs = logs[1:]

        # 원본 로그를 콘솔에 출력 (로그 순서를 유지)
        print('\n[전체 로그 목록 (원본 순서)]')
        for line in logs:
            print(line.strip())  # 공백 제거 후 출력

        # 분석 결과를 Markdown 보고서 파일에 저장
        with open(report_file, 'w', encoding='utf-8') as file:
            # 보고서 제목
            file.write('# 로그 분석 보고서\n\n')

            # 로그 개요 작성
            file.write('## 1. 전체 로그 개요\n')
            file.write(f'- 총 로그 개수: {len(logs)}개\n\n')  # 로그 개수 기록

            # 사고 원인 분석 섹션 작성
            file.write('## 2. 사고 원인 분석\n')
            file.write('문제 로그를 보면, <11:35에 산소 탱크가 불안정해지고, 11:40에 폭발>한 것으로 보인다. ')
            file.write('이는 시스템 이상이나 외부 충격이 원인일 가능성이 있다.\n')

            # 결론 및 조치 사항 작성
            file.write('\n## 3. 결론 및 조치\n')
            file.write('- 산소 탱크 안전 점검 절차 강화\n')
            file.write('- 미션 중 산소 탱크 센서 모니터링 시스템 추가\n')

    # 파일이 존재하지 않을 경우 예외 처리
    except FileNotFoundError:
        print(f'Error: {log_file} 파일을 찾을 수 없습니다.')

    # 기타 예외 발생 시 예외 메시지 출력
    except Exception as e:
        print(f'Error: {e}')

# 프로그램이 직접 실행될 때 main() 함수를 호출
if __name__ == '__main__':
    main()
