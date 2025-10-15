from flask_socketio import SocketIO
import socket, threading, json

class TCPBridge:
    def __init__(self, socketio: SocketIO, host='localhost', port=9999, session_id=None):
        self.socketio = socketio
        self.host = host
        self.port = port
        self.session_id = session_id
        self.socket = None
        self.connected = False
        self.receive_thread = None

    def connect_to_tcp_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.connected = True
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()
    
    def send_message(self, message):
        self.socket.send(json.dumps(message).encode('utf-8'))

    def receive_messages(self):
        while self.connected:
            data = self.socket.recv(4096).decode('utf-8')
            if not data: break
            message = json.loads(data)
            # session_id’ye bağlı WebSocket’e gönder
            self.socketio.emit('tcp_message', message, room=self.session_id)