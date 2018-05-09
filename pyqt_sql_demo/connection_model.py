from PyQt5.Qt import QAbstractTableModel, Qt
from PyQt5.QtCore import pyqtSignal

import os.path
import sqlite3
import pyqt_sql_demo.exceptions as exceptions


class ConnectionModel(QAbstractTableModel):

    executed = pyqtSignal(str, name='executed')
    connected = pyqtSignal(str, name='connected')
    disconnected = pyqtSignal()
    fetch_changed = pyqtSignal(bool, name='fetch_changed')

    def __init__(self, parent):
        super().__init__(parent)

        # Stores last successful connection url
        self.url = None
        # Stores last attempted connection url
        self.attempted_url = None
        # Stores connection object
        self.con = None
        self.cur = None

        self._headers = []
        self._data = []
        self._row_count = 0
        self._column_count = 0

    def connect(self, connection_string):
        # Disconnect from old connection, if any
        self.disconnect()
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
        # Let the listeners know that connection is established
        self.connected.emit(self.url)
        # Log the success message
        self.executed.emit('Connected: ' + connection_string)

    def disconnect(self):
        # Attempt to disconnect
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.con:
            self.con.close()
            self.con = None
        # Notify listeners that connection is closed
        self.disconnected.emit()

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
        self.cur = self.con.cursor()
        self.cur.execute(query)
        print('rowCount:', self.cur.rowcount)

        # Fetch first row
        first_row = self.cur.fetchone()
        if first_row:
            # Fetch first row
            self.beginResetModel()
            print('fetched first row')
            self._column_count = len(first_row)
            print('column_count:', self._column_count)
            self._headers = first_row.keys()
            print('headers:', self._headers)
            self._data = [first_row]
            self._row_count = 1
            self.endResetModel()
            print('Must be 1 row here!')
            # Fetch additional rows
            self.fetch_more()
        else:
            # Try to read from Cursor.description if zero rows
            # returned
            self.beginResetModel()
            if self.cur.description:
                self._headers = [h[0] for h in self.cur.description]
                print('headers:', self._headers)
                self._column_count = len(self._headers)
            else:
                self._headers = []
                self._column_count = 0
            self._row_count = 0
            self._data = []
            self.endResetModel()
            # Disable further fetching
            self.fetch_changed.emit(False)

        # print('data:', [tuple(r) for r in self._data])
        self.executed.emit('Executed: ' + query)

    def fetch_more(self):
        limit = 500
        # Try to fetch more
        more = self.cur.fetchmany(limit)
        print('fetched {} rows in fetch_more'.format(len(more)))
        if len(more) > 0:
            self.beginResetModel()
            count = self._row_count + len(more)
            print('fetched {} rows in total'.format(count))
            self._data.extend(more)
            self._row_count = count
            self.endResetModel()
        # Disable further fetching if less rows than
        # that fetching window is returned
        # And enable otherwise
        self.fetch_changed.emit(len(more) >= limit)

    def commit(self):
        self.con.commit()
        self.executed.emit('Committed')
        print('commit')

    def rollback(self):
        self.con.rollback()
        self.executed.emit('Rollback')
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
