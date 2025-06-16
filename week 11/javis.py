import os
import datetime
import sounddevice as sd
from scipy.io.wavfile import write
import csv
import wave
import contextlib
import speech_recognition as sr

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDS_DIR = os.path.join(BASE_DIR, 'records')


def ensure_records_directory():
    if not os.path.exists(RECORDS_DIR):
        os.mkdir(RECORDS_DIR)


def generate_filename():
    now = datetime.datetime.now()
    filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    return os.path.join(RECORDS_DIR, filename)


def record_audio(duration_seconds=5, sample_rate=44100):
    print('녹음 시작...')
    recording = sd.rec(int(duration_seconds * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    filename = generate_filename()
    write(filename, sample_rate, recording)
    print('녹음 완료. 파일 저장 위치:', filename)


def convert_audio_to_text(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language='ko-KR')
        return [(0, text)]
    except sr.UnknownValueError:
        return [(0, '인식 실패')]
    except sr.RequestError as e:
        return [(0, f'API 오류: {e}')]


def save_text_to_csv(wav_file_path):
    transcript = convert_audio_to_text(wav_file_path)
    csv_file_path = wav_file_path.replace('.wav', '.csv')

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['시간(초)', '인식된 텍스트'])
        for timestamp, text in transcript:
            writer.writerow([timestamp, text])

    print('변환 완료. CSV 저장 위치:', csv_file_path)


def list_wav_files():
    files = []
    for name in os.listdir(RECORDS_DIR):
        if name.endswith('.wav'):
            files.append(os.path.join(RECORDS_DIR, name))
    return files


def run_transcribe_all():
    files = list_wav_files()
    if not files:
        print('변환할 음성 파일이 없습니다.')
        return

    for wav_path in files:
        print('STT 처리 중:', wav_path)
        save_text_to_csv(wav_path)


def search_keyword_in_csv(keyword):
    found = False
    for name in os.listdir(RECORDS_DIR):
        if name.endswith('.csv'):
            path = os.path.join(RECORDS_DIR, name)
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    if keyword in row[1]:
                        print(f'[{name}] {row[0]}초: {row[1]}')
                        found = True
    if not found:
        print('키워드를 포함한 텍스트가 없습니다.')


def main():
    ensure_records_directory()

    print('1: 녹음 시작')
    print('2: 녹음된 파일들을 텍스트로 변환 (STT)')
    print('3: 키워드로 기록 검색')
    print('q: 종료')

    while True:
        command = input('명령을 입력하세요: ')
        if command == '1':
            record_audio()
        elif command == '2':
            run_transcribe_all()
        elif command == '3':
            keyword = input('검색할 키워드를 입력하세요: ')
            search_keyword_in_csv(keyword)
        elif command.lower() == 'q':
            print('종료합니다.')
            break
        else:
            print('알 수 없는 명령입니다.')


if __name__ == '__main__':
    main()
