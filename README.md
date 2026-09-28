# HỆ THỐNG MÃ HÓA & MÔ PHỎNG MẬT MÃ HILL TIẾNG VIỆT ($\mathbb{Z}_{41}$)

Dự án Bài tập lớn Đại số Tuyến tính: xây dựng ứng dụng Web mô phỏng truyền tin bảo mật đầu cuối (End-to-End Encryption) sử dụng Mật mã Hill trên trường hữu hạn $\mathbb{Z}_{41}$. Hệ thống hỗ trợ xử lý Tiếng Việt có dấu và cung cấp bộ Visualizer minh họa chi tiết từng bước tính toán đại số ma trận.

## 1. Cơ sở Toán học & Thuật toán

### 1.1. Trường hữu hạn $\mathbb{Z}_{41}$

Hệ thống sử dụng bảng mã mở rộng gồm 41 ký tự ($m = 41$), được ánh xạ với các chỉ số từ $0$ đến $40$:

- **26 chữ cái:** `a-z` (bao gồm `f`, `j`, `w`... phục vụ quy ước dấu Telex).
- **10 chữ số:** `0-9`.
- **5 ký tự đặc biệt:** Dấu cách (SPACE), `.`, `,`, `!`, `?`.

Vì $41$ là một số nguyên tố, tập hợp $\mathbb{Z}_{41}$ tạo thành một Trường hữu hạn (Galois Field). Điều kiện để ma trận khóa $K$ cấp $n \times n$ khả nghịch là:

$$\det(K) \bmod 41 \neq 0$$

Mọi ma trận vuông thỏa mãn điều kiện trên đều chắc chắn tồn tại ma trận nghịch đảo $K^{-1} \pmod{41}$, được tính bằng công thức:

$$K^{-1} \equiv (\det(K))^{-1} \cdot \text{adj}(K) \pmod{41}$$

Trong đó, $(\det(K))^{-1}$ là nghịch đảo modulo của định thức, và $\text{adj}(K)$ là ma trận phụ hợp (chuyển vị của ma trận phần phụ đại số).

### 1.2. Thuật toán Mã hóa & Giải mã (Hill Cipher)

Giả sử chọn ma trận khóa $K$ cấp $3 \times 3$. Văn bản rõ được chia thành các vector khối $P_i = [p_1, p_2, p_3]^T$.

- **Mã hóa (Encryption):**

  $$C_i = (K \cdot P_i) \bmod 41$$

- **Giải mã (Decryption):**

  $$P_i = (K^{-1} \cdot C_i) \bmod 41$$

## 2. Tiền xử lý & Hậu xử lý Tiếng Việt

Hệ thống không sử dụng bảng ánh xạ hàng trăm ký tự Unicode cồng kềnh mà ứng dụng chuẩn Unicode NFD kết hợp quy ước Telex:

1. **Tiền xử lý (Preprocess):** Rã các ký tự Tiếng Việt có dấu (Unicode NFC) thành nguyên âm gốc và dấu thanh (Canonical Decomposition - NFD). Các dấu được chuyển thành ký tự Telex tương ứng (`f`, `s`, `x`, `r`, `j`, `a`, `w`).
   - *Ví dụ:* `"Gìn giữ"` $\rightarrow$ `"gifn giuwx"`.
2. **Đệm dữ liệu (Padding):** Nếu độ dài chuỗi không chia hết cho kích thước khối $n$ (ví dụ $n=3$), hệ thống tự động đệm ký tự Dấu cách (SPACE) vào cuối.
3. **Hậu xử lý (Postprocess):** Sau khi tính toán $P_i$ và khôi phục chuỗi Telex giải mã, hệ thống quét ngữ cảnh nguyên âm để quy đổi ngược ký tự Telex thành các Combining Mark và gộp lại về Unicode NFC chuẩn.

## 3. Kiến trúc E2EE Web Chat

Ứng dụng được xây dựng theo mô hình SPA (Single Page Application) sử dụng **Flask**, **Flask-SocketIO**, và **TailwindCSS**, mô phỏng môi trường mã hóa đầu cuối (E2EE):

- **Bảo mật kênh truyền:** Server chỉ đóng vai trò Router trung chuyển. Khi Sender gửi tin nhắn, hệ thống chỉ đẩy Ciphertext qua WebSocket tới Receiver. Server không bao giờ truyền bản rõ hay ma trận giải mã qua mạng.
- **Giải mã độc lập:** Người nhận nhận được một chuỗi mã hóa (Locked). Họ phải tự nhập đúng Ma trận Khóa $K$ trên giao diện của mình và thực thi giải mã thông qua API cục bộ.
- **Visualizer Toán học:** Cung cấp bộ công cụ xem log chi tiết (Trace), render trực quan các phép nhân vector khối với ma trận $K$ và $K^{-1}$ theo thời gian thực.

## 4. Cài đặt & Vận hành

### 4.1. Yêu cầu hệ thống

- Python $\ge 3.10$
- Trình duyệt Web hiện đại (Chrome, Edge, Firefox)

### 4.2. Cài đặt

1. Clone hoặc giải nén mã nguồn dự án.
2. Cài đặt các thư viện phụ thuộc:

   ```bash
   pip install -r requirements.txt
   ```

3. Khởi chạy server:

   ```bash
   python app.py
   ```

4. Truy cập giao diện ứng dụng:

   Mở trình duyệt và truy cập: http://127.0.0.1:5000

### 4.3. Hướng dẫn mô phỏng Chat 2 bên (Alice & Bob)

1. Mở 2 Tab ẩn danh (hoặc 2 trình duyệt khác nhau) để giả lập 2 Client.
2. Tại Tab 1, nhập tên Alice và tham gia phòng.
3. Tại Tab 2, nhập tên Bob và tham gia phòng.
4. **Trao đổi khóa:** Ở cả 2 Tab, thiết lập cấu hình chung một Ma trận Khóa $K$ hợp lệ. Bạn có thể bấm "🎲 Sinh khóa ngẫu nhiên" ở Tab 1, sau đó sao chép thủ công các số đó nhập vào Tab 2, rồi bấm "Kiểm tra $\det(K)$".
5. **Gửi tin:** Tab 1 nhập tin nhắn Tiếng Việt và bấm Gửi.
6. **Nhận tin & Giải mã:** Tab 2 sẽ nhận được chuỗi Ciphertext bị khóa. Bấm "🔓 Giải mã bằng khóa $K$ hiện tại" để hệ thống lấy ma trận $K$ của Bob tính toán $K^{-1}$ và khôi phục văn bản.
7. **Xem chi tiết:** Bấm vào nút "Trace Mã hóa / Giải mã" dưới mỗi bong bóng chat để mở Visualizer quan sát quá trình nhân ma trận $3 \times 3$.

## 5. Cấu trúc thư mục

```text
Plaintext.
├── app.py                      # Web Server chính (Flask + SocketIO + APIs)
├── core                        # Lõi thuật toán Toán học & Xử lý văn bản
│   ├── __init__.py
│   ├── char_set.py             # Bảng mã 41 ký tự & Mapping Index
│   ├── hill_math.py            # Phép toán Z_41: det, cofactor, inverse, encrypt
│   └── preprocessor.py         # NFD/Telex converter & NFC Restorer
├── static                      # Static assets cho Frontend
│   ├── css
│   │   └── style.css           # Custom styles (Ma trận Bracket, Animations)
│   └── js
│       ├── app.js              # Controller điều khiển UI, REST fetch, Chat logic
│       ├── socket_client.js    # Cấu hình Socket.IO client
│       └── visualizer.js       # Render bảng tính toán đại số ma trận lên DOM
├── templates
│   └── index.html              # Giao diện Web SPA (TailwindCSS)
├── tests                       # Unit tests
│   ├── test_math.py
│   └── test_preprocessor.py
├── requirements.txt            # Thư viện Python phụ thuộc
├── README.md                   # Tài liệu dự án
└── .gitignore                  # Git ignore rules
```
