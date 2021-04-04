from PySide2.QtGui import QIntValidator, Qt
from PySide2.QtWidgets import QDialog, QFormLayout, QComboBox, QDateEdit, QLineEdit, QDialogButtonBox, QTableWidget, \
    QVBoxLayout, QSizePolicy, QHeaderView, QTableWidgetItem, QLabel


class EditFields(QDialog):
    def __init__(self, title, header, types, parameters, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.inputs = []
        self.types = types

        layout = QFormLayout()

        for desc, parameter, ty in zip(header, parameters, types):
            if ty == 'foreignkey':
                combobox = QComboBox()

                for id, text in parameter:
                    combobox.addItem(text, userData=id)

                layout.addRow(desc, combobox)
                self.inputs.append(combobox)
            elif ty == 'date':
                date_edit = QDateEdit(parameter)
                layout.addRow(desc, date_edit)
                self.inputs.append(date_edit)
            elif ty == 'text':
                line_edit = QLineEdit(parameter)
                layout.addRow(desc, line_edit)
                self.inputs.append(line_edit)
            elif ty == 'integer':
                line_edit = QLineEdit(parameter)
                line_edit.setValidator(QIntValidator())
                layout.addRow(desc, line_edit)
                self.inputs.append(line_edit)
            else:
                assert False

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def values(self):
        values = []

        for input_, ty in zip(self.inputs, self.types):
            if ty == 'text':
                values.append(input_.text())
            if ty == 'integer':
                values.append(int(input_.text()))
            elif ty == 'date':
                values.append(str(input_.date().getDate()))
            elif ty == 'foreignkey':
                values.append(input_.currentData())

        return values


class ShowTable(QDialog):
    def __init__(self, header, values, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Результат запроса')

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(header))
        self.table_widget.setHorizontalHeaderLabels(header)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)
        self.setMinimumSize(600, 400)

        for row_index, row in enumerate(values):
            self.table_widget.insertRow(row_index)

            for column_index, item in enumerate(row):
                item = QTableWidgetItem(str(item) if item is not None else '')
                self.table_widget.setItem(row_index, column_index, QTableWidgetItem(item))


class Authorization(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Авторизация')

        self.inputs = []

        self.login = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Логин'))
        layout.addWidget(self.login)
        layout.addWidget(QLabel('Пароль'))
        layout.addWidget(self.password)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    @staticmethod
    def ask_login_password():
        dialog = Authorization()
        ok = dialog.exec_() == QDialog.Accepted
        return dialog.login.text(), dialog.password.text(), ok
