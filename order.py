# -*- coding: utf-8 -*-

import math

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGroupBox, QFrame, QTabWidget


UNITS = [0.001, 0.01, 0.1, 1]
MIN_DEC_DIGITS = 3
PRODUCT_CODE = 'FX_BTC_JPY'


class Order(QWidget):
    
    def __init__(self, api, status_bar, open_trades, working_trades, trade_history):
        super().__init__()
        
        self.api = api
        self.open_trades = open_trades
        self.working_trades = working_trades
        self.trade_history = trade_history
        
        self.status_bar = status_bar
        
        self.initUI()
        
        
    def initUI(self):
        
        raise NotImplementedError
        
        
    def create_order_preset(self):
        
        self.order_preset_layout = QGridLayout()
        mid_idx = math.ceil(len(UNITS)/2)
        for i, unit in enumerate(UNITS[:mid_idx]):
            unit_btn = QPushButton('+' + str(unit))
            unit_btn.clicked.connect(self.unit_btn_clicked)
            self.order_preset_layout.addWidget(unit_btn, 0, i)
        for i, unit in enumerate(UNITS[mid_idx:]):
            unit_btn = QPushButton('+' + str(unit))
            unit_btn.clicked.connect(self.unit_btn_clicked)
            self.order_preset_layout.addWidget(unit_btn, 1, i)
        self.clear_btn = QPushButton('CLEAR')
        self.clear_btn.clicked.connect(self.clear_btn_clicked)
        self.order_preset_layout.addWidget(self.clear_btn, 1, i+1)
        
        
    def unit_btn_clicked(self):
        
        sender = self.sender()
        amount = float(sender.text()) + float(self.amount.text())
        amount = round(amount, MIN_DEC_DIGITS)
        self.amount.setText(str(amount))
        
        self.active_unit = sender.text()
        
        
    def clear_btn_clicked(self):
        
        self.amount.setText('0')
        
        self.active_unit = '0'
                
        
    def create_order_amount(self):
        
        self.active_unit = '0'
        
        self.amount_label = QLabel('Amount:')
        self.amount = QLineEdit('0')
        self.amount_inc = QPushButton('+')
        self.amount_inc.clicked.connect(self.operate)
        self.amount_dec = QPushButton('-')
        self.amount_dec.clicked.connect(self.operate)
        self.order_amount_layout = QHBoxLayout()
        self.order_amount_layout.addWidget(self.amount_label)
        self.order_amount_layout.addWidget(self.amount)
        self.order_amount_layout.addWidget(self.amount_inc)
        self.order_amount_layout.addWidget(self.amount_dec)
        
        
    def create_order_price(self):
        
        self.price_label = QLabel('Price:')
        self.price = QLineEdit('0')
        self.order_price_layout = QHBoxLayout()
        self.order_price_layout.addWidget(self.price_label)
        self.order_price_layout.addWidget(self.price)
        
        
    def operate(self):
        
        sender = self.sender()
        operator = sender.text()
        
        if operator == '+':
            amount = float(self.amount.text()) + float(self.active_unit)
        elif operator == '-':
            amount = float(self.amount.text()) - float(self.active_unit)
                
        amount = round(amount, MIN_DEC_DIGITS)
        amount = max(0, amount)
        self.amount.setText(str(amount))
        
        
    def create_buy_sell(self):
        
        self.sell_btn = QPushButton('Sell')
        self.sell_btn.clicked.connect(self.place_order)
        self.buy_btn = QPushButton('Buy')
        self.buy_btn.clicked.connect(self.place_order)
        self.buy_sell_layout = QHBoxLayout()
        self.buy_sell_layout.addWidget(self.sell_btn)
        self.buy_sell_layout.addWidget(self.buy_btn)
        
        
    def add_hline(self, layout):
        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        hline.setStyleSheet('color: lightGray')
        layout.addWidget(hline)
        
        
    def refresh_tables(self):
        self.open_trades.refresh_table()
        self.working_trades.refresh_table()
        self.trade_history.refresh_table()
        
        
    def place_order(self):
        
        raise NotImplementedError
        
        
    def check_response(self, res):
        
        # May be better to handle HTTP resonse status code.

        if 'child_order_acceptance_id' in res or 'parent_order_acceptance_id' in res:
            # self.message.setText('Order placed.')
            self.status_bar.showMessage('Order placed.')
        elif 'error_message' in res:
            # self.message.setText('Order failed. ' + res['error_message'])
            self.status_bar.showMessage('Order failed. ' + res['error_message'])
        else:
            # self.message.setText('Order failed. Unexpected error')
            self.status_bar.showMessage('Order failed. Unexpected error')
            
            
        
class MarketOrder(Order):
    
    def __init__(self, api, status_bar, open_trades, working_trades, trade_history):
        super().__init__(api, status_bar, open_trades, working_trades, trade_history)
        
        
    def initUI(self):
        self.create_order_preset()
        self.create_order_amount()
        self.create_buy_sell()

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.order_preset_layout)
        self.add_hline(self.layout)
        self.layout.addLayout(self.order_amount_layout)
        self.add_hline(self.layout)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
                
        
    def place_order(self):
        
        self.params = {'product_code':PRODUCT_CODE,
                      'child_order_type':'MARKET',
                      'side':None,
                      'size':None,
                      'minute_to_expire':43200,
                      'time_in_force':'GTC'}
        
        sender = self.sender()
        side = sender.text().upper()
        size = self.amount.text()
        self.params['side'] = side
        self.params['size'] = size
        
        res = self.api.sendchildorder(**self.params)
        self.check_response(res)
        
        self.refresh_tables()
        
        
class LimitOrder(Order):
    
    def __init__(self, api, status_bar, open_trades, working_trades, trade_history):
        super().__init__(api, status_bar, open_trades, working_trades, trade_history)
        
        
    def initUI(self):
        self.create_order_preset()
        self.create_order_amount()
        self.create_order_price()
        self.create_buy_sell()
        
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.order_preset_layout)
        self.add_hline(self.layout)
        self.layout.addLayout(self.order_amount_layout)
        self.add_hline(self.layout)
        self.layout.addLayout(self.order_price_layout)
        self.add_hline(self.layout)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        
        
    def place_order(self):
        
        self.params = {'product_code':PRODUCT_CODE,
                      'child_order_type':'LIMIT',
                      'side':None,
                      'size':None,
                      'price':None,
                      'minute_to_expire':43200,
                      'time_in_force':'GTC'}
        
        sender = self.sender()
        side = sender.text().upper()
        size = self.amount.text()
        price = self.price.text()
        self.params['side'] = side
        self.params['size'] = size
        self.params['price'] = price
        
        res = self.api.sendchildorder(**self.params)
        self.check_response(res)
        
        self.refresh_tables()
        
        
class StopOrder(Order):
    
    def __init__(self, api, status_bar, open_trades, working_trades, trade_history):
        super().__init__(api, status_bar, open_trades, working_trades, trade_history)
        
        
    def initUI(self):
        
        self.create_order_preset()
        self.create_order_amount()
        self.create_order_price()
        self.create_buy_sell()
        
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.order_preset_layout)
        self.add_hline(self.layout)
        self.layout.addLayout(self.order_amount_layout)
        self.add_hline(self.layout)
        self.layout.addLayout(self.order_price_layout)
        self.add_hline(self.layout)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        
        
    def place_order(self):
        
        self.params = {'order_method':'SIMPLE',
                       'parameters':[{'product_code':PRODUCT_CODE, 'condition_type':'STOP', 'side':None, 'trigger_price':None, 'size':None}]}
        
        sender = self.sender()
        side = sender.text().upper()
        size = self.amount.text()
        trigger_price = self.price.text()
        self.params['parameters'][0]['side'] = side
        self.params['parameters'][0]['size'] = size
        self.params['parameters'][0]['trigger_price'] = trigger_price
            
        res = self.api.sendparentorder(**self.params)
        self.check_response(res)
        
        self.refresh_tables()
        
        
class SimpleOrder(QWidget):
    
    def __init__(self, api, status_bar, open_trades, working_trades, trade_history):
        super().__init__()
        
        self.api = api
        self.status_bar = status_bar
        self.open_trades = open_trades
        self.working_trades = working_trades
        self.trade_history = trade_history
        
        self.initUI()
        
        
    def initUI(self):
        
        self.market_order = MarketOrder(self.api, self.status_bar, self.open_trades, self.working_trades, self.trade_history)
        self.market_order.layout.addLayout(self.market_order.buy_sell_layout)
        
        self.limit_order = LimitOrder(self.api, self.status_bar, self.open_trades, self.working_trades, self.trade_history)
        self.limit_order.layout.addLayout(self.limit_order.buy_sell_layout)
        
        self.stop_order = StopOrder(self.api, self.status_bar, self.open_trades, self.working_trades, self.trade_history)
        self.stop_order.layout.addLayout(self.stop_order.buy_sell_layout)
        
        self.market_order_group = self.create_group_box('Market', self.market_order)
        self.limit_order_group = self.create_group_box('Limit', self.limit_order)
        self.stop_order_group = self.create_group_box('Stop', self.stop_order)
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.market_order_group)
        self.layout.addWidget(self.limit_order_group)
        self.layout.addWidget(self.stop_order_group)
        self.setLayout(self.layout)
        
        
    def create_group_box(self, name, widget):
        
        layout = QHBoxLayout()
        layout.addWidget(widget)
        group = QGroupBox(name)
        group.setLayout(layout)
        return group
    
    
class IFD(QWidget):
    
    def __init__(self, api, status_bar, open_trades_table, working_trades_table, trade_history_table):
        super().__init__()
        
        self.api = api
        self.status_bar = status_bar
        self.open_trades_table = open_trades_table
        self.working_trades_table = working_trades_table
        self.trade_history_table = trade_history_table
        
        self.initUI()
        
        
    def initUI(self):
        
        self.create_if_group()
        self.create_done_group()
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.if_group)
        self.layout.addWidget(self.done_group)
        self.setLayout(self.layout)
        
        
    def create_if_group(self):
        
        self.if_group = QGroupBox('IF')
        layout = QHBoxLayout()
        tabs = QTabWidget()
        self.if_market = MarketOrder(self.api, self.status_bar, self.open_trades_table, self.working_trades_table, self.trade_history_table)
        self.if_limit = LimitOrder(self.api, self.status_bar, self.open_trades_table, self.working_trades_table, self.trade_history_table)
        self.if_stop = StopOrder(self.api, self.status_bar, self.open_trades_table, self.working_trades_table, self.trade_history_table)
        tabs.addTab(self.if_market, 'Market')
        tabs.addTab(self.if_limit, 'Limit')
        tabs.addTab(self.if_stop, 'Stop')
        layout.addWidget(tabs)
        self.if_group.setLayout(layout)


    def create_done_group(self):
        
        self.done_group = QGroupBox('DONE')
        layout = QHBoxLayout()
        tabs = QTabWidget()
        self.done_market = MarketOrder(self.api, self.status_bar, self.open_trades_table, self.working_trades_table, self.trade_history_table)
        self.done_limit = LimitOrder(self.api, self.status_bar, self.open_trades_table, self.working_trades_table, self.trade_history_table)
        self.done_stop = StopOrder(self.api, self.status_bar, self.open_trades_table, self.working_trades_table, self.trade_history_table)
        tabs.addTab(self.done_market, 'Market')
        tabs.addTab(self.done_limit, 'Limit')
        tabs.addTab(self.done_stop, 'Stop')
        layout.addWidget(tabs)
        self.done_group.setLayout(layout)
