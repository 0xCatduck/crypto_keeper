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
            with open(self.key_file, 'r') as f:  # 改為以讀取文本模式開啟
                self.key = bytes.fromhex(f.read())  # 將十六進位字符串轉換回二進制
        else:
            self.key = os.urandom(32)
            with open(self.key_file, 'w') as f:  # 改為以寫入文本模式開啟
                f.write(self.key.hex())  # 寫入十六進位字符串

        self.data = {}
        if os.path.exists(self.data_file):
            self.load_data()
        else:
            self.data['iv'] = os.urandom(16).hex()  # 初始化 IV 並以十六進位字符串保存
            self.save_data()

        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(bytes.fromhex(self.data['iv'])))


    def encrypt_data(self, plaintext):
        encryptor = self.cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt_data(self, encrypted_data):
        encrypted_data = base64.b64decode(encrypted_data.encode('utf-8'))
        decryptor = self.cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        try:
            unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
            return unpadded_data.decode('utf-8')
        except ValueError:
            print("Padding verification failed.")
            return None

    def encrypt_and_store(self, category, identifier, plaintext):
        encrypted_data = self.encrypt_data(plaintext)
        if category not in self.data:
            self.data[category] = {}
        self.data[category][identifier] = encrypted_data
        self.save_data()

    def decrypt_and_retrieve(self, category, identifier):
        if category in self.data:
            encrypted_data = self.data[category].get(identifier)
            if encrypted_data:
                return self.decrypt_data(encrypted_data)
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