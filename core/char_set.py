# core/char_set.py

# Tập hợp 43 ký tự chuẩn (m = 43 là số nguyên tố)
CHAR_SET = [
    'a', 'b', 'c', 'd', 'đ', 'e', 'g', 'h', 'i', 'k', 'l', 'm', 'n',
    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'j', 'f', 'w', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    ' ', '.', ',', '!', '?', '-'
]

MODULO = len(CHAR_SET)  # 43

# Bảng tra cứu nhanh tốc độ O(1)
CHAR_TO_IDX = {char: idx for idx, char in enumerate(CHAR_SET)}
IDX_TO_CHAR = {idx: char for idx, char in enumerate(CHAR_SET)}

def char_to_index(char: str) -> int:
    """Chuyển ký tự sang số index (0..42)."""
    if char not in CHAR_TO_IDX:
        return ''   # If current char is not in the dictionary -> skip this character
    return CHAR_TO_IDX[char]

def index_to_char(index: str) -> str:
    """Chuyển chỉ số index sang ký tự."""
    return IDX_TO_CHAR[index % MODULO]