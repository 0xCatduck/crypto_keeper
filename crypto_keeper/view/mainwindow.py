# crypto_keeper/view/mainwindow.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QListWidget, QLabel, QApplication, QListWidget, QSizePolicy, QScrollArea
)
from PySide6.QtGui import QFont
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
import os
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return sys._MEIPASS
    else:
        # The application is not frozen
        # 返回 view 資料夾的位置
        return os.path.dirname(os.path.abspath(__file__))

class Mainwindow(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.init_ui()
        self.custom_fields = []
        self.resize(600, 800)

    def init_ui(self):
        self.setWindowTitle('Crypto Keeper')
        layout = QVBoxLayout(self)

        # Set size policy for the main layout
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(size_policy)

        # Add icon
        base_dir = get_base_dir()
        icon_path = os.path.join(base_dir, 'icon.png')
        self.setWindowIcon(QIcon(icon_path))

        # Category combo box
        category_layout = QHBoxLayout()
        category_label = QComboBox()
        category_label.addItems(['Wallet', 'Exchange', 'Others'])
        self.category_combo = category_label
        category_layout.addWidget(category_label)
        layout.addLayout(category_layout)

        # Set font size for the main window and all children widgets
        base_font = QFont()
        base_font.setPointSize(12)  # 設置基礎字體大小
        self.setFont(base_font)

        # Identifier input
        identifier_layout = QHBoxLayout()
        identifier_label = QLabel('Name:')
        self.identifier_input = QLineEdit()
        self.identifier_input.textChanged.connect(self.update_save_button_state)
        identifier_layout.addWidget(identifier_label)
        identifier_layout.addWidget(self.identifier_input)
        layout.addLayout(identifier_layout)

        # Data inputs
        self.data_input_widget = QWidget()
        self.data_input_layout = QVBoxLayout(self.data_input_widget)
        self.data_input_layout.setAlignment(Qt.AlignTop)  # 確保內容對齊頂部

        # 將 data_input_widget 封裝在 QScrollArea 中
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.data_input_widget)
        layout.addWidget(self.scroll_area)

        # Set size policy for data_input_widget to allow minimum size
        self.data_input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.scroll_area.setStyleSheet("QScrollArea { background-color: #333; }"
                                       "QScrollBar:vertical { background: #333; }")


        # Buttons
        button_layout = QHBoxLayout()
        self.add_field_button = QPushButton('Add Custom Field')
        self.add_field_button.clicked.connect(self.add_custom_field)
        button_layout.addWidget(self.add_field_button)
        self.reset_button = QPushButton('Reset')  
        self.reset_button.clicked.connect(self.reset_fields)  
        button_layout.addWidget(self.reset_button)  
        layout.addLayout(button_layout)

        button_layout2 = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.save_button.setEnabled(False)
        self.retrieve_button = QPushButton('Retrieve')
        self.delete_button = QPushButton('Delete')
        self.delete_button.setEnabled(False)  # 初始時禁用刪除按鈕
        button_layout2.addWidget(self.save_button)
        button_layout2.addWidget(self.retrieve_button)
        button_layout2.addWidget(self.delete_button)  # 將刪除按鈕添加到第二個按鈕佈局
        layout.addLayout(button_layout2)

        # Data list
        self.data_list = QListWidget()
        self.data_list.currentItemChanged.connect(self.enable_delete_button)
        self.data_list.setFixedHeight(150)
        layout.addWidget(self.data_list)

        # Set size policy for all widgets
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.data_input_widget.setSizePolicy(size_policy)
        self.data_list.setSizePolicy(size_policy)

        # update data list when opening the window
        self.category_combo.currentIndexChanged.connect(self.update_data_inputs)
        self.update_data_inputs(0) 
        self.update_data_list(0)
        self.set_scroll_area_font_size(0)

        # double click to copy data
        self.connect_data_input_events()

        # Set font size for newly added widgets inside the scroll area
        self.category_combo.currentIndexChanged.connect(self.set_scroll_area_font_size)

    def set_scroll_area_font_size(self, index):
        for widget in self.data_input_widget.findChildren(QWidget):
            widget.setFont(self.scroll_area.font())

    def update_data_list(self, index):
        category = self.category_combo.itemText(index)
        self.data_list.clear()
        if category in self.model.data:
            self.data_list.addItems(self.model.data[category].keys())

    def update_data_inputs(self, index):
        # 移除佈局中的所有 widgets
        for i in reversed(range(self.data_input_layout.count())):
            layout_item = self.data_input_layout.itemAt(i)
            widget = layout_item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()  # 確保釋放資源

        if index == 0:  # Wallet
            self.add_wallet_inputs()
        elif index == 1:  # Exchange
            self.add_exchange_inputs()
        else:  # Others
            # 為 Others 分類不加載任何預設欄位
            pass

    def add_wallet_inputs(self):
        wallet_seed_label = QLabel('Wallet Seed:')
        self.wallet_seed_input = QLineEdit()
        self.wallet_seed_input.textChanged.connect(self.update_save_button_state)
        self.data_input_layout.addWidget(wallet_seed_label)
        self.data_input_layout.addWidget(self.wallet_seed_input)

        private_key_label = QLabel('Private Key:')
        self.private_key_input = QLineEdit()
        self.private_key_input.textChanged.connect(self.update_save_button_state)
        self.data_input_layout.addWidget(private_key_label)
        self.data_input_layout.addWidget(self.private_key_input)

    def add_exchange_inputs(self):
            exchange_account_label = QLabel('Exchange Account:')
            self.exchange_account_input = QLineEdit()
            self.exchange_account_input.textChanged.connect(self.update_save_button_state)
            self.data_input_layout.addWidget(exchange_account_label)
            self.data_input_layout.addWidget(self.exchange_account_input)

            exchange_password_label = QLabel('Exchange Password:')
            self.exchange_password_input = QLineEdit()
            self.exchange_password_input.textChanged.connect(self.update_save_button_state)
            self.data_input_layout.addWidget(exchange_password_label)
            self.data_input_layout.addWidget(self.exchange_password_input)

            google_2fa_label = QLabel('Google 2FA:')
            self.google_2fa_input = QLineEdit()
            self.google_2fa_input.textChanged.connect(self.update_save_button_state)
            self.data_input_layout.addWidget(google_2fa_label)
            self.data_input_layout.addWidget(self.google_2fa_input)

            auth_email_label = QLabel('Auth Email:')
            self.auth_email_input = QLineEdit()
            self.auth_email_input.textChanged.connect(self.update_save_button_state)
            self.data_input_layout.addWidget(auth_email_label)
            self.data_input_layout.addWidget(self.auth_email_input)

            auth_phone_label = QLabel('Auth Phone:')
            self.auth_phone_input = QLineEdit()
            self.auth_phone_input.textChanged.connect(self.update_save_button_state)
            self.data_input_layout.addWidget(auth_phone_label)
            self.data_input_layout.addWidget(self.auth_phone_input)

            fund_password_label = QLabel('Fund Password:')
            self.fund_password_input = QLineEdit()
            self.fund_password_input.textChanged.connect(self.update_save_button_state)
            self.data_input_layout.addWidget(fund_password_label)
            self.data_input_layout.addWidget(self.fund_password_input)

            identity_data_label = QLabel('Identity Data:')
            self.identity_data_input = QLineEdit()
            self.identity_data_input.textChanged.connect(self.update_save_button_state)
            self.data_input_layout.addWidget(identity_data_label)
            self.data_input_layout.addWidget(self.identity_data_input)

    def connect_data_input_events(self):
        if self.category_combo.currentIndex() == 0:  # Wallet
            self.connect_wallet_events()
        elif self.category_combo.currentIndex() == 1:  # Exchange
            self.connect_exchange_events()
        else:  # Others
            pass

    def connect_wallet_events(self):
        self.wallet_seed_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.wallet_seed_input)
        self.private_key_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.private_key_input)

    def connect_exchange_events(self):
        self.exchange_account_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.exchange_account_input)
        self.exchange_password_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.exchange_password_input)
        self.google_2fa_input.mouseDoubleClickEvent = lambda event: self.copy_to_clipboard(self.google_2fa_input)
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
        elif self.category_combo.currentIndex() == 1:  # Exchange
            self.exchange_account_input.clear()
            self.exchange_password_input.clear()
            self.google_2fa_input.clear()
            self.auth_email_input.clear()
            self.auth_phone_input.clear()
            self.fund_password_input.clear()
            self.identity_data_input.clear()
        else:  # Others
            pass

    def add_custom_field(self, name=None, value=None):
        # Create the custom field container widget
        custom_field_widget = QWidget()
        custom_field_layout = QHBoxLayout(custom_field_widget)
        
        if isinstance(name, str):
            name_widget = QLabel(name)
        else:
            name_widget = QLineEdit()
            name_widget.setPlaceholderText('Field Name')
            self.setup_double_click_to_copy(name_widget)  # Setup double-click to copy for the name field if it's an input
        
        value_input = QLineEdit()
        if value:
            value_input.setText(value)
        else:
            value_input.setPlaceholderText('Field Value')
        value_input.textChanged.connect(self.update_save_button_state)
        self.setup_double_click_to_copy(value_input)  # Setup double-click to copy for the value field
        
        custom_field_layout.addWidget(name_widget)
        custom_field_layout.addWidget(value_input)
        
        # Add the entire widget to the layout, not just the QLineEdit components
        self.data_input_layout.addWidget(custom_field_widget)
        self.custom_fields.append((custom_field_widget, name_widget, value_input))  # Include the widget itself
        self.update_save_button_state()
        
        # Set font size for the new custom field widget
        scroll_area_font = self.scroll_area.font()
        name_widget.setFont(scroll_area_font)
        value_input.setFont(scroll_area_font)

    def setup_double_click_to_copy(self, input_field):
        def on_double_click(event):
            input_field.selectAll()  # 全選文本
            QApplication.clipboard().setText(input_field.text())  # 複製文本到剪貼板
            QLineEdit.mouseDoubleClickEvent(input_field, event)  # 呼叫原本的雙擊事件以保持行為一致

        input_field.mouseDoubleClickEvent = on_double_click


    def remove_custom_fields(self):
        # Remove all custom field widgets from the layout
        for custom_field_widget, name_input, value_input in self.custom_fields:
            # Remove and delete the whole container widget
            self.data_input_layout.removeWidget(custom_field_widget)
            custom_field_widget.deleteLater()
        self.custom_fields.clear()  # Clear the list after removing all custom fields
        self.update_save_button_state()

    def update_save_button_state(self):
        category = self.category_combo.currentText()
        identifier = self.identifier_input.text().strip()

        if not identifier:
            self.save_button.setEnabled(False)
            return

        if category == 'Others':
            has_custom_field = self.has_valid_custom_fields()
            self.save_button.setEnabled(has_custom_field)
        else:
            has_default_field = self.has_valid_default_fields(category)
            has_custom_field = self.has_valid_custom_fields()
            self.save_button.setEnabled(has_default_field or has_custom_field)

    def has_valid_default_fields(self, category):
        default_fields = []
        if category == 'Wallet':
            default_fields = [
                self.wallet_seed_input.text().strip(),
                self.private_key_input.text().strip()
            ]
        elif category == 'Exchange':
            default_fields = [
                self.exchange_account_input.text().strip(),
                self.exchange_password_input.text().strip(),
                self.google_2fa_input.text().strip(),
                self.auth_email_input.text().strip(),
                self.auth_phone_input.text().strip(),
                self.fund_password_input.text().strip(),
                self.identity_data_input.text().strip()
            ]

        return any(default_fields)

    def has_valid_custom_fields(self):
        return any(
            name_widget.text().strip() and value_input.text().strip()
            for _, name_widget, value_input in self.custom_fields
        )


    def enable_delete_button(self, item):
        self.delete_button.setEnabled(item is not None)

    def reset_fields(self):
        self.identifier_input.clear()
        self.clear_data_fields()
        self.remove_custom_fields()