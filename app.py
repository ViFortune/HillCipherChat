# app.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import time

from core.char_set import MODULO, char_to_index, index_to_char
from core.hill_math import validate_key, get_matrix_inverse, process_vector, generate_key
from core.preprocessor import preprocess_text, postprocess_text, pad_text, unpad_text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hill_cipher_btl_secret_2026'

# Khởi tạo SocketIO với CORS cho phép kết nối linh hoạt
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================================
# 1. HELPER PIPELINE (Gói các bước Visualizer)
# ==========================================
def run_encryption_pipeline(text: str, K: list[list[int]]) -> dict:
    n = len(K)
    preprocessed = preprocess_text(text)
    padded, pad_len = pad_text(preprocessed, block_size=n)
    chunks_char = [padded[i:i+n] for i in range(0, len(padded), n)]
    chunks_idx = [[char_to_index(c) for c in chunk] for chunk in chunks_char]

    encrypted_idx = []
    matrix_steps = []

    for i, vec in enumerate(chunks_idx):
        enc_vec = process_vector(vec, K)
        encrypted_idx.append(enc_vec)
        matrix_steps.append({
            "block_index": i + 1,
            "plain_char": chunks_char[i],
            "plain_vec": vec,
            "cipher_vec": enc_vec,
            "cipher_char": "".join([index_to_char(idx) for idx in enc_vec])
        })

    flat_cipher_idx = [idx for vec in encrypted_idx for idx in vec]
    cipher_text = "".join([index_to_char(idx) for idx in flat_cipher_idx])
    K_inv = get_matrix_inverse(K)

    return {
        "raw_text": text,
        "preprocessed": preprocessed,
        "padded_text": padded,
        "pad_len": pad_len,
        "matrix_size": n,
        "key_matrix": K,
        "key_inverse": K_inv,
        "chunks_char": chunks_char,
        "chunks_idx": chunks_idx,
        "matrix_steps": matrix_steps,
        "ciphertext": cipher_text,
    }

def run_decryption_pipeline(ciphertext: str, K: list[list[int]]) -> dict:
    n = len(K)
    K_inv = get_matrix_inverse(K)

    chunks_char = [ciphertext[i:i+n] for i in range(0, len(ciphertext), n)]
    chunks_idx = [[char_to_index(c) for c in chunk] for chunk in chunks_char]

    decryted_idx = []
    matrix_steps = []

    for i, vec in enumerate(chunks_idx):
        dec_vec = process_vector(vec, K_inv)
        decryted_idx.append(dec_vec)
        matrix_steps.append({
            "block_index": i + 1,
            "cipher_char": chunks_char[i],
            "cipher_vec": vec,
            "plain_vec": dec_vec,
            "plain_char": "".join([index_to_char(idx) for idx in dec_vec])
        })

    flat_plain_idx = [idx for vec in decryted_idx for idx in vec]
    raw_decrypted = "".join([index_to_char(idx) for idx in flat_plain_idx])

    unpadded = unpad_text(raw_decrypted)
    restored_vietnamese = postprocess_text(unpadded)

    return {
        "ciphertext": ciphertext,
        "key_inverse": K_inv,
        "matrix_steps": matrix_steps,
        "raw_decrypted": raw_decrypted,
        "unpadded_text": unpadded,
        "restored_vietnamese": restored_vietnamese
    }

# ==========================================
# 2. HTTP REST API ENDPOINTS
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-key', methods=['POST'])
def api_generate_key():
    data = request.json or {}
    n = data.get('n', 3)
    try: 
        K = generate_key(n=n, m=MODULO)
        return jsonify({"success": True, "key": K, "modulo": MODULO})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/validate-key', methods=['POST'])
def api_validate_key():
    data = request.json or {}
    K = data.get('key', [])
    is_valid, msg = validate_key(K, m=MODULO)
    K_inv = get_matrix_inverse(K, m=MODULO) if is_valid else None
    return jsonify({"valid": is_valid, "message": msg, "key_inverse": K_inv})

# THÊM MỚI: API phục vụ giải mã độc lập tại Client
@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    data = request.json or {}
    ciphertext = data.get('ciphertext', '')
    K = data.get('key', [])

    is_valid, msg = validate_key(K, m=MODULO)
    if not is_valid:
        return jsonify({"success": False, "error": msg}), 400

    try:
        dec_trace = run_decryption_pipeline(ciphertext, K)
        return jsonify({"success": True, "trace": dec_trace})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ==========================================
# 3. WEBSOCKET REALTIME EVENTS
# ==========================================
@socketio.on('joint_chat')
def handle_join_chat(data):
    username = data.get('username', 'Anonymous')
    room = data.get('room', 'default_room')
    join_room(room)
    emit('system_message', {'msg': f"User '{username}' has join chat room."}, to=room)

@socketio.on('send_encryted_message')
def handle_send_message(data):
    sender_name = data.get('sender', 'Anonymous')
    room = data.get('room', 'room_alice_bob')
    text = data.get('text', '')
    K = data.get('key', [])
    # Lấy msg_id từ client gửi lên để đồng bộ UI
    msg_id = data.get('msg_id', str(int(time.time() * 1000))) 

    is_valid, msg = validate_key(K, m=MODULO)
    if not is_valid:
        emit('error_message', {'error': f"Invalid key matrix K: {msg}"})
        return

    # CHỈ chạy pipeline mã hóa tại server
    enc_trace = run_encryption_pipeline(text, K)
    ciphertext = enc_trace['ciphertext']

    # 1. Báo cáo thành công cho CHÍNH NGƯỜI GỬI (Kèm Trace để xem log mã hóa)
    emit('message_sent_success', {
        'msg_id': msg_id,
        'ciphertext': ciphertext,
        'trace': enc_trace
    }, to=request.sid)

    # 2. Broadcast bản mã cho NGƯỜI NHẬN (KHÔNG kèm trace giải mã, bắt buộc phải dùng API /api/decrypt)
    emit('receive_encrypted_message', {
        'msg_id': msg_id,
        'sender': sender_name,
        'ciphertext': ciphertext
    }, to=room, include_self=False)

if __name__ == '__main__':
    print(f"🚀 Server Hill Cipher đang chạy tại http://127.0.0.1:5000 (Modulo {MODULO})")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)