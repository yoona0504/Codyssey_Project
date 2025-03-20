from main import read_csv_file, save_binary_file  # main.py에서 함수 가져오기
import struct

def read_binary_file(file_path):
    """이진 파일에서 데이터를 읽어오는 함수"""
    data = []
    try:
        with open(file_path, 'rb') as file:  # 이진 파일 읽기 모드로 열기
            while True:
                name_length_bytes = file.read(1)  # 1바이트(이름 길이) 읽기
                if not name_length_bytes:
                    break  # 파일 끝에 도달하면 종료

                name_length = int.from_bytes(name_length_bytes, 'big')  # 바이트 값을 정수로 변환
                name = file.read(name_length).decode('utf-8')  # 이름 데이터를 문자열로 변환
                flammability = struct.unpack('d', file.read(8))[0]  # 8바이트(64비트) 실수 데이터 읽기
                data.append((name, flammability))  # 리스트에 추가
    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {file_path}')
    except Exception as e:
        print(f'이진 파일 읽기 중 오류 발생: {e}')
    
    return data  # (이름, 인화성 지수) 튜플 리스트 반환


def main():
    input_file = 'Mars_Base_Inventory_List.csv'  # 원본 CSV 파일
    binary_file = 'Mars_Base_Inventory_List.bin'  # 이진 파일 저장 위치

    # CSV 파일 읽기
    inventory_list = read_csv_file(input_file)

    if not inventory_list:  # 데이터가 없으면 종료
        print('파일에서 데이터를 읽어오지 못했습니다.')
        return

    # 인화성 기준으로 내림차순 정렬
    sorted_inventory = sorted(inventory_list, key=lambda x: x[1], reverse=True)

    # 이진 파일 저장
    save_binary_file(binary_file, sorted_inventory)
    print(f'\n정렬된 목록이 이진 파일 {binary_file}로 저장되었습니다.')

    # 저장된 이진 파일 읽기
    loaded_data = read_binary_file(binary_file)

    # 이진 파일에서 읽어온 데이터 출력
    print('\n< 이진 파일에서 읽어온 데이터 >')
    for item in loaded_data:
        print(f'{item[0]}: {item[1]}')

if __name__ == '__main__':
    main()