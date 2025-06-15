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
        decoded_texts.append(decoded)
    return decoded_texts

def load_dictionary(path='dictionary.txt'):
    try:
        with open(path, 'r') as f:
            words = set(word.strip().lower() for word in f if word.strip())
        return words
    except FileNotFoundError:
        print('[!] dictionary.txt 파일이 없습니다. 자동 탐지를 건너뜁니다.')
        return set()

def detect_valid_text(decoded_list, word_set, threshold=3):
    for i, text in enumerate(decoded_list):
        words = text.lower().split()
        match_count = sum(1 for word in words if word in word_set)
        if match_count >= threshold:
            print(f'\n[자동탐지] 시프트 {i+1} 에서 단어 {match_count}개 일치:')
            print(text)
            return i + 1, text
    return None, None

def main():
    try:
        with open('password_bonus.txt', 'r') as f:
            encrypted = f.read().strip()
    except FileNotFoundError:
        print('[오류] password_bonus.txt 파일이 없습니다.')
        return

    candidates = caesar_cipher_decode(encrypted)
    dictionary = load_dictionary()

    shift, result = detect_valid_text(candidates, dictionary)

    if not result:
        print('\n[실패] 자동 탐지에 실패했습니다. 수동으로 선택해야 합니다.')
        for i, candidate in enumerate(candidates):
            print(f'\n[Shift {i+1}]\n{candidate}')
        try:
            shift_input = input('\n정답으로 보이는 시프트 수를 입력하세요 (1~25): ')
            shift = int(shift_input)
            result = candidates[shift - 1]
        except Exception:
            print('[오류] 수동 입력 실패.')
            return

    try:
        with open('result_bonus.txt', 'w') as f:
            f.write(result)
        print('\n[완료] 복호화된 결과가 result_bonus.txt에 저장되었습니다.')
    except Exception as e:
        print(f'[오류] 결과 저장 실패: {e}')

if __name__ == '__main__':
    main()
