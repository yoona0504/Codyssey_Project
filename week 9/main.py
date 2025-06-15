def caesar_cipher_decode(target_text):
    decoded_texts = []
    for shift in range(1, 26):
        decoded = ''
        for char in target_text:
            if 'a' <= char <= 'z':
                decoded += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                decoded += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                decoded += char
        print(f'\n[Shift {shift}]:\n{decoded}')
        decoded_texts.append(decoded)
    return decoded_texts

def main():
    try:
        with open('password.txt', 'r') as f:
            encrypted = f.read().strip()
    except FileNotFoundError:
        print('password.txt 파일을 찾을 수 없습니다.')
        return
    except Exception as e:
        print(f'파일 읽기 중 오류 발생: {e}')
        return

    candidates = caesar_cipher_decode(encrypted)

    try:
        shift_input = input('\n올바른 복호화 결과를 출력한 시프트 수를 입력하세요 (1~25): ')
        shift = int(shift_input)
        if not 1 <= shift <= 25:
            print('잘못된 숫자입니다. 1~25 사이의 숫자를 입력하세요.')
            return
    except ValueError:
        print('숫자를 입력해야 합니다.')
        return

    result = candidates[shift - 1]
    try:
        with open('result.txt', 'w') as f:
            f.write(result)
        print('\n복호화된 결과가 result.txt에 저장되었습니다.')
    except Exception as e:
        print(f'result.txt 저장 중 오류 발생: {e}')

if __name__ == '__main__':
    main()
