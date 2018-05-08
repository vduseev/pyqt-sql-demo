from PyQt5.Qt import QAbstractTableModel, Qt
from PyQt5.QtCore import pyqtSignal

import os.path
import sqlite3
import pyqt_sql_demo.exceptions as exceptions


class ConnectionModel(QAbstractTableModel):

    execute_signal = pyqtSignal(str, name='execute_signal')

    def __init__(self, parent):
        super().__init__(parent)

        # Stores last successful connection url
        self.url = None
        # Stores last attempted connection url
        self.attempted_url = None
        # Stores connection object
        self.con = None

        self._headers = []
        self._data = []
        self._row_count = 0
        self._column_count = 0

    def connect(self, connection_string):
        # Strip connection string of missed whitespaces
        self.attempted_url = connection_string.strip()
        # Throw error if url is invalid
        self.verify_attempted_url()
        # Attempt connection
        self.con = sqlite3.connect(self.attempted_url)
        # Use highly-optimized RowFactory to enable
        # name based access to columns in rows
        self.con.row_factory = sqlite3.Row
        # Remember current connected URL
        self.url = self.attempted_url
        # Log the success message
        self.execute_signal.emit('Connected: ' + connection_string)
        print('probably connected')

    def verify_attempted_url(self):
        url = self.attempted_url
        # Two types of SQLite connection URLs are allowed:
        # - :memory:
        # - path to existing file
        if url == ':memory:':
            return
        if os.path.isfile(url):
            return
        # Raise an exception with predefined message
        raise exceptions.FileNotFoundError(url)

    def execute(self, query):
        cur = self.con.cursor()
        cur.execute(query)
        print('rowCount:', cur.rowcount)

        # Fetch first row
        first_row = cur.fetchone()
        if first_row:
            self.beginResetModel()
            print('fetched first row')
            self._column_count = len(first_row)
            print('column_count:', self._column_count)
            self._headers = first_row.keys()
            print('headers:', self._headers)
            self._data = [first_row]

            # Try to fetch more
            more = cur.fetchall()
            if len(more) > 0:
                print('fetched all else')
                self._data.extend(more)
            self._row_count = len(self._data)
            self.endResetModel()

        print('data:', [tuple(r) for r in self._data])
        self.execute_signal.emit('Executed: ' + query)

    def commit(self):
        self.con.commit()
        self.execute_signal.emit('Committed')
        print('commit')

    def rollback(self):
        self.con.rollback()
        self.execute_signal.emit('Rollback')
        print('rollback')

    def rowCount(self, parent):
        return self._row_count

    def columnCount(self, parent):
        return self._column_count

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if len(self._headers) > 0:
                return self._headers[section]

        return None

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

        return None
