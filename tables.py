from PySide2.QtCore import QDate
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QHeaderView, QTableWidgetItem, QDialog, QMessageBox

from dialog import EditFields


class Table:
    def __init__(self, db, widget):
        self.db = db
        self.table = widget
        self.table.setColumnCount(len(self.header))
        self.table.setHorizontalHeaderLabels(self.header)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def renewal(self):
        self.table.clearContents()
        self.table.setRowCount(0)

        for row_index, row in enumerate(self.fetch()):
            self.table.insertRow(row_index)
            id, *row_data = row

            for column_index, item in enumerate(row_data):
                item = QTableWidgetItem(str(item) if item is not None else '')
                item.setData(Qt.UserRole, id)

                self.table.setItem(row_index, column_index, QTableWidgetItem(item))


class TeacherTable(Table):
    header = ['Тип пары', 'Количество часов', 'Фамилия', 'Имя', 'Отчество', 'Кабинет', 'Дисциплина', 'Группа']
    types = ['text', 'integer', 'text', 'text', 'text', 'foreignkey', 'foreignkey', 'foreignkey']

    def __init__(self, db, widget):
        super().__init__(db, widget)

    def parameters(self):
        return ['', '', '', '', '',
                self.db.fetch_all('SELECT id, classroomNumber FROM Classroom'),
                self.db.fetch_all('SELECT id, disciplineName FROM Discipline'),
                self.db.fetch_all('SELECT id, brigadeCode FROM Brigade')]

    def on_add(self):
        dialog = EditFields('Добавить', self.header, self.types, self.parameters())

        if dialog.exec_() == QDialog.Accepted:
            self.db.cursor.execute('CALL Add_Teacher(%s, %s, %s, %s, %s, %s, %s, %s)', tuple(dialog.values()))
            self.db.conn.commit()

    def on_change(self):
        if self.table.currentItem() is None:
            QMessageBox.warning(self.table, 'ОШИБКА', 'ВЫБЕРИТЕ СТРОКУ ПЕРЕД ИЗМЕНЕНИЕМ')
            return

        index = self.table.currentItem().data(Qt.UserRole)
        dialog = EditFields('Изменить', self.header, self.types, self.parameters())

        if dialog.exec_() == QDialog.Accepted:
            self.db.cursor.execute('CALL Change_Teacher(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (index, *dialog.values()))
            self.db.conn.commit()

    def on_delete(self):
        if self.table.currentItem() is None:
            QMessageBox.warning(self.table, 'ОШИБКА', 'ВЫБЕРИТЕ СТРОКУ ПЕРЕД ИЗМЕНЕНИЕМ')
            return

        index = self.table.currentItem().data(Qt.UserRole)
        self.db.cursor.execute('CALL Delete_Teacher(%s)', (index,))
        self.db.conn.commit()

    def fetch(self):
        self.db.cursor.execute('''
        SELECT  id, pairType, totalWorkHours, Firstname, Surname, Lastname, 
        (SELECT classroomNumber FROM Classroom WHERE id = classroom), 
        (SELECT disciplineName FROM Discipline WHERE id = discipline), 
        (SELECT brigadeCode FROM Brigade WHERE id = brigade) 
            FROM Teacher ORDER BY id''')

        return self.db.cursor.fetchall()


class BrigadeTable(Table):
    header = ['Год поступления', 'Размер', 'Код специальности', 'Код группы', 'Год аккредетации ВУЗа']
    types = ['date', 'integer', 'text', 'text']

    def __init__(self, db, widget):
        super().__init__(db, widget)

    def parameters(self):
        return [QDate.currentDate(), '', '', '', QDate.currentDate()]

    def on_add(self):
        dialog = EditFields('Добавить', self.header, self.types, self.parameters())

        if dialog.exec_() == QDialog.Accepted:
            self.db.cursor.execute('CALL Add_Brigade(%s, %s, %s, %s)', tuple(dialog.values()))
            self.db.conn.commit()

    def on_change(self):
        if self.table.currentItem() is None:
            QMessageBox.warning(self.table, 'ОШИБКА', 'ВЫБЕРИТЕ СТРОКУ ПЕРЕД ИЗМЕНЕНИЕМ')
            return

        index = self.table.currentItem().data(Qt.UserRole)
        dialog = EditFields('Изменить', self.header, self.types, self.parameters())

        if dialog.exec_() == QDialog.Accepted:
            self.db.cursor.execute('CALL Change_Brigade(%s, %s, %s, %s, %s)', (index, *dialog.values()))
            self.db.conn.commit()

    def on_delete(self):
        if self.table.currentItem() is None:
            QMessageBox.warning(self.table, 'ОШИБКА', 'ВЫБЕРИТЕ СТРОКУ ПЕРЕД ИЗМЕНЕНИЕМ')
            return

        index = self.table.currentItem().data(Qt.UserRole)
        self.db.cursor.execute('CALL Delete_Brigade(%s)', (index,))
        self.db.conn.commit()

    def fetch(self):
        self.db.cursor.execute('''
            SELECT id, yearOfAdmission, brigadeSize, courseCode, brigadeCode, dateOfAccreditation 
                FROM Brigade 
                ORDER BY brigadeCode''')

        return self.db.cursor.fetchall()


class ClassroomTable(Table):
    header = ['Группа',     'Статус',   'Номер',    'Размер']
    types  = ['foreignkey', 'text',     'text',     'integer']

    def parameters(self):
        return [self.db.fetch_all('SELECT id, brigadeCode FROM Brigade'), '', '', '']

    def on_add(self):
        dialog = EditFields('Добавить', self.header, self.types, self.parameters())

        if dialog.exec_() == QDialog.Accepted:
            self.db.cursor.execute('CALL Add_Classroom(%s, %s, %s, %s)', tuple(dialog.values()))
            self.db.conn.commit()

    def on_change(self):
        if self.table.currentItem() is None:
            QMessageBox.warning(self.table, 'ОШИБКА', 'ВЫБЕРИТЕ СТРОКУ ПЕРЕД ИЗМЕНЕНИЕМ')
            return

        index = self.table.currentItem().data(Qt.UserRole)
        dialog = EditFields('Изменить', self.header, self.types, self.parameters())

        if dialog.exec_() == QDialog.Accepted:
            self.db.cursor.execute('CALL Change_Classroom(%s, %s, %s, %s, %s)', (index, *dialog.values()))
            self.db.conn.commit()

    def on_delete(self):
        if self.table.currentItem() is None:
            QMessageBox.warning(self.table, 'ОШИБКА', 'ВЫБЕРИТЕ СТРОКУ ПЕРЕД ИЗМЕНЕНИЕМ')
            return

        index = self.table.currentItem().data(Qt.UserRole)
        self.db.cursor.execute('CALL Delete_Classroom(%s)', (index,))
        self.db.conn.commit()

    def fetch(self):
        self.db.cursor.execute('''
        SELECT id, (SELECT brigadeCode FROM Brigade WHERE id = brigade), status, classroomNumber, numberOfPeople
            FROM Classroom 
            ORDER BY classroomNumber''')

        return self.db.cursor.fetchall()


class DisciplineTable(Table):
    header = ['Количество часов', 'Тип',  'Сдача', 'Название']
    types  = ['integer',          'text', 'text',  'text']

    def parameters(self):
        return ['', '', '', '']

    def on_add(self):
        dialog = EditFields('Добавить', self.header, self.types, self.parameters())

        if dialog.exec_() == QDialog.Accepted:
            self.db.cursor.execute('CALL Add_Discipline(%s, %s, %s, %s)', tuple(dialog.values()))
            self.db.conn.commit()

    def on_change(self):
        if self.table.currentItem() is None:
            QMessageBox.warning(self.table, 'ОШИБКА', 'ВЫБЕРИТЕ СТРОКУ ПЕРЕД ИЗМЕНЕНИЕМ')

            return

        index = self.table.currentItem().data(Qt.UserRole)
        dialog = EditFields('Изменить', self.header, self.types, self.parameters())

        if dialog.exec_() == QDialog.Accepted:
            self.db.cursor.execute('CALL Change_Discipline(%s, %s, %s, %s, %s)', (index, *dialog.values()))
            self.db.conn.commit()

    def on_delete(self):
        if self.table.currentItem() is None:
            QMessageBox.warning(self.table, 'ОШИБКА', 'ВЫБЕРИТЕ СТРОКУ ПЕРЕД ИЗМЕНЕНИЕМ')

            return

        index = self.table.currentItem().data(Qt.UserRole)
        self.db.cursor.execute('CALL Delete_Discipline(%s)', (index,))
        self.db.conn.commit()

    def fetch(self):
        self.db.cursor.execute('''
        SELECT id, totalHours, disciplineType, creditType, disciplineName 
            FROM Discipline 
            order by disciplineName''')

        return self.db.cursor.fetchall()
