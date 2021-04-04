from PySide2.QtCore import Slot, QFile, QIODevice
from PySide2.QtUiTools import QUiLoader
from dialog import Authorization, ShowTable
from tables import TeacherTable, BrigadeTable, ClassroomTable, DisciplineTable


def load_ui(name):
    file = QFile(name)

    if not file.open(QIODevice.ReadOnly):
        raise Exception('file')

    loader = QUiLoader()
    window = loader.load(file)
    file.close()

    if not window:
        raise Exception(loader.errorString())

    return window

class GUI:
    def __init__(self, db):
        self.db = db

        self.window = load_ui('mainwindow.ui')

        self.tables = [
            TeacherTable(self.db, self.window.teacherTable),
            BrigadeTable(self.db, self.window.groupTable),
            ClassroomTable(self.db, self.window.classroomTable),
            DisciplineTable(self.db, self.window.disciplineTable),
        ]

        for table in self.tables:
            table.renewal()

        self.window.ordering.addItem('ПО ВОЗРАСТАНИЮ', userData='asc')
        self.window.ordering.addItem('ПО УБЫВАНИЮ', userData='desc')

        self.window.addButton.clicked.connect(self.addButton)
        self.window.changeButton.clicked.connect(self.changeButton)
        self.window.deleteButton.clicked.connect(self.deleteButton)
        self.window.accreditationButton.clicked.connect(self.cursorButton)
        self.window.caseButton.clicked.connect(self.caseButton)
        self.window.viewButton.clicked.connect(self.viewButton)
        self.window.notCorrelationButton.clicked.connect(self.notCorrelationButton)
        self.window.secondCourseButton.clicked.connect(self.havingButton)
        self.window.lessThan30Button.clicked.connect(self.on_lessThan30Button)

        self.window.tabs.currentChanged.connect(self.on_tab_changed)

        self.window.show()

    def on_tab_changed(self, index):
        self.tables[index].renewal()

    def addButton(self):
        tab_index = self.window.tabs.currentIndex()
        self.tables[tab_index].on_add()
        self.tables[tab_index].renewal()

    def changeButton(self):
        tab_index = self.window.tabs.currentIndex()
        self.tables[tab_index].on_change()
        self.tables[tab_index].renewal()

    def deleteButton(self):
        tab_index = self.window.tabs.currentIndex()
        self.tables[tab_index].on_delete()
        self.tables[tab_index].renewal()

    def caseButton(self):
        values = self.db.fetch_all('''
            SELECT DISTINCT Teacher.firstName, Classroom.classroomNumber,
            CASE
            WHEN status = 'Занята'
                THEN 'Аудитория свободна'
                ELSE 'Аудитория занята'
            END
            FROM Teacher LEFT JOIN
            Classroom ON Teacher.classroom = Classroom.id;
        ''')

        dialog = ShowTable(['Фамилия', 'Номер', 'Статус'], values)
        dialog.exec_()

    @Slot()
    def viewButton(self):
        ordering = self.window.ordering.currentData()
        values = self.db.fetch_all('''
            SELECT classroomNumber, numberOfPeople, bn from View_Classroom
                GROUP BY (id, classroomNumber, numberOfPeople, bn)
                    ORDER BY classroomNumber
        ''' + ' ' + ordering)

        dialog = ShowTable(['Кабинет', 'Количество людей в аудитории', 'Количество людей в группе'], values)
        dialog.exec_()

    @Slot()
    def notCorrelationButton(self):
        values = self.db.fetch_all('''
        SELECT brigadeCode, brigadeSize, (SELECT AVG(brigadeSize) FROM Brigade ) AS avg_Size FROM Brigade;''')

        dialog = ShowTable(['Номер группы', 'Размер группы', 'Средний размер'], values)
        dialog.exec_()

    @Slot()
    def havingButton(self):
        values = self.db.fetch_all('''
        SELECT Concat_Brigade(brigadeSize, brigadeCode) FROM Brigade JOIN Classroom ON Brigade.id = Classroom.brigade 
            GROUP BY Brigade.id HAVING MIN(yearOfAdmission) > '2018-02-16';''')

        dialog = ShowTable(['Группа + размер'], values)
        dialog.exec_()

    @Slot()
    def on_lessThan30Button(self):
        values = self.db.fetch_all('''
        SELECT brigadeCode, courseCode, brigadeSize FROM Brigade WHERE brigadeSize = 
            ANY(SELECT brigadeSize FROM Brigade WHERE brigadeSize < 30);''')

        dialog = ShowTable(['Номер группы', 'Номер потока', 'Размер'], values)
        dialog.exec_()

    @Slot()
    def cursorButton(self):
        self.db.cursor.execute('call Renewal()')
        self.db.conn.commit()

        for table in self.tables:
            table.renewal()
