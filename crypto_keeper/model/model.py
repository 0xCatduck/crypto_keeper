# crypto_keeper/model/model.py
import os
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import json
import base64

class LegacyModel:
    def __init__(self, key_file='key.txt', data_file='legacy_data.json'):
        # 確定應用程序的可執行文件所在的目錄
        if getattr(sys, 'frozen', False):
            # 如果應用程序被打包，使用 sys.executable 獲得路徑
            app_dir = os.path.dirname(sys.executable)
        else:
            # 如果應用程序未被打包，使用當前腳本的目錄
            app_dir = os.path.dirname(os.path.abspath(__file__))

        # 創建一個名為 'data' 的子資料夾
        data_dir = os.path.join(app_dir, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)  # 如果 'data' 資料夾不存在，則創建它

        # 組合 key 和 data 文件的完整路徑
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