from PyQt5.Qt import QAbstractTableModel, Qt
from PyQt5.QtCore import pyqtSignal

import pyqt_sql_demo.connection.exceptions as exceptions
import pyqt_sql_demo.widgets.text as UI

from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit

import os.path
import sqlite3
import mysql.connector as MySqlConnector
import logging
import typing # Needed for byte string to string conversion

class ConnectionModel(QAbstractTableModel):
    executed = pyqtSignal(str, name="executed")
    connected = pyqtSignal(str, name="connected")
    disconnected = pyqtSignal()
    fetch_changed = pyqtSignal(bool, name="fetch_changed")
    database_type = None

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

    def connect(self, database_type, connection_string):
        # Disconnect from old connection, if any
        self.disconnect()
        self.database_type = database_type
        if database_type == "SQLite":            
            # Strip connection string of missed whitespaces
            self.attempted_url = connection_string.strip()
            # Throw error if url is invalid
            self.verify_attempted_url()
            # Attempt connection
            self.con = sqlite3.connect(self.attempted_url)
            # Use highly-optimized RowFactory to enable
            # name based access to columns in rows
            self.con.row_factory = sqlite3.Row
        elif database_type == "MySQL":
            #host=localhost;port=3307;dbname=mysql.user
            #connection_string = "username=root;host=localhost;port=3306;dbname=mysql"
            connection_args = dict(s.split("=") for s in connection_string.split(";"))

            if "dbname" in connection_args:
                connection_args["database"] = connection_args.pop("dbname")

            if "username" in connection_args:
                connection_args["user"] = connection_args.pop("username")

            password, ok = QInputDialog.getText(
                None,
                "Attention",
                "Password?", 
                QLineEdit.Password
            )

            if ok and password:
                connection_args["password"] = password

            self.con = MySqlConnector.connect(**connection_args)
        # Remember current connected URL
        self.url = self.attempted_url
        # Let the listeners know that connection is established
        self.connected.emit(self.url)
        # Log the success message
        self.executed.emit("Connected: " + connection_string)

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
        if url == ":memory:":
            return
        if os.path.isfile(url):
            return
        # Raise an exception with predefined message
        raise exceptions.FileNotFoundError(url)

    def execute(self, query):
        self.cur = self.con.cursor()
        self.cur.execute(query)
        logging.debug(f"row count: {self.cur.rowcount}")

        # Fetch first row
        first_row = self.cur.fetchone()
        if first_row:
            # Fetch first row
            self.beginResetModel()
            logging.debug("fetcher first row")
            if self.cur.description:
                self._headers = [h[0] for h in self.cur.description]
                self._column_count = len(self._headers)
            else:
                self._column_count = len(first_row)
                self._headers = first_row.keys()

            logging.debug(f"column count: {self._column_count}")
            logging.debug(f"headers: {self._headers}")

            first_row_as__list = [first_row]

            if self.database_type == 'MySQL':
                self._data = self._rows_to_string(first_row_as__list)
            else:
                self._data = first_row_as__list
            self._row_count = 1
            self.endResetModel()
            # Fetch additional rows
            self.fetch_more()
        else:
            # Try to read from Cursor.description if zero rows
            # returned
            self.beginResetModel()
            if self.cur.description:
                self._headers = [h[0] for h in self.cur.description]
                logging.debug(f"headers: {self._headers}")
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
        self.executed.emit("Executed: " + query)

    def fetch_more(self):
        limit = 500
        # Try to fetch more
        more = self.cur.fetchmany(limit)
        logging.debug(f"fetched {len(more)} rows in fetch_more call")

        if self.database_type == 'MySQL':
            more = self._rows_to_string(more)

        if len(more) > 0:
            self.beginResetModel()
            count = self._row_count + len(more)
            logging.debug(f"fetched {count} rows in total")
            self._data.extend(more)
            self._row_count = count
            self.endResetModel()
        # Disable further fetching if less rows than
        # that fetching window is returned
        # And enable otherwise
        self.fetch_changed.emit(len(more) >= limit)

    def _rows_to_string(self, rows):
        """ bin data to string """
        rows_string = []
        for row in rows:
            row_string = []
            for cell in row:
                if isinstance(cell, typing.ByteString):
                    cell = cell.decode()
                row_string.append(cell)
            rows_string.append(row_string)
        return rows_string


    def commit(self):
        self.con.commit()
        self.executed.emit("Committed")
        logging.debug("Commit")

    def rollback(self):
        self.con.rollback()
        self.executed.emit("Rollback")
        logging.debug("Rollback")

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
