# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class TradeTable(QTableWidget):
    
    """Might be better to use abc to force implementing some variables.
    max_n_rows = ...
    headers = ...
    """
    
    def __init__(self, api, n_rows, n_cols):
        super().__init__(n_rows, n_cols)
        
        self.api = api
        
        self.setHorizontalHeaderLabels(self.headers)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        self.refresh_table()
        
        # Widen the length of Time column.
        self.horizontalHeader().resizeSection(0, 200)
                
                
    def refresh_table(self):
        
        raise NotImplementedError
            
            
class OpenTradesTable(TradeTable):
    
    max_n_rows = 10        
    headers = ['Time', 'Pair', 'Sell/Buy', 'Price', 'Amount']
    params = {'product_code':'FX_BTC_JPY'}
    # Convert table headers to HTTP response keys.
    header2responsekey = {'Time':'open_date',
                          'Pair':'product_code',
                          'Sell/Buy':'side',
                          'Price':'price',
                          'Amount':'size'}
    
    
    def __init__(self, api):
        super().__init__(api, self.max_n_rows, len(self.headers))
        
                
    def refresh_table(self):

        res = self.api.getpositions(**self.params)
        
        if res:
            # Insert response into table.
            for i, row in enumerate(res[::-1]):
                for j, header in enumerate(self.headers):
                    key = self.header2responsekey[header]
                    item = QTableWidgetItem(str(row[key]))
                    self.setItem(i, j, item)
        else:
            self.clearContents()
            
            
class WorkingTradesTable(TradeTable):
        
    max_n_rows = 10        
    headers = ['Time', 'Pair', 'OrderType', 'Sell/Buy', 'Amount', 'Remain', 'Price', 'AvePrice']
    params_child = {'product_code':'FX_BTC_JPY',
                    'count':max_n_rows,
                    'child_order_state':'ACTIVE'}
    # Convert table headers to HTTP response keys.
    header2responsekey_child = {'Time':'child_order_date',
                                'Pair':'product_code',
                                'OrderType':'child_order_type',
                                'Sell/Buy':'side',
                                'Amount':'size',
                                'Remain':'outstanding_size',
                                'Price':'price',
                                'AvePrice':'average_price'}
    params_parent = {'product_code':'FX_BTC_JPY',
                     'count':max_n_rows,
                     'parent_order_state':'ACTIVE'}
    # Convert table headers to HTTP response keys.
    header2responsekey_parent = {'Time':'parent_order_date',
                                 'Pair':'product_code',
                                 'OrderType':'parent_order_type',
                                 'Sell/Buy':'side',
                                 'Amount':'size',
                                 'Remain':'outstanding_size',
                                 'Price':'price',
                                 'AvePrice':'average_price'}    


    def __init__(self, api):
        super().__init__(api, self.max_n_rows, len(self.headers))

                
    def refresh_table(self):
        
        def sort_by_time(dic):
            if 'child_order_date' in dic:
                return dic['child_order_date']
            else:
                return dic['parent_order_date']

        res = self.api.getchildorders(**self.params_child)
        res += self.api.getparentorders(**self.params_parent)
        res.sort(key=sort_by_time, reverse=True)
        
        if res:
            # Insert response into table.
            for i, row in enumerate(res):
                if 'child_order_date' in row:
                    for j, header in enumerate(self.headers):
                        key = self.header2responsekey_child[header]
                        item = QTableWidgetItem(str(row[key]))
                        self.setItem(i, j, item)
                else:
                    for j, header in enumerate(self.headers):
                        key = self.header2responsekey_parent[header]
                        item = QTableWidgetItem(str(row[key]))
                        self.setItem(i, j, item)
        else:
            self.clearContents()
            
            
class TradeHistoryTable(TradeTable):
    
    max_n_rows = 10        
    headers = ['Time', 'Sell/Buy', 'Price', 'Amount']                
    params = {'product_code':'FX_BTC_JPY',
              'count':max_n_rows}
    # Convert table headers to HTTP response keys.
    header2responsekey = {'Time':'exec_date',
                          'Sell/Buy':'side',
                          'Amount':'size',
                          'Price':'price'}
            
    
    def __init__(self, api):
        super().__init__(api, self.max_n_rows, len(self.headers))

                
    def refresh_table(self):

        res = self.api.getexecutions(**self.params)
        
        if res:
            # Insert response into table.
            for i, row in enumerate(res):
                for j, header in enumerate(self.headers):
                    key = self.header2responsekey[header]
                    item = QTableWidgetItem(str(row[key]))
                    self.setItem(i, j, item)
        else:
            self.clearContents()