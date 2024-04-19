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

        has_valid_identifier = bool(identifier)
        can_save = self.can_save(category, has_valid_identifier)

        self.view.save_button.setEnabled(can_save)

    def has_valid_custom_fields(self):
        return any(
            name_widget.text().strip() and value_input.text().strip()
            for _, name_widget, value_input in self.view.custom_fields
        )

    def can_save(self, category, has_valid_identifier):
        if category == 'Others':
            has_valid_custom_fields = self.has_valid_custom_fields()
            return has_valid_identifier and has_valid_custom_fields
        else:
            data_fields = self.get_data_fields(category)
            has_valid_default_fields = any(field.strip() for field in data_fields)
            return has_valid_identifier and has_valid_default_fields

    def update_save_button_state(self):
        category = self.view.category_combo.currentText()
        identifier = self.view.identifier_input.text().strip()
        has_valid_identifier = bool(identifier)

        can_save = self.can_save(category, has_valid_identifier)
        self.view.save_button.setEnabled(can_save)

    def get_default_fields(self, category):
        if category == 'Wallet':
            return [self.view.wallet_seed_input, self.view.private_key_input]
        elif category == 'Exchange':
            return [
                self.view.exchange_account_input, self.view.exchange_password_input,
                self.view.google_2fa_input,self.view.auth_email_input,
                self.view.auth_phone_input,self.view.fund_password_input,
                self.view.identity_data_input
            ]
        return []


    def save_data(self):
        category = self.view.category_combo.currentText()
        identifier = self.view.identifier_input.text()

        if not self.confirm_overwrite(category, identifier):
            return

        data_fields = self.get_data_fields(category)
        custom_data = self.get_custom_data()

        all_data = ','.join(data_fields + custom_data)

        try:
            self.model.encrypt_and_store(category, identifier, all_data)
            self.view.remove_custom_fields()
            self.update_data_list(self.view.category_combo.currentIndex())
            self.view.clear_data_fields()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to save data: {str(e)}")

    def confirm_overwrite(self, category, identifier):
        if identifier in self.model.data.get(category, {}):
            reply = QMessageBox.question(
                self.view, 'Confirm Save',
                f"'{identifier}' already exists for '{category}'. Do you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    def get_data_fields(self, category):
        data_fields = []
        if category == 'Wallet':
            data_fields.append(self.view.wallet_seed_input.text())
            data_fields.append(self.view.private_key_input.text())
        elif category == 'Exchange':
            data_fields.extend([
                self.view.exchange_account_input.text(),
                self.view.exchange_password_input.text(),
                self.view.google_2fa_input.text(),
                self.view.auth_email_input.text(),
                self.view.auth_phone_input.text(),
                self.view.fund_password_input.text(),
                self.view.identity_data_input.text()
            ])
        return data_fields


    def get_custom_data(self):
        custom_data = []
        for custom_field_widget, name_input, value_input in self.view.custom_fields:
            name = name_input.text().strip()
            value = value_input.text().strip()
            if name and value:
                custom_data.append(f"{name}:{value}")
        return custom_data

    def retrieve_data(self):
        current_item = self.view.data_list.currentItem()
        if current_item is None:
            return

        category = self.view.category_combo.currentText()
        identifier = self.view.data_list.currentItem().text()
        decrypted_data = self.model.decrypt_and_retrieve(category, identifier)

        if decrypted_data is None:
            QMessageBox.warning(self.view, "Error", "Failed to retrieve data or decryption error, please check the key and try again.")
            return

        self.view.identifier_input.setText(identifier)
        data_parts = decrypted_data.split(',')

        self.view.remove_custom_fields()

        self.populate_default_fields(category, data_parts)
        self.populate_custom_fields(category, data_parts)

    def populate_default_fields(self, category, data_parts):
        if category == 'Wallet':
            if len(data_parts) >= 2:
                self.view.wallet_seed_input.setText(data_parts[0])
                self.view.private_key_input.setText(data_parts[1])
        elif category == 'Exchange':
            if len(data_parts) >= 7:
                self.view.exchange_account_input.setText(data_parts[0])
                self.view.exchange_password_input.setText(data_parts[1])
                self.view.google_2fa_input.setText(data_parts[2])
                self.view.auth_email_input.setText(data_parts[3])
                self.view.auth_phone_input.setText(data_parts[4])
                self.view.fund_password_input.setText(data_parts[5])
                self.view.identity_data_input.setText(data_parts[6])

    def populate_custom_fields(self, category, data_parts):
        custom_data_parts = []
        if category == 'Wallet':
            if len(data_parts) >= 2:
                custom_data_parts = data_parts[2:]
        elif category == 'Exchange':
            if len(data_parts) >= 7:
                custom_data_parts = data_parts[7:]
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

    def update_data_list_selection(self, current_item):
        self.view.enable_delete_button(current_item)

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

    def delete_data(self, identifier):
        category = self.view.category_combo.currentText()
        self.model.delete_data(category, identifier)  # 呼叫模型的 delete_data 方法
        self.update_data_list(self.view.category_combo.currentIndex())  # 更新數據列表


    # 添加一個方法來刪除數據
    def delete_data(self, identifier):
        category = self.view.category_combo.currentText()
        if identifier in self.model.data[category]:
            del self.model.data[category][identifier]
            self.model.save_data()  # 保存數據到文件
            self.update_data_list(self.view.category_combo.currentIndex())  # 更新列表