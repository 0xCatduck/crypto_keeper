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
        self.view.delete_button.clicked.connect(self.confirm_delete)

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
        custom_data = []
        for custom_field_widget, name_input, value_input in self.view.custom_fields:
            name = name_input.text().strip()
            value = value_input.text().strip()
            if name and value:  # 確保名稱和值都不是空的
                custom_data.append(f"{name}:{value}")

        
        all_data = [data] + custom_data  # 組合預設欄位和自定義欄位的數據
        final_data = ','.join(all_data)
        
        self.model.encrypt_and_store(category, identifier, final_data)
        self.view.remove_custom_fields()  # 儲存後移除自定義欄位
        self.update_data_list(self.view.category_combo.currentIndex())
        self.view.clear_data_fields()

    def retrieve_data(self):
        category = self.view.category_combo.currentText()
        identifier = self.view.data_list.currentItem().text()
        decrypted_data = self.model.decrypt_and_retrieve(category, identifier)
        if decrypted_data is None:
            QMessageBox.warning(self.view, "Error", "Unable to read key.txt file. Please ensure it is in the same directory as legacy_data.json.")
            return

        self.view.identifier_input.setText(identifier)
        data_parts = decrypted_data.split(',')

        # 移除之前的自定義欄位
        self.view.remove_custom_fields()

        if category == 'Wallet':
            # 確保有足夠的資料來填充預設欄位
            if len(data_parts) >= 2:
                self.view.wallet_seed_input.setText(data_parts[0])
                self.view.private_key_input.setText(data_parts[1])
                custom_data_parts = data_parts[2:]  # 剩餘的視為自定義欄位
            for custom_data in custom_data_parts:
                name_value_pair = custom_data.split(':', 1)
                if len(name_value_pair) == 2:
                    name, value = name_value_pair
                    self.view.add_custom_field()
                    # 正確設置 QLineEdit 的文本
                    self.view.custom_fields[-1][1].setText(name.strip())  # 設置名稱欄位的文本
                    self.view.custom_fields[-1][2].setText(value.strip())  # 設置值欄位的文本
                else:
                    QMessageBox.warning(self.view, "Error", f"Invalid custom field format: {custom_data}")
                    return
        else:  # Exchange
            # ... 為交易所設置欄位 ...
            # 確保有足夠的資料來填充交易所的欄位
            if len(data_parts) >= 8:
                self.view.exchange_account_input.setText(data_parts[0])
                self.view.exchange_password_input.setText(data_parts[1])
                self.view.google_2fa_input.setText(data_parts[2])
                self.view.phone_number_input.setText(data_parts[3])
                self.view.auth_email_input.setText(data_parts[4])
                self.view.auth_phone_input.setText(data_parts[5])
                self.view.fund_password_input.setText(data_parts[6])
                self.view.identity_data_input.setText(data_parts[7])
                custom_data_parts = data_parts[8:]  # 剩餘的視為自定義欄位
            for custom_data in custom_data_parts:
                name_value_pair = custom_data.split(':', 1)
                if len(name_value_pair) == 2:
                    name, value = name_value_pair
                    self.view.add_custom_field()
                    # 正確設置 QLineEdit 的文本
                    self.view.custom_fields[-1][1].setText(name.strip())  # 設置名稱欄位的文本
                    self.view.custom_fields[-1][2].setText(value.strip())  # 設置值欄位的文本
                else:
                    QMessageBox.warning(self.view, "Error", f"Invalid custom field format: {custom_data}")
                    return


    def update_data_list(self, index):
        category = self.view.category_combo.itemText(index)
        self.view.data_list.clear()
        if category in self.model.data:
            self.view.data_list.addItems(self.model.data[category].keys())

    def update_data_list_selection(self, row):
        if row >= 0:
            self.view.clear_data_fields()

    # 添加一個方法來處理刪除事件
    def confirm_delete(self):
        selected_item = self.view.data_list.currentItem()
        if selected_item:
            reply = QMessageBox.question(
                self.view, 
                'Confirm Delete', 
                f"Are you sure you want to delete '{selected_item.text()}'?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.delete_data(selected_item.text())


    # 添加一個方法來刪除數據
    def delete_data(self, identifier):
        category = self.view.category_combo.currentText()
        if identifier in self.model.data[category]:
            del self.model.data[category][identifier]
            self.model.save_data()  # 保存數據到文件
            self.update_data_list(self.view.category_combo.currentIndex())  # 更新列表