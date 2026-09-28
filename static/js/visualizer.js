// static/js/visualizer.js

// Hàm phụ trợ vẽ vector (dấu ngoặc vuông ma trận)
function renderVector(vec) {
    return `<div class="matrix-bracket text-sm">${vec.map(v => `<span>${v}</span>`).join('')}</div>`;
}

function openVisualizerModal(type, traceData) {
    const content = document.getElementById('visualizer-content');
    let html = '';

    if (type === 'encode') {
        html = `
            <h2 class="text-xl font-bold text-blue-700 border-b pb-2 mb-4">Góc nhìn Người gửi: Quá trình Mã hóa</h2>
            
            <section class="mb-6">
                <h3 class="font-bold text-gray-700 mb-3">1. Tiền xử lý Văn bản (NFD + Telex)</h3>
                <div class="grid grid-cols-3 gap-4 text-center">
                    <div class="bg-gray-100 p-3 rounded">
                        <p class="text-xs text-gray-500">Văn bản gốc</p>
                        <p class="font-mono font-bold mt-1">'${traceData.raw_text}'</p>
                    </div>
                    <div class="bg-gray-100 p-3 rounded">
                        <p class="text-xs text-gray-500">Chuỗi NFD/Telex</p>
                        <p class="font-mono font-bold mt-1 text-orange-600">'${traceData.preprocessed}'</p>
                    </div>
                    <div class="bg-gray-100 p-3 rounded">
                        <p class="text-xs text-gray-500">Sau khi Padding (Đệm khoảng trắng)</p>
                        <p class="font-mono font-bold mt-1 text-green-600">'${traceData.padded_text}'</p>
                    </div>
                </div>
            </section>

            <section>
                <h3 class="font-bold text-gray-700 mb-3">2. Mã hóa Khối (C = K * P mod Modulo)</h3>
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white border text-center text-sm">
                        <thead class="bg-blue-50">
                            <tr>
                                <th class="py-2 border">Khối</th>
                                <th class="py-2 border">Ký tự thô</th>
                                <th class="py-2 border">Vector Rõ (P)</th>
                                <th class="py-2 border">Vector Mã (C)</th>
                                <th class="py-2 border">Ký tự Mã</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${traceData.matrix_steps.map(step => `
                            <tr>
                                <td class="py-2 border font-bold">#${step.block_index}</td>
                                <td class="py-2 border font-mono">'${step.plain_char}'</td>
                                <td class="py-2 border">${renderVector(step.plain_vec)}</td>
                                <td class="py-2 border">${renderVector(step.cipher_vec)}</td>
                                <td class="py-2 border font-mono font-bold text-red-600">'${step.cipher_char}'</td>
                            </tr>`).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="mt-2 bg-gray-100 p-2 rounded text-sm text-center">
                    <b>Ciphertext hoàn chỉnh gửi đi:</b> <span class="font-mono text-red-600 text-lg">${traceData.ciphertext}</span>
                </div>
            </section>
        `;
    } else if (type === 'decode') {
        html = `
            <h2 class="text-xl font-bold text-green-700 border-b pb-2 mb-4">Góc nhìn Người nhận: Quá trình Giải mã</h2>
            
            <div class="mb-6 bg-gray-100 p-4 rounded text-center">
                <p class="text-sm font-bold text-gray-600">Ciphertext nhận được qua mạng:</p>
                <p class="font-mono text-red-600 text-lg mt-1">'${traceData.ciphertext}'</p>
            </div>

            <section class="mb-6">
                <h3 class="font-bold text-gray-700 mb-3">1. Giải mã Khối (P = K⁻¹ * C mod Modulo)</h3>
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white border text-center text-sm">
                        <thead class="bg-green-50">
                            <tr>
                                <th class="py-2 border">Khối</th>
                                <th class="py-2 border">Ký tự Mã</th>
                                <th class="py-2 border">Vector Mã (C)</th>
                                <th class="py-2 border">Vector Rõ (P)</th>
                                <th class="py-2 border">Khôi phục Ký tự</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${traceData.matrix_steps.map(step => `
                            <tr>
                                <td class="py-2 border font-bold">#${step.block_index}</td>
                                <td class="py-2 border font-mono text-red-600">'${step.cipher_char}'</td>
                                <td class="py-2 border">${renderVector(step.cipher_vec)}</td>
                                <td class="py-2 border">${renderVector(step.plain_vec)}</td>
                                <td class="py-2 border font-mono font-bold text-blue-600">'${step.plain_char}'</td>
                            </tr>`).join('')}
                        </tbody>
                    </table>
                </div>
            </section>

            <section>
                <h3 class="font-bold text-gray-700 mb-3">2. Hậu xử lý (NFC Khôi phục)</h3>
                <div class="grid grid-cols-2 gap-4 text-center">
                    <div class="bg-gray-100 p-3 rounded border">
                        <p class="text-xs text-gray-500">Giải mã thô (Chưa Unpad & NFC)</p>
                        <p class="font-mono font-bold mt-1">'${traceData.raw_decrypted}'</p>
                    </div>
                    <div class="bg-green-100 p-3 rounded border border-green-300">
                        <p class="text-xs text-green-700">Khôi phục Tiếng Việt hoàn chỉnh</p>
                        <p class="font-mono font-bold mt-1 text-lg text-green-800">'${traceData.restored_vietnamese}'</p>
                    </div>
                </div>
            </section>
        `;
    }

    content.innerHTML = html;
    document.getElementById('visualizer-modal').classList.replace('hidden', 'flex');
}

// Bắt sự kiện đóng modal
document.getElementById('btn-close-modal').addEventListener('click', () => {
    document.getElementById('visualizer-modal').classList.replace('flex', 'hidden');
});