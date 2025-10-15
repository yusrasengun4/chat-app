# core/tcp_server.py
import socket
import threading
import json
from database.queries import verify_user, save_message, get_online_users

class TCPServer:
    """Mevcut TCP sunucunuzun kodunu buraya taşıyın"""
    
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {socket: user_info}
        self.running = False
    
    def start(self):
        """Sunucuyu başlat"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"🚀 TCP Sunucu başlatıldı: {self.host}:{self.port}")
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"✅ Yeni bağlantı: {address}")
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                ).start()
            except Exception as e:
                if self.running:
                    print(f"❌ Hata: {e}")
    
    def handle_client(self, client_socket, address):
        """İstemciyi yönet - Mevcut kodunuzu buraya ekleyin"""
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                # Mesajı işle
                message = json.loads(data)
                self.process_message(client_socket, message)
        
        except Exception as e:
            print(f"❌ İstemci hatası: {e}")
        finally:
            self.remove_client(client_socket)
            client_socket.close()
    
    def process_message(self, client_socket, message):
        """Mesajı işle"""
        msg_type = message.get('type')
        
        if msg_type == 'login':
            self.handle_login(client_socket, message)
        elif msg_type == 'message':
            self.handle_message(client_socket, message)
        # ... diğer mesaj tipleri
    
    def handle_login(self, client_socket, message):
        """Login işlemi"""
        username = message.get('username')
        password = message.get('password')
        
        success, user = verify_user(username, password)
        
        if success:
            self.clients[client_socket] = user
            response = {'type': 'login_response', 'success': True, 'user': user}
        else:
            response = {'type': 'login_response', 'success': False, 'error': 'Geçersiz kullanıcı'}
        
        client_socket.send(json.dumps(response).encode('utf-8'))
    
    def handle_message(self, client_socket, message):
        """Mesaj gönderimi"""
        # Mevcut mesaj gönderme kodunuzu buraya ekleyin
        pass
    
    def remove_client(self, client_socket):
        """İstemciyi kaldır"""
        if client_socket in self.clients:
            user = self.clients[client_socket]
            print(f"👋 {user['username']} ayrıldı")
            del self.clients[client_socket]
    
    def stop(self):
        """Sunucuyu durdur"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

# Standalone çalıştırma
if __name__ == '__main__':
    from database.db_manager import init_db
    init_db()
    
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Sunucu durduruluyor...")
        server.stop()