from cryptography.fernet import Fernet

# Генерация случайного ключа
key = Fernet.generate_key()

# Вывод сгенерированного ключа
print("Сгенерированный ключ:", key)