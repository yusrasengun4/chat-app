# app.py
from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO
from extensions import socketio
from auth.routers import auth_bp
from api import users_api, groups_api, messages_api
import messaging.socket_handler  # Socket olayları burada

# Flask uygulaması
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = 'supersecretkey'

# Blueprint kayıtları
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(users_api, url_prefix='/api/users')
app.register_blueprint(groups_api, url_prefix='/api/groups')
app.register_blueprint(messages_api, url_prefix='/api/messages')

# SocketIO başlatma
socketio.init_app(app, cors_allowed_origins="*")

# ---- Web arayüzü yönlendirmeleri ---- #

@app.route('/')
def index():
    # Varsayılan olarak login sayfasına yönlendir
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Form verilerini al
        username = request.form.get('username')
        password = request.form.get('password')

        # Burada kullanıcı doğrulama işlemleri yapılır (örnek)
        if username and password:
            # Giriş başarılıysa sohbet sayfasına yönlendir
            return redirect(url_for('chat'))
        else:
            return render_template("login.html", error="Geçersiz kullanıcı adı veya şifre!")

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Form verilerini al
        username = request.form.get('username')
        password = request.form.get('password')

        # Burada kullanıcı veritabanına kaydedilir (örnek)
        print(f"Kayıt oldu: {username}")

        # Kayıt sonrası login sayfasına yönlendir
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/chat')
def chat():
    return render_template("chat.html")

# ---- Ana çalıştırma ---- #
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


