# test_database.py oluştur
from database import init_db, register_user, authenticate_user

# Veritabanını başlat
init_db()

# Test kullanıcısı oluştur
success, user_id = register_user('test', 'test123', 'test@example.com')
print(f"Kayıt: {success}, ID: {user_id}")

# Giriş yap
success, user = authenticate_user('test', 'test123')
print(f"Giriş: {success}, Kullanıcı: {user}")