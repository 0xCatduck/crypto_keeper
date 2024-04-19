# crypto_keeper/model/model.py
import os
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import json
import base64
import platform

def get_app_dir():
    base_path = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))

    # 檢查是否在 macOS 的 .app 包内
    if base_path.endswith('MacOS') and platform.system() == 'Darwin':
        # 向上三级是.app外
        return os.path.abspath(os.path.join(base_path, os.pardir, os.pardir, os.pardir))
    elif os.path.exists(os.path.join(base_path, 'exe_marker.txt')):
        # 是 Windows 或 Linux 下的 .exe 或其他封裝形式
        return base_path
    elif os.path.exists(os.path.join(base_path, 'app_marker.txt')):
        # 是 .app 封装，但不在 MacOS 目錄下
        return os.path.abspath(os.path.join(base_path, os.pardir, os.pardir, os.pardir))

    # 判斷是否直接運行 Python 檔案
    if not getattr(sys, 'frozen', False):
        # 假設 model.py 位於 main.py 的子目錄，則回到上級目錄
        return os.path.abspath(os.path.join(base_path, os.pardir))
    
    return base_path  # 默認返回當前路徑

class LegacyModel:
    def __init__(self, key_file='key.txt', data_file='legacy_data.json'):
        app_dir = get_app_dir()
        data_dir = os.path.join(app_dir, 'CryptoKeeperData')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        self.key_file = os.path.join(data_dir, key_file)
        self.data_file = os.path.join(data_dir, data_file)
        
        self.load_key_and_data()

    def load_key_and_data(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'r') as f:
                self.key = bytes.fromhex(f.read())
        else:
            self.key = os.urandom(32)
            with open(self.key_file, 'w') as f:
                f.write(self.key.hex())

        self.data = {}
        if os.path.exists(self.data_file):
            self.load_data()

    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading from file: {e}")



    def encrypt_data(self, plaintext):
        # Generate a new random IV
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Prepare the plaintext for encryption
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        
        # Encrypt the data
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return the IV along with the encrypted data, here encoded in base64
        return base64.b64encode(iv + encrypted_data).decode('utf-8')

    def decrypt_data(self, encrypted_data):
        # Decode the data from base64
        encrypted_data_with_iv = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # Extract the IV and encrypted data
        iv = encrypted_data_with_iv[:16]
        encrypted_data = encrypted_data_with_iv[16:]
        
        # Create a Cipher object using the extracted IV
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        # Decrypt and depad the data
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        
        return unpadded_data.decode('utf-8')


    def encrypt_and_store(self, category, identifier, plaintext):
        encrypted_data = self.encrypt_data(plaintext)
        if category not in self.data:
            self.data[category] = {}
        self.data[category][identifier] = encrypted_data
        self.save_data()

    def decrypt_and_retrieve(self, category, identifier):
        encrypted_data = self.data[category].get(identifier)
        if encrypted_data:
            try:
                return self.decrypt_data(encrypted_data)
            except ValueError as e:
                print(f"Decryption error: {e}")
                return None
        return None

    def delete_data(self, category, identifier):
        if category in self.data and identifier in self.data[category]:
            del self.data[category][identifier]
            self.save_data()




    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                # 使用 indent=4 來美化輸出，使 JSON 文件具有縮進，更易於閱讀
                json.dump(self.data, f, indent=4, sort_keys=True)
        except IOError as e:
            print(f"Error writing to file: {e}")

    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading from file: {e}")