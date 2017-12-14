# -*- coding:utf-8 -*-

import sys

from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QPushButton, QDialog, QVBoxLayout, QSizePolicy, QMainWindow, QTabWidget, QDockWidget
from PyQt5.QtCore import Qt

from login import Login
from table import OpenTradesTable, WorkingTradesTable, TradeHistoryTable
from order import SimpleOrder


class MainWindow(QMainWindow):
    
    def __init__(self, api):
        super().__init__()
        
        self.resize(1000, 600)
        self.center()
        self.setWindowTitle('Quick Order for bitFlyer Lightning')
        
        self.api = api
        
        self.status_bar = self.statusBar()
        
        self.create_table_dock()
        
        self.create_tabs()        
        self.setCentralWidget(self.tabs)
        
        
    def center(self):
        """Position the window on the center of a monitor."""
        
        geometry = self.frameGeometry()
        center_p = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(center_p)
        self.move(geometry.topLeft())
        
        
    def create_table_dock(self):
        
        self.create_open_trades()
        open_trades_dock = QDockWidget("Open Trades", self)
        open_trades_dock.setWidget(self.open_trades)
        self.addDockWidget(Qt.BottomDockWidgetArea, open_trades_dock)
        # self.viewMenu.addAction(dock.toggleViewAction())
        
        self.create_working_trades()
        working_trades_dock = QDockWidget("Working Trades", self)
        working_trades_dock.setWidget(self.working_trades)
        self.addDockWidget(Qt.BottomDockWidgetArea, working_trades_dock)
        # self.viewMenu.addAction(dock.toggleViewAction())
        
        self.create_trade_history()
        trade_history_dock = QDockWidget("Trade History", self)
        trade_history_dock.setWidget(self.trade_history)
        self.addDockWidget(Qt.BottomDockWidgetArea, trade_history_dock)
        # self.viewMenu.addAction(dock.toggleViewAction())
        
        self.tabifyDockWidget(open_trades_dock, working_trades_dock)
        self.tabifyDockWidget(working_trades_dock, trade_history_dock)
        open_trades_dock.raise_()
        
    def create_tabs(self):
        
        self.simple_order = SimpleOrder(self.api, self.status_bar, self.open_trades_table, self.working_trades_table, self.trade_history_table)
        # self.ifd = IFD(self.api, self.status_bar, self.open_trades_table, self.working_trades_table, self.trade_history_table)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.simple_order, 'Simple Order')
        # self.tabs.addTab(self.ifd, 'IFD')
        
        
    def create_open_trades(self):
        
        self.open_trades_table = OpenTradesTable(self.api)
        
        layout = QVBoxLayout()
        layout.addWidget(self.create_refresh_btn())
        layout.addWidget(self.open_trades_table)
        self.open_trades = QWidget()
        self.open_trades.setLayout(layout)
        
        # Insert response into table.
        self.open_trades_table.refresh_table()
        
        
    def create_working_trades(self):

        self.working_trades_table = WorkingTradesTable(self.api)

        layout = QVBoxLayout()
        layout.addWidget(self.create_refresh_btn())
        layout.addWidget(self.working_trades_table)
        self.working_trades = QWidget()
        self.working_trades.setLayout(layout)
        
        # Insert response into table.
        self.working_trades_table.refresh_table()
        
        
    def create_trade_history(self):

        self.trade_history_table = TradeHistoryTable(self.api)
        
        layout = QVBoxLayout()
        layout.addWidget(self.create_refresh_btn())
        layout.addWidget(self.trade_history_table)
        self.trade_history = QWidget()
        self.trade_history.setLayout(layout)
        
        # Insert response into table.
        self.trade_history_table.refresh_table()
        
        
    def create_refresh_btn(self):
        
        refresh_btn = QPushButton('Refresh')
        refresh_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        refresh_btn.clicked.connect(self.refresh_tables)
        return refresh_btn
        
        
    def refresh_tables(self):
        self.open_trades_table.refresh_table()
        self.working_trades_table.refresh_table()
        self.trade_history_table.refresh_table()
        
        
if __name__ == '__main__':

    app = QApplication(sys.argv)

    login = Login()
    if login.exec_() == QDialog.Accepted:
        mainwindow = MainWindow(login.api)
        mainwindow.show()
        sys.exit(app.exec_())  