# core/preprocessor.py

import unicodedata
from core.char_set import CHAR_TO_IDX

DIACRITICS_MAP = {
    "\u0300": "f",      # DAU HUYEN
    "\u0301": "s",      # DAU SAC
    "\u0303": "x",      # DAU NGA
    "\u0309": "r",      # DAU HOI
    "\u0323": "j",      # DAU NANG
    "\u0302": "a",      # DAU MU (â, ê, ô). Choose 'a' as representation.
    "\u0306": "w",      # DAU TRANG (ă)
    "\u031b": "w",      # DAU MOC (ơ, ư)
}

INVERSED_DIACRITICS_MAP = {v: k for k, v in DIACRITICS_MAP.items()}
VOWELS = {'a', 'e', 'i', 'o', 'u', 'y'}
VOWEL_MODIFIERS = {'\u0302', '\u0306', '\u031b'}  # Các dấu mũ/móc sau khi đã quy đổi ngược

def preprocess_text(text: str) -> str:
    """
    Tiền xử lý: Chuyển Tiếng Việt có dấu -> NFD -> Thế combining marks thành chữ Telex.
    Ví dụ: 'Gìn giữ' -> 'gifn giuwx'
    """
    text = text.strip().lower()
    nfd_text = unicodedata.normalize('NFD', text)

    converted_chars = []
    for char in nfd_text:
        if char in DIACRITICS_MAP:
            converted_chars.append(DIACRITICS_MAP[char])
        else:
            converted_chars.append(char)

    clean_text = "".join(converted_chars)

    # Chỉ giữ lại các ký tự nằm trong bảng 43 ký tự đã định nghĩa
    return "".join([c for c in clean_text if c in CHAR_TO_IDX])

def postprocess_text(text: str) -> str:
    """
    Hậu xử lý: Khôi phục chuỗi Telex giải mã về lại Tiếng Việt chuẩn NFC.
    Ví dụ: 'gifn giuwx' -> 'Gìn giữ'
    """
    chars = list(text)
    n = len(chars)
    res_chars = []

    for i in range(n):
        c = chars[i]
        prev_c = res_chars[-1] if res_chars else ''

        # Kiểm tra xem ký tự trước đó có phải nguyên âm hoặc dấu phụ nguyên âm không
        is_prev_vowel = (prev_c in VOWELS) or (prev_c in VOWEL_MODIFIERS)

        # 1. Xử lý dấu mũ 'a' (â, ê, ô)
        if c == 'a' and prev_c in {'a', 'e', 'o'}:
            res_chars.append('\u0302')

        # 2. Xử lý dấu 'w' (ă, ơ, ư)
        elif c == 'w' and is_prev_vowel:
            if prev_c == 'a':
                res_chars.append('\u0306')  # Dấu trăng (ă)
            elif prev_c in {'o', 'u'}:
                res_chars.append('\u031b')  # Dấu móc (ơ, ư)
            else:
                res_chars.append(c)         # Giữ nguyên chữ 'w' gốc cho từ tiếng Anh/ngoại nhập (view, news...)

        # 3. Xử lý các dấu thanh: f, s, x, r, j
        elif c == 'f' and is_prev_vowel: res_chars.append('\u0300') # Huyền
        elif c == 's' and is_prev_vowel: res_chars.append('\u0301') # Sắc
        elif c == 'x' and is_prev_vowel: res_chars.append('\u0303') # Ngã
        elif c == 'r' and is_prev_vowel: res_chars.append('\u0309') # Hỏi
        elif c == 'j' and is_prev_vowel: res_chars.append('\u0323') # Nặng

        else:
            res_chars.append(c)

    # Gom các combining marks về dạng NFC chuẩn
    raw_nfd = "".join(res_chars)
    return unicodedata.normalize('NFC', raw_nfd)

def pad_text(text: str, block_size: int = 3, pad_char: str = ' ') -> tuple[str, int]:
    """
    Đệm ký tự pad_char vào cuối chuỗi sao cho độ dài chia hết cho block_size.
    Trả về: (chuỗi_đã_pad, số_ký_tự_đã_thêm)
    """
    remainder = len(text) % block_size
    if remainder == 0:
        return text, 0
    
    pad_len = block_size - remainder
    padded_text = text + (pad_char * pad_len)
    return padded_text, pad_len

def unpad_text(text: str) -> str:
    """
    Loại bỏ các dấu cách thừa ở cuối chuỗi sau khi giải mã.
    """
    return text.rstrip(' ')

if __name__ == "__main__":
    pass
