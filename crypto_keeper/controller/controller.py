# crypto_keeper/controller/controller.py
from PySide6.QtWidgets import QMessageBox, QLineEdit

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
        # 清除所有數據欄位
        self.view.clear_data_fields()
        # 清除所有自定義欄位
        self.view.remove_custom_fields()
        # 更新數據列表
        self.update_data_list(index)
        # 重新評估保存按鈕狀態
        self.update_save_button_state()


    def update_identifier(self, text):
        category = self.view.category_combo.currentText()
        identifier = text.strip()

        # 判斷是否有有效的 identifier
        has_valid_identifier = bool(identifier)

        # 初始設定為不能儲存
        can_save = False

        if category == 'Others':
            # 對於 "Others" 分類，確保有自定義欄位且欄位有值
            has_valid_custom_fields = any(
                name_widget.text().strip() and value_input.text().strip()
                for _, name_widget, value_input in self.view.custom_fields
            )
            can_save = has_valid_identifier and has_valid_custom_fields
        else:
            # 對於 "Wallet" 或 "Exchange"，確保至少有一個預設資料欄位被填寫
            data_fields = []
            if category == 'Wallet':
                data_fields = [self.view.wallet_seed_input, self.view.private_key_input]
            elif category == 'Exchange':
                data_fields = [
                    self.view.exchange_account_input, self.view.exchange_password_input,
                    self.view.google_2fa_input, self.view.phone_number_input,
                    self.view.auth_email_input, self.view.auth_phone_input,
                    self.view.fund_password_input, self.view.identity_data_input
                ]
            
            has_valid_default_fields = any(field.text().strip() for field in data_fields)
            can_save = has_valid_identifier and has_valid_default_fields

        self.view.save_button.setEnabled(can_save)

    def update_save_button_state(self):
        # 從視圖中檢索當前類別
        category = self.view.category_combo.currentText()
        identifier = self.view.identifier_input.text().strip()
        has_valid_identifier = bool(identifier)
        
        if category == 'Others':
            # 對於 "Others" 分類，確保有自定義欄位且欄位有值
            has_valid_custom_fields = any(
                name_widget.text().strip() and value_input.text().strip()
                for _, name_widget, value_input in self.view.custom_fields
            )
            self.view.save_button.setEnabled(has_valid_identifier and has_valid_custom_fields)
        else:
            # 對於 "Wallet" 或 "Exchange"，確保至少有一個預設資料欄位被填寫
            data_fields = self.get_default_fields(category)
            has_valid_default_fields = any(field.text().strip() for field in data_fields)
            self.view.save_button.setEnabled(has_valid_identifier and has_valid_default_fields)

    def get_default_fields(self, category):
        if category == 'Wallet':
            return [self.view.wallet_seed_input, self.view.private_key_input]
        elif category == 'Exchange':
            return [
                self.view.exchange_account_input, self.view.exchange_password_input,
                self.view.google_2fa_input, self.view.phone_number_input,
                self.view.auth_email_input, self.view.auth_phone_input,
                self.view.fund_password_input, self.view.identity_data_input
            ]
        return []


    def save_data(self):
        category = self.view.category_combo.currentText()
        identifier = self.view.identifier_input.text()

        # 預設資料欄位，根據類別來決定是否包含
        data_fields = []
        if category == 'Wallet':
            data_fields.append(self.view.wallet_seed_input.text())
            data_fields.append(self.view.private_key_input.text())
        elif category == 'Exchange':
            data_fields.extend([
                self.view.exchange_account_input.text(),
                self.view.exchange_password_input.text(),
                self.view.google_2fa_input.text(),
                self.view.phone_number_input.text(),
                self.view.auth_email_input.text(),
                self.view.auth_phone_input.text(),
                self.view.fund_password_input.text(),
                self.view.identity_data_input.text()
            ])

        # 將預設資料欄位與自定義欄位合併
        custom_data = []
        for custom_field_widget, name_input, value_input in self.view.custom_fields:
            name = name_input.text().strip()
            value = value_input.text().strip()
            if name and value:  # 確保名稱和值都不是空的
                custom_data.append(f"{name}:{value}")

        # 如果 data_fields 為空，則全部數據為自定義欄位
        all_data = ','.join(data_fields + custom_data)

        # 儲存加密的數據
        self.model.encrypt_and_store(category, identifier, all_data)
        self.view.remove_custom_fields()  # 儲存後移除自定義欄位
        self.update_data_list(self.view.category_combo.currentIndex())
        self.view.clear_data_fields()


    def retrieve_data(self):
        current_item = self.view.data_list.currentItem()
        if current_item is None:
            return
        category = self.view.category_combo.currentText()
        identifier = self.view.data_list.currentItem().text()
        decrypted_data = self.model.decrypt_and_retrieve(category, identifier)
        if decrypted_data is None:
            QMessageBox.warning(self.view, "Error", "Failed to retrieve data, please check the key.txt file.")
            return

        self.view.identifier_input.setText(identifier)
        data_parts = decrypted_data.split(',')

        # 移除之前的自定義欄位
        self.view.remove_custom_fields()

        custom_data_parts = []  # 初始化為空列表以避免 UnboundLocalError

        if category == 'Wallet':
            if len(data_parts) >= 2:
                self.view.wallet_seed_input.setText(data_parts[0])
                self.view.private_key_input.setText(data_parts[1])
                custom_data_parts = data_parts[2:]
        elif category == 'Exchange':
            if len(data_parts) >= 8:
                self.view.exchange_account_input.setText(data_parts[0])
                self.view.exchange_password_input.setText(data_parts[1])
                self.view.google_2fa_input.setText(data_parts[2])
                self.view.phone_number_input.setText(data_parts[3])
                self.view.auth_email_input.setText(data_parts[4])
                self.view.auth_phone_input.setText(data_parts[5])
                self.view.fund_password_input.setText(data_parts[6])
                self.view.identity_data_input.setText(data_parts[7])
                custom_data_parts = data_parts[8:]
        else:  # Others
            custom_data_parts = data_parts

        for custom_data in custom_data_parts:
            name_value_pair = custom_data.split(':', 1)
            if len(name_value_pair) == 2:
                name, value = name_value_pair
                self.view.add_custom_field(name.strip(), value.strip())
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