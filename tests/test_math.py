# test_core.py
from core.hill_math import validate_key, get_matrix_inverse, process_vector, generate_key
from core.preprocessor import preprocess_text, postprocess_text
from core.char_set import char_to_index, index_to_char, MODULO

if __name__ == "__main__":
    # 1. Khởi tạo ma trận khóa K cấp 3x3
    # K = [
    #     [3, 10, 20],
    #     [20, 19, 17],
    #     [15, 18, 6]
    # ]
    K = generate_key(n=7, m=43, trial=100)

    print("=== 1. KIỂM TRA MA TRẬN KHÓA ===")
    is_valid, msg = validate_key(K)
    print(msg)

    K_inv = get_matrix_inverse(K)
    print(f"Ma trận nghịch đảo K^-1 mod {MODULO}:")
    for row in K_inv:
        print(row)

    # 2. Test Tiền xử lý Tiếng Việt
    print("\n=== 2. TEST TIỀN XỬ LÝ TIẾNG VIỆT ===")
    original_text = "cơm"
    preprocessed = preprocess_text(original_text)
    print(f"Văn bản gốc:      '{original_text}'")
    print(f"Sau khi Reorder:   '{preprocessed}'")

    # 3. Mã hóa từng khối 3x1
    print("\n=== 3. QUÁ TRÌNH MÃ HÓA & GIẢI MÃ HILL ===")
    n = len(K)
    # Pad dấu cách nếu độ dài không chia hết cho 3
    padded_text = preprocessed
    while len(padded_text) % n != 0:
        padded_text += " "

    # Đổi sang chỉ số
    indices = [char_to_index(c) for c in padded_text]

    # Chia block & Mã hóa
    cipher_indices = []
    for i in range(0, len(indices), n):
        block = indices[i:i+n]
        cipher_block = process_vector(block, K)
        cipher_indices.extend(cipher_block)

    cipher_text = "".join([index_to_char(idx) for idx in cipher_indices])
    print(f"Bản mã (Ciphertext): '{cipher_text}'")

    # Giải mã với K^-1
    decrypted_indices = []
    for i in range(0, len(cipher_indices), n):
        block = cipher_indices[i:i+n]
        plain_block = process_vector(block, K_inv)
        decrypted_indices.extend(plain_block)

    decrypted_preprocessed = "".join([index_to_char(idx) for idx in decrypted_indices]).rstrip()
    final_restored_text = postprocess_text(decrypted_preprocessed)

    print(f"Giải mã thô:         '{decrypted_preprocessed}'")
    print(f"Khôi phục Tiếng Việt: '{final_restored_text}'")

    assert original_text == final_restored_text, "LỖI: Khôi phục không trùng khớp!"
    print("\n XÁC NHẬN: TOÀN BỘ MODULE CORE HOẠT ĐỘNG HOÀN HẢO!")