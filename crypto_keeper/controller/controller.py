# crypto_keeper/controller/controller.py
from PySide6.QtWidgets import QMessageBox

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.connect_signals()

    def connect_signals(self):
        self.view.category_combo.currentIndexChanged.connect(self.update_category)
        self.view.identifier_input.textChanged.connect(self.update_identifier)
        self.view.save_button.clicked.connect(self.save_data)
        self.view.retrieve_button.clicked.connect(self.retrieve_data)
        self.view.data_list.currentRowChanged.connect(self.update_data_list_selection)

    def update_category(self, index):
        self.view.clear_data_fields()
        self.update_data_list(index)

    def update_identifier(self, text):
        self.view.save_button.setEnabled(bool(text))

    def save_data(self):
        category = self.view.category_combo.currentText()
        identifier = self.view.identifier_input.text()
        if category == 'Wallet':
            data = ','.join([self.view.wallet_seed_input.text(), self.view.private_key_input.text()])
        else:  # Exchange
            data = ','.join([
                self.view.exchange_account_input.text(),
                self.view.exchange_password_input.text(),
                self.view.google_2fa_input.text(),
                self.view.phone_number_input.text(),
                self.view.auth_email_input.text(),
                self.view.auth_phone_input.text(),
                self.view.fund_password_input.text(),
                self.view.identity_data_input.text()
            ])
        self.model.encrypt_and_store(category, identifier, data)
        self.update_data_list(self.view.category_combo.currentIndex())
        self.view.clear_data_fields()

    def retrieve_data(self):
        category = self.view.category_combo.currentText()
        identifier = self.view.data_list.currentItem().text()
        decrypted_data = self.model.decrypt_and_retrieve(category, identifier)
        if decrypted_data is None:  # 檢查返回值是否為 None
            QMessageBox.warning(self.view, "Error", "Unable to read key.txt file. Please ensure it is in the same directory as legacy_data.json.")
            return

        if decrypted_data:
            self.view.identifier_input.setText(identifier)
            if category == 'Wallet':
                data1, data2 = decrypted_data.split(',')
                self.view.wallet_seed_input.setText(data1)
                self.view.private_key_input.setText(data2)
            else:  # Exchange
                data1, data2, data3, data4, data5, data6, data7, data8 = decrypted_data.split(',')
                self.view.exchange_account_input.setText(data1)
                self.view.exchange_password_input.setText(data2)
                self.view.google_2fa_input.setText(data3)
                self.view.phone_number_input.setText(data4)
                self.view.auth_email_input.setText(data5)
                self.view.auth_phone_input.setText(data6)
                self.view.fund_password_input.setText(data7)
                self.view.identity_data_input.setText(data8)
        else:
            QMessageBox.warning(self.view, "Error", "No data found.")

    def update_data_list(self, index):
        category = self.view.category_combo.itemText(index)
        self.view.data_list.clear()
        if category in self.model.data:
            self.view.data_list.addItems(self.model.data[category].keys())

    def update_data_list_selection(self, row):
        if row >= 0:
            self.view.clear_data_fields()