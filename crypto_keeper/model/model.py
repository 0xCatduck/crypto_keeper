# crypto_keeper/model/model.py
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import json
import base64

class LegacyModel:
    def __init__(self, key_file='key.txt', data_file='legacy_data.json'):
        self.key_file = key_file
        self.data_file = data_file
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


    def encrypt_and_store(self, category, identifier, plaintext):
        #print(f"Encrypting data for {category}: {plaintext}")  
        encryptor = self.cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        if category not in self.data:
            self.data[category] = {}
        self.data[category][identifier] = base64.b64encode(encrypted_data).decode('utf-8')
        self.save_data()

    def decrypt_and_retrieve(self, category, identifier):
        if category in self.data:
            encrypted_data = self.data[category].get(identifier)
            #print(f"Retrieved encrypted data for {category}: {encrypted_data}") 
            if encrypted_data:
                encrypted_data = base64.b64decode(encrypted_data.encode('utf-8'))
                decryptor = self.cipher.decryptor()
                unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

                decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
                try:
                    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
                    #print(f"Decrypted data: {unpadded_data.decode('utf-8')}") 
                    return unpadded_data.decode('utf-8')
                except ValueError:
                    print("Padding verification failed.")
                    return None
        return None




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