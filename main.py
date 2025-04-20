import sys
import sqlite3
from PyQt5 import uic, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QMainWindow, QFileDialog

# специальная переменная, которая будет содержать в себе название выбранной книге при выполнении разных функций
globname = ''
# специальный массив, который нужен для изменения основного каталога при удалении/редактировании/добавлении
globlistbooks = []
# переменная для учитывыния заработка и занесения его в profit.txt
f = open('profit.txt', 'r', encoding='utf-8')
lst = []
try:
    for x in f:
        x = x.strip()
        lst.append(x.split())
    globprofit = int(lst[0][0])
except Exception:
    f = open("profit.txt", 'w')
    f.write(0)
    f.close()
    globprofit = 0


class mainLibrary(QMainWindow):
    global globlistbooks

    def __init__(self, parent=None):
        super().__init__(parent)
        self.counthelp = True
        self._closable = True
        uic.loadUi('QtDesign\\main.ui', self)
        self.newapp = None
        self.fill()
        self.poiskBut.clicked.connect(self.fill)
        self.updateBut.clicked.connect(self.fill)
        self.BooksList.itemDoubleClicked.connect(self.moreInfo)
        self.delBut.clicked.connect(self.delete)
        self.editBut.clicked.connect(self.edit)
        self.addBut.clicked.connect(self.addBook)
        self.textBut.clicked.connect(self.tex)
        self.addAuthorBut.clicked.connect(self.addAuthor)

    def addAuthor(self):
        self.newapp = editAuthor()
        self.newapp.show()

    def tex(self):
        makeText().exec()

    def addBook(self):
        self.newapp = addBook()
        self.newapp.show()

    def fill(self):
        self.profit.setText(f'Прибыль с продаж: {globprofit}₽')
        f = open("profit.txt", 'w')
        f.write(str(globprofit))
        f.close()
        self.BooksList.clear()
        con = sqlite3.connect('BooksList.db')
        curs = con.cursor()
        query_str = 'SELECT title, Author, Price FROM Books'
        if self.updateBut == self.sender() or self.poiskBut == self.sender() and \
                self.parametrs.currentText() == 'Выберите параметр поиска':
            query_str = '''SELECT title, Author, Price FROM Books'''
        elif self.poiskBut == self.sender():
            if self.parametrs.currentText() == 'Автор':
                query_str = f'''SELECT title, Author, Price FROM Books where Author == "{self.poiskEdit.text()}" '''
            elif self.parametrs.currentText() == 'Название':
                query_str = f'''SELECT title, Author, Price FROM Books where title == "{self.poiskEdit.text()}" '''
            else:
                x = self.poiskEdit.text().split()
                if len(x) != 3:
                    pass
                else:
                    query_str = f'''SELECT title, Author, Price FROM Books
                     where price >= {int(x[0])} and price <= {int(x[2])}'''
        que = curs.execute(query_str)
        f = que.fetchall()
        con.close()
        for x in sorted(f):
            inf = []
            for i in x:
                inf.append(str(i))
            globlistbooks.append(inf[0])
            self.BooksList.addItem(f'{inf[0]}. {inf[1]}, {inf[2]}₽')

    def moreInfo(self):
        global globname
        globname = self.BooksList.currentItem().text()
        globname = globname[: globname.find(".")]
        self.currentBook.setText(f'Последняя книга, с которой производилось какое-либо действие: {globname}')
        self.newapp = moreInfAboutBooks()
        self.newapp.show()

    def delete(self):
        global globname
        try:
            globname = self.BooksList.currentItem().text()
            globname = globname[: globname.find(".")]
            self.currentBook.setText(f'Последняя книга, с которой производилось какое-либо действие: {globname}')
            DeleteWarning().exec()
        except Exception:
            pass

    def edit(self):
        global globname
        try:
            globname = self.BooksList.currentItem().text()
            globname = globname[: globname.find(".")]
            self.currentBook.setText(f'Последняя книга, с которой производилось какое-либо действие: {globname}')
            self.newapp = editingBook()
            self.newapp.show()
        except Exception:
            pass


class moreInfAboutBooks(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi('QtDesign\\infAboutBook.ui', self)
        titleOfCurrentBook = globname  # берем название произведение из предыдущего окна с помощью глобальной переменной
        # Выясняем название, жанр и год выпуска книги
        more = sqlite3.connect('BooksList.db')
        curs = more.cursor()
        query_str = f'''SELECT Title, Genre, BookReleaseYear, Cover, Price, Count FROM Books WHERE Title = '{titleOfCurrentBook}' '''
        que = curs.execute(query_str)
        f = list(que.fetchall())
        more.close()
        inf = []
        for x in f:
            for i in x:
                inf.append(i)
        self.titlelabel.setText(str(inf[0]))
        self.genrelabel.setText(str(inf[1]))
        self.rellabel.setText(str(inf[2]))
        self.pricelabel.setText(str(inf[4]) + '₽')
        self.countlabel.setText(str(inf[5]))

        # вставляем обложку книги
        if inf[3] == '' or inf[3] is None:
            self.cover.setText('Фотография отсутсвует!')
        else:
            self.cover.setPixmap(QPixmap(inf[3]))

        # С помощью фамилии автора обращаемся к базе данных с авторами и находим более подробную информацию о нем
        more2 = sqlite3.connect('BooksList.db')
        curs2 = more2.cursor()
        query_str2 = f'''SELECT Name, Surname, Country
         FROM Authors WHERE Surname = (SELECT Author FROM Books WHERE Title = '{titleOfCurrentBook}') '''
        que2 = curs2.execute(query_str2)
        f2 = que2.fetchall()
        more2.close()
        inf2 = []
        for x in f2:
            for i in x:
                inf2.append(i)

        self.countrylabel.setText(str(inf2[2]))
        self.authorlabel.setText(str(inf2[0] + ' ' + inf2[1]))
        # на это заполнение информации о книге закончено, далее идут функции кнопок
        self.deleteBut.clicked.connect(self.delete)
        self.editBut.clicked.connect(self.edit)
        self.sellBut.clicked.connect(self.sell)

    def delete(self):
        self.hide()
        DeleteWarning().exec()

    def edit(self):
        self.close()
        self.app2 = editingBook()
        self.app2.show()

    def sell(self):
        sellBook().exec()
        self.close()


class editingBook(QWidget):
    def __init__(self, parent=None):
        self.fname = QFileDialog
        super().__init__(parent)
        self.newInfa = []
        uic.loadUi('QtDesign\editBook.ui', self)
        self.titleOfCurrentBook = globname
        more = sqlite3.connect('BooksList.db')
        curs = more.cursor()
        query_str = f'''SELECT Title, Genre, BookReleaseYear, Cover, Author,
         Price, Count FROM Books WHERE Title = '{self.titleOfCurrentBook}' '''
        que = curs.execute(query_str)
        f = list(que.fetchall())
        more.close()
        self.inf = []

        for x in f:
            for i in x:
                self.inf.append(i)
        self.oldTitle.setText('Старое название:' + str(self.inf[0]))
        self.oldGenre.setText('Старый жанр: ' + str(self.inf[1]))
        self.oldRelease.setText('Старый год выпуска:' + str(self.inf[2]))
        self.oldAuthor.setText('Старый автор:' + str(self.inf[4]))
        self.oldPrice.setText('Старая цена:' + str(self.inf[5]))
        self.oldCount.setText('Старое количество:' + str(self.inf[6]))

        conn2 = sqlite3.connect('BooksList.db')
        curs2 = conn2.cursor()
        query_str2 = f'''SELECT Surname FROM Authors'''
        que2 = curs2.execute(query_str2)
        f2 = que2.fetchall()
        conn2.close()
        authors = []
        for x in f2:
            for i in x:
                authors.append(i)
        for x in sorted(authors):
            self.chooseAuthor.addItem(x)

        self.okBut.clicked.connect(self.save)
        self.noBut.clicked.connect(self.cancel)
        self.pictureBut.clicked.connect(self.loadPicture)

    def loadPicture(self):
        pictureway = self.fname.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png)')
        a = []
        for x in pictureway:
            a.append(x)
        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        que = f'''UPDATE Books
                SET Cover = '{a[0]}'
                WHERE Title = '{self.titleOfCurrentBook}' '''
        s = curs.execute(que)
        conn.commit()

    def cancel(self):
        self.close()

    def save(self):
        self.okBut.setText('Сохранить изменения')
        if self.newTitle.text() in globlistbooks:
            self.okBut.setText(
                f'Вы не можете изменить название книги на {self.newTitle.text()}, потому что книга с таким названием уже есть!')
        else:
            if self.newRelease.text() != '':
                if not self.newRelease.text().isdigit():
                    self.okBut.setText(
                        f'Неверный год выпуска книги. Возможно в нем есть буквы или специальные символы')
                else:
                    self.proverka()
            else:
                self.proverka()

    def proverka(self):
        if self.newTitle.text() != '':
            self.newInfa.append(self.newTitle.text())
        else:
            self.newInfa.append(str(self.inf[0]))
        if self.newGenre.text() != '':
            self.newInfa.append(self.newGenre.text())
        else:
            self.newInfa.append(self.inf[1])
        if self.newRelease.text() != '':
            self.newInfa.append(int(self.newRelease.text()))
        else:
            self.newInfa.append(int(self.inf[2]))
        if self.newPrice.text() != '':
            self.newInfa.append(int(self.newPrice.text()))
        else:
            self.newInfa.append(int(self.inf[5]))
        if self.newCount.text() != '':
            if self.newCount.text() == '0':
                self.newInfa.append(1)
            else:
                self.newInfa.append(int(self.newCount.text()))
        else:
            self.newInfa.append(int(self.inf[6]))
        self.newInfa.append(self.chooseAuthor.currentText())

        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        que = f'''
               UPDATE Books
               SET Genre = '{self.newInfa[1]}'
               WHERE Title = '{self.titleOfCurrentBook}' '''
        s = curs.execute(que)
        conn.commit()

        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        que = f'''
        UPDATE Books
        SET Title = '{self.newInfa[0]}'
        WHERE Title = '{self.titleOfCurrentBook}' '''
        s = curs.execute(que)
        conn.commit()
        globlistbooks.append(self.newInfa[0])
        globlistbooks.remove(self.inf[0])

        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        que = f'''
               UPDATE Books
               SET BookReleaseYear = '{self.newInfa[2]}'
               WHERE Title = '{self.titleOfCurrentBook}' '''
        s = curs.execute(que)
        conn.commit()

        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        que = f'''
               UPDATE Books
               SET Author = '{self.newInfa[5]}'
               WHERE Title = '{self.titleOfCurrentBook}' '''
        s = curs.execute(que)
        conn.commit()

        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        que = f'''UPDATE Books
                  SET Price = '{self.newInfa[3]}'
                  WHERE Title = '{self.titleOfCurrentBook}' '''
        s = curs.execute(que)
        conn.commit()

        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        que = f'''UPDATE Books
                  SET Count = '{int(self.newInfa[4])}'
                  WHERE Title = '{self.titleOfCurrentBook}' '''
        s = curs.execute(que)
        conn.commit()
        self.hide()


class addBook(QWidget):
    def __init__(self, parent=None):
        self.fname = QFileDialog
        super().__init__(parent)
        self.newInfa = []
        self.pictureway = ''
        uic.loadUi('QtDesign\\addBook.ui', self)
        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        query_str = f'''SELECT Surname FROM Authors'''
        que = curs.execute(query_str)
        f = que.fetchall()
        conn.close()
        authors = []

        for x in f:
            for i in x:
                authors.append(i)
        for x in sorted(authors):
            self.chooseAuthor.addItem(x)

        self.saveBut.clicked.connect(self.save)
        self.noBut.clicked.connect(self.cancel)
        self.pictureBut.clicked.connect(self.loadPicture)

    # в этом методе мы просто получаем путь к изображению
    def loadPicture(self):
        self.pictureway = self.fname.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png)')[0].split('/')[-1]

    def cancel(self):
        self.close()

    def save(self):
        self.saveBut.setText('Сохранить книгу')
        if self.newTitle.text() in globlistbooks:
            self.saveBut.setText(
                f'''Вы не можете изменить название книги на {self.newTitle.text()}, потому
                 что книга с таким названием уже есть!''')
        else:
            if self.newTitle.text() == '':
                self.saveBut.setText(f'У книги не может не быть названия')
            else:
                if self.newRelease.text() != '':
                    if not self.newRelease.text().isdigit():
                        self.saveBut.setText(
                            f'Неверный год выпуска книги. Возможно в нем есть буквы или специальные символы')
                    else:
                        if self.newPrice.text() != '':
                            if not self.newPrice.text().isdigit():
                                self.saveBut.setText(
                                    f'Неверная цена книги. Возможно в ней указаны буквы или специальные символы')
                            else:
                                if self.newCount.text() != '':
                                    if not self.newCount.text().isdigit():
                                        self.saveBut.setText(
                                            f'Неверное количество книги поштучно')
                                    else:
                                        self.proverka()
                                else:
                                    self.proverka()

    def proverka(self):
        if self.newTitle.text() != '':
            self.newInfa.append(self.newTitle.text())
            self.newInfa.append(self.newGenre.text())
            if self.newRelease.text() == '':
                self.newInfa.append(0)
            else:
                self.newInfa.append(int(self.newRelease.text()))
            self.newInfa.append(self.chooseAuthor.currentText())
            if self.pictureway == '':
                self.newInfa.append('')
            else:
                self.newInfa.append(self.pictureway)
            if self.newPrice.text() == '':
                self.newInfa.append(1000)
            else:
                self.newInfa.append(int(self.newPrice.text()))
            if self.newCount.text() == '':
                self.newInfa.append(10)
            else:
                self.newInfa.append(int(self.newCount.text()))
            conn = sqlite3.connect('BooksList.db')
            curs = conn.cursor()
            que = f'''INSERT INTO Books(Title, Author, Genre, BookReleaseYear, Cover, Price, Count) VALUES 
            ('{self.newInfa[0]}','{self.newInfa[3]}', '{self.newInfa[1]}', {self.newInfa[2]}, '{self.newInfa[4]}', 
             '{self.newInfa[5]}', '{self.newInfa[6]}')'''
            s = curs.execute(que)
            conn.commit()
            globlistbooks.append(self.newInfa[0])
            self.close()
        else:
            self.okBut.setText('С названием что-то не так')


class editAuthor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('QtDesign\\addAuthor.ui', self)

        conn = sqlite3.connect('BooksList.db')
        curs = conn.cursor()
        query_str2 = f'''SELECT Surname FROM Authors'''
        que = curs.execute(query_str2)
        f = que.fetchall()
        conn.close()
        a = []
        for x in f:
            for i in x:
                a.append(i)
        self.authors.addItem('Никого не удалять')
        for x in sorted(a):
            self.authors.addItem(x)

        self.save.clicked.connect(self.makesave)
        self.back.clicked.connect(self.cancel)
        self.remove.clicked.connect(self.delete)

    def delete(self):
        if self.authors.currentText() != 'Никого не удалять':
            BookConn = sqlite3.connect('BooksList.db')
            curs = BookConn.cursor()
            query_str = f'''SELECT Title FROM Books
                                WHERE Author = "{self.authors.currentText()}" '''
            s = curs.execute(query_str)
            BookConn.commit()
            k = []
            for x in s:
                for i in x:
                    k.append(i)
            for x in k:
                globlistbooks.remove(x)

            delBookConn = sqlite3.connect('BooksList.db')
            curs = delBookConn.cursor()
            query_str = f'''DELETE FROM Books
                               WHERE Author = "{self.authors.currentText()}" '''
            s = curs.execute(query_str)
            delBookConn.commit()

            delAutConn = sqlite3.connect('BooksList.db')
            curs = delAutConn.cursor()
            query_str = f'''DELETE FROM Authors
                               WHERE Surname = "{self.authors.currentText()}" '''
            s = curs.execute(query_str)
            delAutConn.commit()
            self.close()

    def cancel(self):
        self.close()

    def makesave(self):
        self.exc.setText('')
        country = ''
        if self.countryedit.text() is None:
            country = ' '
        if self.surnameedit.text() == '':
            self.exc.setText('''Ввод фамилии автора обязателен. Если вы хотите добавить народные книги,
                                    то в графе фамилии напишите прочерк''')
        else:
            conn = sqlite3.connect('BooksList.db')
            curs = conn.cursor()
            que = f'''INSERT INTO Authors(Name, Surname, Country) VALUES 
                        ('{self.nameedit.text()}','{self.surnameedit.text()}', '{country}')'''
            s = curs.execute(que)
            conn.commit()
            self.close()


class DeleteWarning(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('QtDesign\\deleteWarning.ui', self)
        self.back.clicked.connect(self.check_ans)
        self.delet.clicked.connect(self.check_ans)

    def check_ans(self):
        if self.delet == self.sender():
            delBookConn = sqlite3.connect('BooksList.db')
            curs = delBookConn.cursor()
            query_str = f'''DELETE FROM Books
                    WHERE Title = "{globname}" '''
            s = curs.execute(query_str)
            delBookConn.commit()

            globlistbooks.remove(globname)
            self.accept()
        else:
            self.reject()
            self.close()


class makeText(QDialog):
    def __init__(self):
        super().__init__()
        self.textway = ''
        self.fname = QFileDialog
        uic.loadUi('QtDesign\\toText.ui', self)
        self.findfile.clicked.connect(self.buildtxt)
        self.build.clicked.connect(self.buildtxt)

    def buildtxt(self):
        if self.sender() == self.findfile:
            # тут мы получаем путь к файлу, куда хотим записать инфу
            self.textway = self.fname.getOpenFileName(
                self, 'Выбрать файл', '',
                'Блокнот (*.txt)')[0]
            f = open(self.textway, 'w')
            for value in globlistbooks:
                f.write(value + '\n')
            f.close()
        if self.sender() == self.build:
            if self.filename.text() == '':
                self.filename.setText('Вы забыли ввести название файла!')
            else:
                f = open(f'{self.filename.text()}.txt', 'w', encoding='utf-8')
                for value in globlistbooks:
                    f.write(value + '\n')
                f.close()
                self.close()
        self.reject()


class sellBook(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('QtDesign\\sellBooks.ui', self)
        take = sqlite3.connect('BooksList.db')
        curs = take.cursor()
        query_str = f'''SELECT Count, Price FROM Books WHERE Title = '{globname}' '''
        que = curs.execute(query_str)
        file = list(que.fetchall())
        self.f = []
        for x in file:
            for i in x:
                self.f.append(i)
        take.close()
        self.noBut.clicked.connect(self.back)
        self.okBut.clicked.connect(self.sell)

    def back(self):
        self.close()

    def sell(self):
        global globprofit
        if not self.countEdit.text().isdigit():
            self.countEdit.setText('Вводите только цифры')

        elif int(self.countEdit.text()) < 0:
            self.countEdit.setText('У вас нет такого количества книг')

        elif int(self.countEdit.text()) > self.f[0]:
            self.countEdit.setText('Вы не можете продать столько книг')

        elif 0 <= int(self.countEdit.text()) <= self.f[0]:
            globprofit += int(self.countEdit.text()) * self.f[1]
            if self.f[0] == int(self.countEdit.text()):
                delBookConn = sqlite3.connect('BooksList.db')
                curs = delBookConn.cursor()
                query_str = f'''DELETE FROM Books
                                    WHERE Title = "{globname}" '''
                s = curs.execute(query_str)
                delBookConn.commit()
                self.accept()
            else:
                conn = sqlite3.connect('BooksList.db')
                curs = conn.cursor()
                que = f'''UPDATE Books
                                  SET Count = '{self.f[0] - int(self.countEdit.text())}'
                                  WHERE Title = '{globname}' '''
                s = curs.execute(que)
                conn.commit()
                self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('pictures\\icon'))
    ex = mainLibrary()
    ex.show()
    sys.exit(app.exec())

