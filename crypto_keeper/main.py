# Application Name: Crypto Keeper
# Version: 1.0.0
# Encoding: UTF-8
# Release Date: 2024-04-19
# Description: Crypto Keeper is a simple password manager designed specifically for cryptocurrency users. 
#              It provides secure and easy management of your crypto-related credentials.
# Author: 0xCatduck
# Download URL: https://github.com/0xCatduck/crypto_keeper


# crypto_keeper/main.py
import sys
import os

# 獲取當前文件的路徑
current_dir = os.path.dirname(os.path.abspath(__file__))

# 獲取上級目錄的路徑
parent_dir = os.path.dirname(current_dir)

# 將上級目錄添加到 sys.path
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from PySide6.QtWidgets import QApplication
from model.model import LegacyModel
from controller.controller import Controller
from view.mainwindow import Mainwindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = LegacyModel()
    view = Mainwindow(model)
    controller = Controller(model, view)

    view.show()
    sys.exit(app.exec())