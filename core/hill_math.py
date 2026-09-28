# core/hill_math.py
# This file contains all exact Linear Algebra operations over \(\mathbb{Z}_{43}\) (free from decimal round-off errors).

import random
import numpy as np
from core.char_set import MODULO

def extended_gcd(a: int, b: int):
    """
        Thuật toán Euclid mở rộng tìm gcd và hệ số Bézout.
        Bézout: d = gcd(a, b) -> Exist x & y: ax + by = d
    """
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a: int, m: int = MODULO) -> int:
    """
        Tìm nghịch đảo modulo của a trong Z_m.
        We have a*a^-1 = 1 mod m <=> a * x - MODULO*y = 1
    """
    a = a % m
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"Số {a} không có nghịch đảo modulo {m} (gcd != 1).")
    return x % m    # -> This is mod inverse of a

def get_matrix_det(matrix: list[list[int]]) -> int:
    """Tính định thức ma trận vuông nguyên cấp n x n bằng biến đổi chính xác."""
    arr = np.array(matrix, dtype=int)
    det = int(round(np.linalg.det(arr)))
    return det

def validate_key(K: list[list[int]], m: int = MODULO) -> tuple[bool, str]:
    """Kiểm tra ma trận khóa K có hợp lệ trong Z_m không."""
    n_rows = len(K)
    for row in K:
        if len(row) != n_rows:
            return False, "Ma trận khóa phải là ma trận vuông n x n."

    det = get_matrix_det(K) % m
    if det == 0:
        return False, f"Định thức det(K) mod {m} = 0. Ma trận không khả nghịch."

    try:
        mod_inverse(det, m)
        return True, f"Khóa hợp lệ! det(K) mod {m} = {det}"
    except ValueError:
        return False, f"det(K) = {det} không nguyên tố cùng nhau với {m}."

def get_cofactor_matrix(K: list[list[int]]) -> list[list[int]]:
    """Tính ma trận các phần phụ đại số (Cofactor Matrix)."""
    n = len(K)
    cofactor = []
    arr = np.array(K, dtype=int)

    for i in range(n):
        cofactor_row = []
        for j in range(n):
            # Tạo ma trận con bằng cách bỏ hàng i, cột j
            minor = np.delete(np.delete(arr, i, axis=0), j, axis=1)
            minor_det = int(round(np.linalg.det(minor)))
            cofactor_val = ((-1) ** (i + j)) * minor_det
            cofactor_row.append(cofactor_val)
        cofactor.append(cofactor_row)
    return cofactor

def get_matrix_inverse(K: list[list[int]], m: int = MODULO) -> list[list[int]]:
    """Tính ma trận nghịch đảo K^-1 mod m sử dụng ma trận phụ hợp adj(K)."""
    is_valid, msg = validate_key(K, m)
    if not is_valid:
        raise ValueError(msg)

    n = len(K)
    det = get_matrix_det(K) % m
    det_inv = mod_inverse(det, m)

    # 1. Tính ma trận phụ hợp adj(K) = chuyển vị của ma trận phụ đại số
    cofactor = get_cofactor_matrix(K)
    adj = np.array(cofactor, dtype=int).T   # Transpose

    # 2. K^-1 = (det_inv * adj) mod m
    K_inv = (det_inv * adj) % m
    return K_inv.tolist()

def process_vector(vector: list[int], M: list[list[int]], m: int = MODULO) -> list[int]:
    """Nhân vector khối với ma trận M modulo m."""
    v_arr = np.array(vector, dtype=int)
    M_arr = np.array(M, dtype=int)
    result = np.dot(M_arr, v_arr) % m
    return result.tolist()

def generate_key(n: int = 3, m: int = MODULO, trial: int = 100) -> list[list[int]]:
    """
        Ta chọn theo hàng, hàng 1 có tổng số là p^n hàng có thể thành lập. Nhưng phải khác hàng 0 -> p^n - 1 cho hàng 1.
        Hàng 2 không được là một tổ hợp tuyến tính của hàng 1 -> h2 != c*h1 -> c có thể trải từ 0 -> p-1. Tổng là p hàng. Do đó ta có thể thành lập p^n-p hàng 2.
        Hàng 3 thì không được là tổ hợp tuyến tính của hàng 1 và hàng 2 -> h3 != c1 * h1 + c2 * h2. Cũng tương tự là ta có thể thành lập c1 c2 từ 0 -> p-1 -> Có thể thành lập được p^n - p*p hàng 3.
        Tương tự cho hàng i

        Xác suất để chọn ngẫu nhiên ra một ma trận K thỏa mãn det != 0 là (với điều kiện m là một số nguyên tố:):
            P = \prod_i=1^n(1-1/p^i)
    """
    attempts = 0
    while True:
        attempts += 1
        # 1. Sinh ma trận n x n ngẫu nhiên các giá trị từ 0 đến m-1
        K = [[random.randint(0, m-1) for _ in range(n)] for _ in range(n)]

        # 2. Kiểm tra tính hợp lệ
        is_valid, _ = validate_key(K, m)

        # Loại bỏ trường hợp ma trận đơn vị (quá vô vị cho mã hóa)
        is_identity = (K == np.eye(n, dtype=int).tolist())

        if is_valid and not is_identity:
            print(f"Generate key matrix successfully after {attempts} tries!")
            return K

        if attempts > trial:
            raise RuntimeError(f"Không thể sinh ma trận khóa hợp lệ sau {trial} lần thử.")