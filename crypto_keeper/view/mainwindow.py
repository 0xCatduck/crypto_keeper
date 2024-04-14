# crypto_keeper/view/mainwindow.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QListWidget, QLabel, QApplication, QListWidget, QToolTip
)
from PySide6.QtCore import QThread, Signal

class Mainwindow(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Digital Legacy Safe')
        layout = QVBoxLayout(self)

        # Category combo box
        category_layout = QHBoxLayout()
        category_label = QComboBox()
        category_label.addItems(['Wallet', 'Exchange'])
        self.category_combo = category_label
        category_layout.addWidget(category_label)
        layout.addLayout(category_layout)

        # Identifier input
        identifier_layout = QHBoxLayout()
        identifier_label = QLabel('Name:')
        self.identifier_input = QLineEdit()
        identifier_layout.addWidget(identifier_label)
        identifier_layout.addWidget(self.identifier_input)
        layout.addLayout(identifier_layout)

        # Data inputs
        self.data_input_widget = QWidget()
        self.data_input_layout = QVBoxLayout(self.data_input_widget)
        layout.addWidget(self.data_input_widget)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.save_button.setEnabled(False)
        self.retrieve_button = QPushButton('Retrieve')
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.retrieve_button)
        layout.addLayout(button_layout)

        # Data list
        self.data_list = QListWidget()
        layout.addWidget(self.data_list)

        # update data list when opening the window
        self.category_combo.currentIndexChanged.connect(self.update_data_inputs)
        self.update_data_inputs(0) 
        self.update_data_list(0)

        self.category_combo.currentIndexChanged.connect(self.update_data_inputs)
        self.update_data_inputs(0)

        # double click to copy data
        self.connect_data_input_events()

    def update_data_list(self, index):
        category = self.category_combo.itemText(index)
        self.data_list.clear()
        if category in self.model.data:
            self.data_list.addItems(self.model.data[category].keys())

    def update_data_inputs(self, index):
        for i in reversed(range(self.data_input_layout.count())):
            self.data_input_layout.itemAt(i).widget().setParent(None)

        if index == 0:  # Wallet
            wallet_seed_label = QLabel('Wallet Seed:')
            self.wallet_seed_input = QLineEdit()
            self.data_input_layout.addWidget(wallet_seed_label)
            self.data_input_layout.addWidget(self.wallet_seed_input)

            private_key_label = QLabel('Private Key:')
            self.private_key_input = QLineEdit()
            self.data_input_layout.addWidget(private_key_label)
            self.data_input_layout.addWidget(self.private_key_input)
        else:  # Exchange
            exchange_account_label = QLabel('Exchange Account:')
            self.exchange_account_input = QLineEdit()
            self.data_input_layout.addWidget(exchange_account_label)
            self.data_input_layout.addWidget(self.exchange_account_input)

            exchange_password_label = QLabel('Exchange Password:')
            self.exchange_password_input = QLineEdit()
            self.data_input_layout.addWidget(exchange_password_label)
            self.data_input_layout.addWidget(self.exchange_password_input)

            google_2fa_label = QLabel('Google 2FA:')
            self.google_2fa_input = QLineEdit()
            self.data_input_layout.addWidget(google_2fa_label)
            self.data_input_layout.addWidget(self.google_2fa_input)

            phone_number_label = QLabel('Phone Number:')
            self.phone_number_input = QLineEdit()
            self.data_input_layout.addWidget(phone_number_label)
            self.data_input_layout.addWidget(self.phone_number_input)

            auth_email_label = QLabel('Auth Email:')
            self.auth_email_input = QLineEdit()
            self.data_input_layout.addWidget(auth_email_label)
            self.data_input_layout.addWidget(self.auth_email_input)

            auth_phone_label = QLabel('Auth Phone:')
            self.auth_phone_input = QLineEdit()
            self.data_input_layout.addWidget(auth_phone_label)
            self.data_input_layout.addWidget(self.auth_phone_input)

            fund_password_label = QLabel('Fund Password:')
            self.fund_password_input = QLineEdit()
            self.data_input_layout.addWidget(fund_password_label)
            self.data_input_layout.addWidget(self.fund_password_input)

            identity_data_label = QLabel('Identity Data:')
            self.identity_data_input = QLineEdit()
            self.data_input_layout.addWidget(identity_data_label)
            self.data_input_layout.addWidget(self.identity_data_input)

    def connect_data_input_events(self):
        if self.category_combo.currentIndex() == 0:  # Wallet
            self.wallet_seed_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.wallet_seed_input)
            self.private_key_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.private_key_input)
        else:  # Exchange
            self.exchange_account_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.exchange_account_input)
            self.exchange_password_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.exchange_password_input)
            self.google_2fa_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.google_2fa_input)
            self.phone_number_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.phone_number_input)
            self.auth_email_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.auth_email_input)
            self.auth_phone_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.auth_phone_input)
            self.fund_password_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.fund_password_input)
            self.identity_data_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.identity_data_input)

    def copy_to_clipboard(self, input_field):
        input_field.selectAll()
        QApplication.clipboard().setText(input_field.selectedText())


    def clear_data_fields(self):
        self.identifier_input.clear()
        if self.category_combo.currentIndex() == 0:  # Wallet
            self.wallet_seed_input.clear()
            self.private_key_input.clear()
        else:  # Exchange
            self.exchange_account_input.clear()
            self.exchange_password_input.clear()
            self.google_2fa_input.clear()
            self.phone_number_input.clear()
            self.auth_email_input.clear()
            self.auth_phone_input.clear()
            self.fund_password_input.clear()
            self.identity_data_input.clear()
