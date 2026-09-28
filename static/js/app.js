// static/js/app.js
const MATRIX_SIZE = 3;
let currentKeyMatrix = [];
let myUsername = '';
let traceHistory = {}; 

// ==========================================
// A. QUẢN LÝ MA TRẬN KHÓA K
// ==========================================
function initKeyGrid() {
    const grid = document.getElementById('key-matrix-input');
    grid.innerHTML = '';
    for (let i = 0; i < MATRIX_SIZE; i++) {
        for (let j = 0; j < MATRIX_SIZE; j++) {
            grid.innerHTML += `<input type="number" id="k_${i}_${j}" class="w-10 h-8 text-center border rounded text-sm" value="0">`;
        }
    }
}

function getKeyFromUI() {
    let matrix = [];
    for (let i = 0; i < MATRIX_SIZE; i++) {
        let row = [];
        for (let j = 0; j < MATRIX_SIZE; j++) {
            row.push(parseInt(document.getElementById(`k_${i}_${j}`).value) || 0);
        }
        matrix.push(row);
    }
    return matrix;
}

function updateKeyToUI(matrix) {
    for (let i = 0; i < MATRIX_SIZE; i++) {
        for (let j = 0; j < MATRIX_SIZE; j++) {
            document.getElementById(`k_${i}_${j}`).value = matrix[i][j];
        }
    }
    currentKeyMatrix = matrix;
}

document.getElementById('btn-gen-key').addEventListener('click', async () => {
    const res = await fetch('/api/generate-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n: MATRIX_SIZE })
    }).then(r => r.json());

    if (res.success) {
        updateKeyToUI(res.key);
        document.getElementById('key-status').innerHTML = '<span class="text-blue-500">Đã sinh khóa mới.</span>';
    }
});

document.getElementById('btn-validate-key').addEventListener('click', async () => {
    const K = getKeyFromUI();
    const res = await fetch('/api/validate-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: K })
    }).then(r => r.json());

    const statusEl = document.getElementById('key-status');
    if (res.valid) {
        statusEl.innerHTML = `<span class="text-green-600">Khả nghịch! det(K) ≠ 0</span>`;
        currentKeyMatrix = K;
    } else {
        statusEl.innerHTML = `<span class="text-red-600 text-xs">${res.message}</span>`;
    }
});

// ==========================================
// B. QUẢN LÝ GIAO DIỆN CHAT (2 TAB)
// ==========================================
document.getElementById('btn-join').addEventListener('click', () => {
    myUsername = document.getElementById('username-input').value.trim();
    if (!myUsername) return;

    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('chat-screen').classList.replace('hidden', 'flex');
    document.getElementById('my-name-display').innerText = `(${myUsername})`;

    socket.emit('joint_chat', { username: myUsername, room: 'room_alice_bob' });
});

document.getElementById('btn-send').addEventListener('click', () => {
    const text = document.getElementById('chat-input').value.trim();
    if (!text) return;
    
    currentKeyMatrix = getKeyFromUI();
    const msgId = Date.now().toString(); // Khởi tạo ID tin nhắn từ client

    socket.emit('send_encryted_message', {
        msg_id: msgId,
        sender: myUsername,
        room: 'room_alice_bob',
        text: text,
        key: currentKeyMatrix
    });
    document.getElementById('chat-input').value = '';
});

// Người gửi: Nhận lại Trace mã hóa để xem
socket.on('message_sent_success', (data) => {
    const msgId = data.msg_id;
    traceHistory[msgId] = { type: 'encode', trace: data.trace };

    const html = `
        <div class="flex flex-col items-end self-end max-w-[80%]">
            <div class="bg-blue-500 text-white p-3 rounded-l-lg rounded-tr-lg shadow">
                <p class="text-xs text-blue-200 mb-1">Đã gửi mã hóa:</p>
                <p class="font-mono text-sm break-all">${data.ciphertext}</p>
            </div>
            <button onclick="viewTrace('${msgId}')" class="mt-1 text-xs text-blue-600 underline">Trace Mã hóa</button>
        </div>
    `;
    document.getElementById('chat-messages').insertAdjacentHTML('beforeend', html);
});

// Người nhận: CHỈ NHẬN CIPHERTEXT
socket.on('receive_encrypted_message', (data) => {
    const msgId = data.msg_id;
    // Lưu tạm ciphertext, trạng thái 'locked'
    traceHistory[msgId] = { type: 'locked', ciphertext: data.ciphertext };

    const html = `
        <div id="msg-container-${msgId}" class="flex flex-col items-start self-start max-w-[80%] w-full">
            <p class="text-xs text-gray-500 mb-1">${data.sender}</p>
            <div class="bg-gray-100 border border-gray-300 p-3 rounded-r-lg rounded-tl-lg shadow w-full">
                <p class="text-xs text-red-500 font-bold mb-1">🔒 Bản mã (Ciphertext):</p>
                <p class="font-mono text-gray-800 break-all text-sm">${data.ciphertext}</p>
            </div>
            <button onclick="attemptDecrypt('${msgId}')" class="mt-2 text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded hover:bg-blue-200 border border-blue-300">
                🔓 Giải mã bằng khóa $K$ hiện tại
            </button>
        </div>
    `;
    document.getElementById('chat-messages').insertAdjacentHTML('beforeend', html);
});

// Nút bấm thực hiện giải mã bằng ma trận của người nhận
window.attemptDecrypt = async function(msgId) {
    const record = traceHistory[msgId];
    if (!record || record.type !== 'locked') return;

    const K = getKeyFromUI();
    
    // Gọi API để giải mã
    const res = await fetch('/api/decrypt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ciphertext: record.ciphertext, key: K })
    }).then(r => r.json());

    if (res.success) {
        // Cập nhật record với Trace giải mã
        traceHistory[msgId] = { type: 'decode', trace: res.trace };
        
        // Render lại UI của tin nhắn đó
        const container = document.getElementById(`msg-container-${msgId}`);
        container.innerHTML = `
            <p class="text-xs text-green-600 mb-1 font-bold">🔓 Đã giải mã thành công</p>
            <div class="bg-green-50 border border-green-300 p-3 rounded-r-lg rounded-tl-lg shadow w-full">
                <p class="text-gray-800">${res.trace.restored_vietnamese}</p>
            </div>
            <button onclick="viewTrace('${msgId}')" class="mt-1 text-xs text-green-700 underline font-semibold">Xem Trace Giải mã</button>
        `;
    } else {
        alert("Khóa giải mã sai hoặc không hợp lệ: " + res.error);
    }
};

window.viewTrace = function(msgId) {
    const record = traceHistory[msgId];
    if(record && record.type !== 'locked') {
        openVisualizerModal(record.type, record.trace);
    }
};

// Khởi tạo ban đầu
initKeyGrid();