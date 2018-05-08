from PyQt5.Qt import QVBoxLayout, QHBoxLayout, QComboBox,\
                     QLineEdit, QPushButton, QWidget, QTabWidget,\
                     QSplitter, QTextEdit, QTableView, QSizePolicy, Qt

from pyqt_sql_demo.connection_model import ConnectionModel
from pyqt_sql_demo.error_handler import ErrorHandler as handle_error


class ConnectionWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # Initialize data model
        self.model = ConnectionModel(self)
        # Initialize UI
        self.init_ui()

    def init_ui(self):
        # Declare main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # Initialize control toolbar
        control_bar = self.init_control_bar()
        layout.addWidget(control_bar)
        # Initialize workspace
        workspace = self.init_workspace()
        layout.addWidget(workspace)
        # Apply configured UI layout to the widget
        self.setLayout(layout)

    def init_control_bar(self):
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
        return control_row

    def init_workspace(self):
        # Create a splitter consisting of query edit and table view
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.sizePolicy().setVerticalPolicy(QSizePolicy.Maximum)

        # Initialize query edit file
        query_edit = self.init_query_text_edit()
        splitter.addWidget(query_edit)

        # Initialize result desiplaying widgets
        results_widget = self.init_results_widget()
        splitter.addWidget(results_widget)
        splitter.setSizes([100, 900])
        return splitter

    def init_query_text_edit(self):
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

        query_rollback_button = QPushButton('Rollback', self)
        query_rollback_button.clicked.connect(self.model.rollback)
        query_control_layout.addWidget(query_rollback_button)

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
        return query_edit

    def init_results_widget(self):
        # Initialize QTabWidget to display table view and log
        # in differnt unclosable tabs
        results_widget = QTabWidget(self)
        results_widget.setTabsClosable(False)

        # Add table view
        table_view = QTableView(self)
        table_view.setModel(self.model)
        table_view.sizePolicy().setVerticalPolicy(
            QSizePolicy.MinimumExpanding)
        results_widget.addTab(table_view, 'Data')

        # Att log view
        log = QTextEdit(self)
        log.setReadOnly(True)
        self.model.execute_signal.connect(log.append)
        results_widget.addTab(log, 'Events')
        return results_widget

    def on_connect_click(self):
        with handle_error():
            connection_string = self.connection_line.text()
            self.model.connect(connection_string)
            print('Connected', connection_string)

    def on_execute_click(self):
        with handle_error():
            query = self.query_text_edit.toPlainText()
            self.model.execute(query)
            print('Executed:', query)

    def on_rollbacl_click(self):
        with handle_error():
            self.model.rollback()
            print('Rollback')
