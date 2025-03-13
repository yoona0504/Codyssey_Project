def main():
    print('Hello Mars')

    log_file = 'mission_computer_main.log'
    report_file = 'log_analysis.md'  # Markdown 보고서 파일

    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            logs = file.readlines()

        # 헤더 제거
        # logs = logs[1:]

        # 원본 로그 순서대로 출력
        print('\n[전체 로그 목록 (원본 순서)]')
        for line in logs:
            print(line.strip())

        # Markdown 보고서 작성
        with open(report_file, 'w', encoding='utf-8') as file:
            file.write('# 로그 분석 보고서\n\n')
            file.write('## 1. 전체 로그 개요\n')
            file.write(f'- 총 로그 개수: {len(logs)}개\n\n')

            file.write('## 2. 사고 원인 분석\n')
            file.write('문제 로그를 보면, <11:35에 산소 탱크가 불안정해지고, 11:40에 폭발>한 것으로 보인다. ')
            file.write('이는 시스템 이상이나 외부 충격이 원인일 가능성이 있다.\n')

            file.write('\n## 3. 결론 및 조치\n')
            file.write('- 산소 탱크 안전 점검 절차 강화\n')
            file.write('- 미션 중 산소 탱크 센서 모니터링 시스템 추가\n')

    except FileNotFoundError:
        print(f'Error: {log_file} 파일을 찾을 수 없습니다.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()
