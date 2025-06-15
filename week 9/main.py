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
        print(f'\n[Shift {shift}]\n{decoded}')
        decoded_texts.append(decoded)
    return decoded_texts

def main():
    try:
        with open('password.txt', 'r') as f:
            encrypted = f.read().strip()
    except FileNotFoundError:
        print('[오류] password.txt 파일이 없습니다.')
        return

    candidates = caesar_cipher_decode(encrypted)

    try:
        shift_input = input('\n정답으로 보이는 시프트 수를 입력하세요 (1~25): ')
        shift = int(shift_input)
        if not 1 <= shift <= 25:
            print('시프트 수는 1부터 25 사이여야 합니다.')
            return
        result = candidates[shift - 1]
    except ValueError:
        print('숫자를 입력하세요.')
        return

    try:
        with open('result_basic.txt', 'w') as f:
            f.write(result)
        print('\n[완료] 복호화된 결과가 result.txt에 저장되었습니다.')
    except Exception as e:
        print(f'[오류] 결과 저장 중 문제가 발생했습니다: {e}')

if __name__ == '__main__':
    main()
