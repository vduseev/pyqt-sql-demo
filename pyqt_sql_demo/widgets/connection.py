import logging

from PyQt5.Qt import (
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QWidget,
    QTabWidget,
    QSplitter,
    QTextEdit,
    QTextCursor,
    QTextDocument,
    QTableView,
    QSizePolicy,
    Qt,
)
from PyQt5.QtCore import pyqtSignal

from pyqt_sql_demo.connection.model import ConnectionModel
from pyqt_sql_demo.connection.error_handler import ErrorHandler
from pyqt_sql_demo.widgets.text import *
from pyqt_sql_demo.syntax_highlighter import sql as SQLHighlighter


class ConnectionWidget(QWidget):
    title_changed = pyqtSignal(QWidget, str, name="title_changed")

    def __init__(self, parent):
        super().__init__(parent)

        # Initialize anti-recursion flag during highlighting
        self.is_processing_highlighting = False

        # Initial widget title
        self.title = CONNECTION_TAB_DEFAULT_TITLE

        # Initialize data model
        self.model = ConnectionModel(self)
        self.model.connected.connect(self.on_connection_changed)

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        # Declare main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Initialize control toolbar
        control_bar = self.build_control_bar()
        layout.addWidget(control_bar)

        # Initialize workspace
        workspace = self.build_workspace()
        layout.addWidget(workspace)

        # Apply configured UI layout to the widget
        self.setLayout(layout)

    def build_control_bar(self):
        # Add control bar
        control_row_layout = QHBoxLayout(self)
        control_row_layout.setContentsMargins(0, 0, 0, 0)

        # DB type combo box
        db_combo_box = QComboBox(self)
        for dbname in CONNECTION_STRING_SUPPORTED_DB_NAMES:
            db_combo_box.addItem(dbname)
        control_row_layout.addWidget(db_combo_box)

        # Connection string
        self.connection_line = QLineEdit(self)
        self.connection_line.setPlaceholderText(CONNECTION_STRING_PLACEHOLDER)
        self.connection_line.setText(CONNECTION_STRING_DEFAULT)
        control_row_layout.addWidget(self.connection_line)

        # Connection button
        connection_button = QPushButton(self)
        connection_button.setText(QUERY_CONTROL_CONNECT_BUTTON_TEXT)
        connection_button.clicked.connect(self.on_connect_click)
        control_row_layout.addWidget(connection_button)

        # Add contol row as a first widget in a column
        control_row = QWidget(self)
        control_row.setLayout(control_row_layout)
        return control_row

    def build_workspace(self):
        # Create a splitter consisting of query edit and table view
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.sizePolicy().setVerticalPolicy(QSizePolicy.Maximum)

        # Initialize query edit
        query_edit = self.build_query_text_edit()

        # Disable query control buttons by default
        self.on_disconnected()
        splitter.addWidget(query_edit)

        # Initialize result desiplaying widgets
        results_widget = self.build_results_widget()
        splitter.addWidget(results_widget)
        splitter.setSizes([100, 900])
        return splitter

    def build_query_text_edit(self):
        # Add layouts
        query_edit_layout = QVBoxLayout(self)
        query_edit_layout.setContentsMargins(0, 0, 0, 0)
        query_control_layout = QHBoxLayout(self)
        query_control_layout.setContentsMargins(0, 0, 0, 0)

        # Execute query button
        self.query_execute_button = QPushButton(QUERY_CONTROL_EXECUTE_BUTTON_TEXT, self)
        self.query_execute_button.clicked.connect(self.on_execute_click)
        query_control_layout.addWidget(self.query_execute_button)

        # Fetch data button
        self.query_fetch_button = QPushButton(QUERY_CONTROL_FETCH_BUTTON_TEXT, self)
        self.query_fetch_button.clicked.connect(self.on_fetch_click)
        self.model.fetch_changed.connect(self.on_fetch_changed)
        query_control_layout.addWidget(self.query_fetch_button)

        # Commit button
        self.query_commit_button = QPushButton(QUERY_CONTROL_COMMIT_BUTTON_TEXT, self)
        self.query_commit_button.clicked.connect(self.on_connect_click)
        query_control_layout.addWidget(self.query_commit_button)

        # Rollback button
        self.query_rollback_button = QPushButton(
            QUERY_CONTROL_ROLLBACK_BUTTON_TEXT, self
        )
        self.query_rollback_button.clicked.connect(self.on_rollback_click)
        query_control_layout.addWidget(self.query_rollback_button)

        # Build control strip widget
        query_control = QWidget(self)
        query_control.setLayout(query_control_layout)
        query_edit_layout.addWidget(query_control)

        # Initialize query edit document for text editor
        # and use SQL Highlighter CSS styles for it.
        self.query_text_edit_document = QTextDocument(self)
        self.query_text_edit_document.setDefaultStyleSheet(SQLHighlighter.style())

        # Initialize query text editor using previously built
        # text edutir document.
        self.query_text_edit = QTextEdit(self)
        self.query_text_edit.setDocument(self.query_text_edit_document)
        self.query_text_edit.textChanged.connect(self.on_query_changed)
        self.query_text_edit.setText(QUERY_EDITOR_DEFAULT_TEXT)
        query_edit_layout.addWidget(self.query_text_edit)

        # Connect model's connected/disconnected signals
        self.model.connected.connect(self.on_connected)
        self.model.disconnected.connect(self.on_disconnected)

        query_edit = QWidget(self)
        query_edit.setLayout(query_edit_layout)
        query_edit.sizePolicy().setVerticalPolicy(QSizePolicy.Minimum)
        return query_edit

    def build_results_widget(self):
        # Initialize QTabWidget to display table view and log
        # in differnt unclosable tabs
        results_widget = QTabWidget(self)
        results_widget.setTabsClosable(False)

        # Add table view
        table_view = QTableView(self)
        table_view.setModel(self.model)
        table_view.sizePolicy().setVerticalPolicy(QSizePolicy.MinimumExpanding)
        results_widget.addTab(table_view, QUERY_RESULTS_DATA_TAB_TEXT)

        # Att log view
        log = QTextEdit(self)
        log.setReadOnly(True)
        self.model.executed.connect(log.append)
        results_widget.addTab(log, QUERY_RESULTS_EVENTS_TAB_TEXT)
        return results_widget

    def on_query_changed(self):
        """Process query edits by user"""
        if self.is_processing_highlighting:
            # If we caused the invokation of this slot by set highlighted
            # HTML text into query editor, then ignore this call and
            # mark highlighting processing as finished.
            self.is_processing_highlighting = False
        else:
            # If changes to text were made by user, mark beginning of
            # highlighting process
            self.is_processing_highlighting = True
            # Get plain text query and highlight it
            query_text = self.query_text_edit.toPlainText()
            highlighted_query_text = SQLHighlighter.highlight(query_text)

            # After we set highlighted HTML back to QTextEdit form
            # the cursor will jump to the end of the text.
            # To avoid that we remember the current position of the cursor.
            current_cursor = self.query_text_edit.textCursor()
            current_cursor_position = current_cursor.position()
            # Set highlighted text back to editor which will cause the
            # cursor to jump to the end of the text.
            self.query_text_edit_document.setHtml(highlighted_query_text)
            # Return cursor back to the old position
            current_cursor.setPosition(current_cursor_position)
            self.query_text_edit.setTextCursor(current_cursor)

    def on_connect_click(self):
        with ErrorHandler():
            connection_string = self.connection_line.text()
            self.model.connect(connection_string)
            logging.info(f"Connected: {connection_string}")

    def on_execute_click(self):
        with ErrorHandler():
            query = self.query_text_edit.toPlainText()
            self.model.execute(query)
            logging.info(f"Executed: {query}")

    def on_fetch_click(self):
        with ErrorHandler():
            self.model.fetch_more()
            logging.info(f"Fetch more")

    def on_rollback_click(self):
        with ErrorHandler():
            self.model.rollback()
            logging.info(f"Rollback")

    def on_connected(self):
        self.query_commit_button.setEnabled(True)
        self.query_execute_button.setEnabled(True)
        self.query_fetch_button.setEnabled(False)
        self.query_rollback_button.setEnabled(True)
        self.query_text_edit.setEnabled(True)

    def on_disconnected(self):
        self.query_commit_button.setEnabled(False)
        self.query_execute_button.setEnabled(False)
        self.query_fetch_button.setEnabled(False)
        self.query_rollback_button.setEnabled(False)
        self.query_text_edit.setEnabled(False)

    def on_fetch_changed(self, state):
        self.query_fetch_button.setEnabled(state)

    def on_connection_changed(self, name):
        self.title_changed.emit(self, name)
