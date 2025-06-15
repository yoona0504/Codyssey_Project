import os
import datetime
import sounddevice as sd
from scipy.io.wavfile import write


def ensure_records_directory():
    if not os.path.exists('records'):
        os.mkdir('records')


def generate_filename():
    now = datetime.datetime.now()
    filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    return os.path.join('records', filename)


def record_audio(duration_seconds=5, sample_rate=44100):
    print('녹음 시작...')
    recording = sd.rec(int(duration_seconds * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    filename = generate_filename()
    write(filename, sample_rate, recording)
    print('녹음 완료. 파일 저장 위치:', filename)


def list_recordings_by_date(start_date_str, end_date_str):
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d')
    except ValueError:
        print('날짜 형식이 올바르지 않습니다. 예시: 20250101')
        return

    print('지정한 날짜 범위 내 녹음 파일:')
    for file_name in os.listdir('records'):
        if file_name.endswith('.wav'):
            file_date_str = file_name.split('-')[0]
            try:
                file_date = datetime.datetime.strptime(file_date_str, '%Y%m%d')
                if start_date <= file_date <= end_date:
                    print(file_name)
            except ValueError:
                continue


def main():
    ensure_records_directory()

    print('1: 녹음 시작')
    print('2: 날짜 범위로 녹음 파일 조회')
    print('q: 종료')

    while True:
        command = input('명령을 입력하세요: ')
        if command == '1':
            record_audio()
        elif command == '2':
            start = input('시작 날짜 (예: 20250101): ')
            end = input('끝 날짜 (예: 20250131): ')
            list_recordings_by_date(start, end)
        elif command.lower() == 'q':
            print('종료합니다.')
            break
        else:
            print('알 수 없는 명령입니다.')


if __name__ == '__main__':
    main()
