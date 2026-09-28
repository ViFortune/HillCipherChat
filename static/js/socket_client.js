// static/js/socket_client.js
const socket = io('http://127.0.0.1:5000');

socket.on('connect', () => {
    console.log('🔗 Đã kết nối tới Server Hill Cipher Socket.IO');
    // ĐÃ BỎ emit 'joint_chat' tự động ở đây để nhường cho màn hình Đăng nhập xử lý
});

socket.on('system_message', (data) => {
    console.log('System:', data.msg);
});

socket.on('error_message', (data) => {
    alert(`Lỗi hệ thống: ${data.error}`);
});