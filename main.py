import sys

from PySide2.QtWidgets import QApplication, QMessageBox
from psycopg2._psycopg import OperationalError
from psycopg2.errors import lookup

from database import Database
from gui import Authorization, GUI

db = None

def handle_exception(cls, exception, traceback):
    if type(exception) == lookup('42501'):
        QMessageBox.critical(None, 'Ошибка', 'Не удалось выполнить операцию')
        db.conn.rollback()
    else:
        print(exception)


def main():
    global db

    sys.excepthook = handle_exception
    app = QApplication(sys.argv)
    login, password, ok = Authorization.ask_login_password()
    if not ok:
        sys.exit(1)

    try:
        db = Database(login, password)
    except OperationalError as e:
        QMessageBox.critical(None, 'Ошибка', 'Не удалось подключиться к базе')
        print(e)
        print(e.pgcode)
        print(e.pgerror)
        sys.exit(1)

    try:
        gui = GUI(db)
        app.exec_()
    except lookup('42501'):
        QMessageBox.critical(None, 'Ошибка', 'Недостаточно прав для осуществления действия')
        sys.exit(1)
    db.close()


main()
