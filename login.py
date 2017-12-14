# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QDesktopWidget, QMessageBox
import pybitflyer


class Login(QDialog):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        self.resize(300, 150)
        self.center()
        self.setWindowTitle('Quick Order for bitFlyer Lightning')
        
        self.key_label = QLabel('API Key: ')
        self.key_edit = QLineEdit()
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_label)
        key_layout.addWidget(self.key_edit)
        
        self.secret_label = QLabel('API Secret')
        self.secret_edit = QLineEdit()
        self.secret_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        secret_layout = QHBoxLayout()
        secret_layout.addWidget(self.secret_label)
        secret_layout.addWidget(self.secret_edit)
        
        self.confirm = QPushButton('Login')
        self.confirm.clicked.connect(self.handler)
        
        layout = QVBoxLayout()
        layout.addLayout(key_layout)
        layout.addLayout(secret_layout)
        layout.addWidget(self.confirm)
        self.setLayout(layout)
        
        
    def center(self):
        """Position the window on the center of a monitor."""
        
        geometry = self.frameGeometry()
        center_p = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(center_p)
        self.move(geometry.topLeft())
        
        
        
    def handler(self):
        
        self.key = self.key_edit.text()
        self.secret = self.secret_edit.text()
        self.api = pybitflyer.API(self.key, self.secret)
        res = self.api.gettradingcommission(product_code='FX_BTC_JPY')
        if 'commission_rate' in res: # May be better to handle HTTP response status code.
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid API key or secret!')