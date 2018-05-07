from PyQt5.Qt import *

from pyqt_sql_demo.connection_model import ConnectionModel
from pyqt_sql_demo.error_handler import ErrorHandler as handle_error


class ConnectionWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.model = ConnectionModel(self)

        # Declare widgets layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add control bar
        control_row_layout = QHBoxLayout(self)
        control_row_layout.setContentsMargins(0, 0, 0, 0)
        # DB type combo box
        db_combo_box = QComboBox(self)
        db_combo_box.addItem('SQLite')
        db_combo_box.addItem('PostgreSQL')
        control_row_layout.addWidget(db_combo_box)
        # Connection string
        self.connection_line = QLineEdit(self)
        self.connection_line.setPlaceholderText('Enter...')
        self.connection_line.setText('demo.db')
        control_row_layout.addWidget(self.connection_line)
        # Connection button
        connection_button = QPushButton(self)
        connection_button.setText('Connect')
        connection_button.clicked.connect(self.on_connect_click)
        control_row_layout.addWidget(connection_button)
        # Add contol row as a first widget in a column
        control_row = QWidget(self)
        control_row.setLayout(control_row_layout)
        layout.addWidget(control_row)

        # Create a splitter consisting of query edit and table view
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.sizePolicy().setVerticalPolicy(QSizePolicy.Maximum)

        # Add query edit widget
        query_edit_layout = QVBoxLayout(self)
        query_edit_layout.setContentsMargins(0, 0, 0, 0)

        query_control_layout = QHBoxLayout(self)
        query_control_layout.setContentsMargins(0, 0, 0, 0)

        query_execute_button = QPushButton('Execute', self)
        query_execute_button.clicked.connect(self.on_execute_click)
        query_control_layout.addWidget(query_execute_button)

        query_commit_button = QPushButton('Commit', self)
        query_commit_button.clicked.connect(self.model.commit)
        query_control_layout.addWidget(query_commit_button)

        query_control = QWidget(self)
        query_control.setLayout(query_control_layout)
        query_edit_layout.addWidget(query_control)

        self.query_text_edit = QTextEdit(self)
        self.query_text_edit.setText(
           "SELECT name FROM sqlite_master WHERE type='table'")
        query_edit_layout.addWidget(self.query_text_edit)

        query_edit = QWidget(self)
        query_edit.setLayout(query_edit_layout)
        query_edit.sizePolicy().setVerticalPolicy(QSizePolicy.Minimum)
        splitter.addWidget(query_edit)

        # Add table view
        table_view = QTableView(self)
        table_view.setModel(self.model)
        table_view.sizePolicy().setVerticalPolicy(
            QSizePolicy.MinimumExpanding)
        splitter.addWidget(table_view)
        splitter.setSizes([100, 900])

        # Assign layout to the widget
        layout.addWidget(splitter)
        self.setLayout(layout)

    def on_connect_click(self):
        with handle_error():
            connection_string = self.connection_line.text()
            self.model.connect(connection_string)
            print('Connected to', connection_string)

    def on_execute_click(self):
        with handle_error():
            query = self.query_text_edit.toPlainText()
            self.model.execute(query)
            print('Executed:', query)

