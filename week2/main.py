def read_csv_file(file_path):
    """CSV 파일을 읽고 인화성이 높은 물질을 리스트로 변환하는 함수"""
    inventory_list = []  # 데이터를 저장할 리스트

    try:
        # UTF-8 인코딩으로 파일을 읽기 모드로 열기
        with open(file_path, 'r', encoding='utf-8') as file:
            header = file.readline().strip().split(',')  # 첫 번째 줄(헤더)을 읽고 버림

            for line in file:
                parts = line.strip().split(',')  # 쉼표(,)를 기준으로 문자열을 분할
                if len(parts) < 5:  
                    continue  # 데이터가 부족한 경우 무시

                try:
                    name = parts[0].strip()  # 첫 번째 컬럼: 물질 이름
                    flammability = float(parts[4].strip())  # 다섯 번째 컬럼: 인화성 지수
                    inventory_list.append((name, flammability))  # 리스트에 추가
                except ValueError:
                    continue  # 숫자로 변환할 수 없는 경우 무시
    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {file_path}')
    except Exception as e:
        print(f'오류 발생: {e}')
    
    return inventory_list  # 최종적으로 (물질 이름, 인화성 지수) 리스트 반환


def save_csv_file(file_path, data):
    """리스트 데이터를 CSV 파일로 저장하는 함수"""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('Name,Flammability\n')  # 첫 번째 줄(헤더) 추가

            for item in data:
                file.write(f'{item[0]},{item[1]}\n')  # 각 행을 CSV 형식으로 저장
    except Exception as e:
        print(f'파일 저장 중 오류 발생: {e}')


def save_binary_file(file_path, data):
    """리스트 데이터를 이진 파일로 저장하는 함수"""
    try:
        with open(file_path, 'wb') as file:  # 이진 파일 쓰기 모드로 열기
            for item in data:
                name_bytes = item[0].encode('utf-8')  # 이름을 바이트로 변환
                name_length = len(name_bytes)  # 바이트 길이 계산
                file.write(name_length.to_bytes(1, 'big'))  # 이름 길이를 1바이트로 저장
                file.write(name_bytes)  # 이름 데이터를 저장
                file.write(float_to_bytes(item[1]))  # 인화성 지수를 이진 형식으로 저장
    except Exception as e:
        print(f'이진 파일 저장 중 오류 발생: {e}')


def float_to_bytes(value):
    """실수를 바이트로 변환"""
    import struct
    return struct.pack('d', value)  # 8바이트(64비트) 부동소수점 형식으로 변환


def main():
    input_file = 'Mars_Base_Inventory_List.csv'  # 입력 CSV 파일
    output_file = 'Mars_Base_Inventory_danger.csv'  # 위험 물질 저장할 CSV 파일

    # CSV 파일 읽기
    inventory_list = read_csv_file(input_file)

    if not inventory_list:  # 데이터가 없으면 종료
        print('파일에서 데이터를 읽어오지 못했습니다.')
        return

    # 인화성 기준으로 내림차순 정렬
    sorted_inventory = sorted(inventory_list, key=lambda x: x[1], reverse=True)

    # 인화성 0.7 이상인 데이터만 필터링
    dangerous_items = [item for item in sorted_inventory if item[1] >= 0.7]

    # 정렬된 전체 목록 출력
    print('정렬된 전체 목록:')
    for item in sorted_inventory:
        print(f'{item[0]}: {item[1]}')

    # 인화성이 높은 항목 출력
    print('\n인화성이 높은 항목 목록:')
    for item in dangerous_items:
        print(f'{item[0]}: {item[1]}')

    # 위험한 항목을 CSV 파일로 저장
    save_csv_file(output_file, dangerous_items)
    print(f'\n인화성 0.7 이상 목록이 {output_file} 에 저장되었습니다.')


if __name__ == '__main__':
    main()

# 외부에서 import 가능하도록 설정
__all__ = ['read_csv_file', 'save_binary_file']
