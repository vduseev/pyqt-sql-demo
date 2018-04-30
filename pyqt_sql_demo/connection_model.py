from PyQt5.Qt import *


import sqlite3


class ConnectionModel(QAbstractTableModel):
    def __init__(self, parent):
        super().__init__(parent)

        # Dummy initialization
        self.con = None
        self._headers = []
        self._data = []
        self._row_count = 0
        self._column_count = 0

    def connect(self, connection_string):
        self.con = sqlite3.connect(connection_string)
        self.con.row_factory = sqlite3.Row
        print('probably connected')

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

    def commit(self):
        self.con.commit()
        print('commit')

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

