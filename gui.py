# from curses.textpad import Textbox
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QLineEdit, QMessageBox, QDesktopWidget
from functools import partial
import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
import sys
from random import seed, random, shuffle, randint, choice
from PyQt5 import QtGui
from PyQt5.QtCore import QRect
from functools import reduce
from sqlalchemy import true

COLOR_A = '#0FC'
COLOR_ERR = '#F00'
COLOR_SOLVED = '#F03'

def use_color_A(i, j):
    return (i // 3 + j // 3) % 2 == 1

def operation(operator):
    """
    A utility function used in order to determine the operation corresponding
    to the operator that is given in string format
    """
    if operator == '+':
        return lambda a, b: a + b
    elif operator == '-':
        return lambda a, b: a - b
    elif operator == '*':
        return lambda a, b: a * b
    elif operator == '/':
        return lambda a, b: a / b
    else:
        return None

def adjacent(xy1, xy2):
    x1, y1 = xy1
    x2, y2 = xy2
    dx, dy = x1 - x2, y1 - y2
    return (dx == 0 and abs(dy) == 1) or (dy == 0 and abs(dx) == 1)

def generate(size):
    board = [[((i + j) % size) + 1 for i in range(size)] for j in range(size)]

    for _ in range(size):
        shuffle(board)

    for c1 in range(size):
        for c2 in range(size):
            if random() > 0.5:
                for r in range(size):
                    board[r][c1], board[r][c2] = board[r][c2], board[r][c1]

    board = {(j + 1, i + 1): board[i][j]
             for i in range(size) for j in range(size)}

    uncaged = sorted(board.keys(), key=lambda var: var[1])

    cliques = []
    while uncaged:

        cliques.append([])

        csize = randint(1, 4)

        cell = uncaged[0]

        uncaged.remove(cell)

        cliques[-1].append(cell)

        for _ in range(csize - 1):

            adjs = [other for other in uncaged if adjacent(cell, other)]

            cell = choice(adjs) if adjs else None

            if not cell:
                break

            uncaged.remove(cell)

            cliques[-1].append(cell)

        csize = len(cliques[-1])
        if csize == 1:
            cell = cliques[-1][0]
            cliques[-1] = ((cell, ), '.', board[cell])
            continue
        elif csize == 2:
            fst, snd = cliques[-1][0], cliques[-1][1]
            if board[fst] / board[snd] > 0 and not board[fst] % board[snd]:
                operator = "/"  # choice("+-*/")
            else:
                operator = "-"  # choice("+-*")
        else:
            operator = choice("+*")

        target = reduce(operation(operator), [
                        board[cell] for cell in cliques[-1]])

        cliques[-1] = (tuple(cliques[-1]), operator, int(target))

    return size, cliques


def validate(cliques):
    for member in cliques:
        target = member[2]
        if target < 0:
            return False

    return True

class AnotherWindow(QMainWindow):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def _init_(self):
        super()._init_()
        top = 100
        left = 100
        width = 800
        height = 800
        self.setGeometry(left, top, width, height)
        self.setWindowTitle("hello")
        layout = QVBoxLayout()
        self.input1 = QLineEdit()
        self.input2 = QLineEdit()
        layout.addWidget(self.input1)
        layout.addWidget(self.input2)
        self.CloseButton = QPushButton("close")
        layout.addWidget(self.CloseButton)
        self.setLayout(layout)

    def buttons(self):
        button1 = QPushButton("Backtracking", self)
        button2 = QPushButton("Forward checking", self)
        button3 = QPushButton("Arc consistency", self)
        button4 = QPushButton("Close", self)
          # button.move(100,100)
        button1.setGeometry(QRect(30, 900, 150, 50))
        button2.setGeometry(QRect(200, 900, 200, 50))
        button3.setGeometry(QRect(420, 900, 200, 50))
        button4.setGeometry(QRect(640, 900, 100, 50))
        button1.clicked.connect(self. Backtracking)
        button2.clicked.connect(self. Backtracking_with_forward_checking)
        button3.clicked.connect(self.Backtracking_with_arc_consistency)
        button4.clicked.connect(self.Close)

    def Backtracking(self):
        print("hello")

    def Backtracking_with_forward_checking(self):
            print("h")

    def Backtracking_with_arc_consistency(self):
         print("hello")

    def Close(self):
       sys.exit()

    def display(self):
        self.show()

    def on_change(self, i, j, is_color_A):
        n = getattr(self, 'textbox%d%d' % (i, j)).text()
        if len(n) == 1 and not n.isdigit() or len(n) > 1:
            getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                'background-color: %s;' % COLOR_ERR)
            self.solve_button.setEnabled(False)
        elif is_color_A:
            getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                'background-color: %s;' % COLOR_A)
            self.solve_button.setEnabled(True)
        else:
            getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                'background-color: %s;' % COLOR_A)
            self.solve_button.setEnabled(True)

    def initUI(self, n):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        size, cliques = generate(n)
        print(cliques)
        self.setWindowTitle('KENKEN PUZZLE')
        valid=validate(cliques)
        while(valid==False):    
            size, cliques = generate(n)
            valid = validate(cliques)
  

        for members in cliques:
            random_number = randint(0, 16777215)
            hex_number = str(hex(random_number))
            color = '#' + hex_number[2:]
            flag = 0
            for member in members[0]:
                x, y = member
                i = x-1
                j = y-1
                flag = flag+1
                setattr(self, 'textbox%d%d' % (i, j), QLineEdit(self))
                getattr(self, 'textbox%d%d' % (i, j)).move(20 + 92 * j, 20 + 92 * i)
                getattr(self, 'textbox%d%d' % (i, j)).resize(90, 90)
                getattr(self, 'textbox%d%d' % (i, j)).setAlignment(Qt.AlignTop)
                font = QFont()
                font.setFamily("Comic Sans MS")
                font.setPointSize(11)
                if(flag == 1):
                    if(members[1] == '.'):
                        getattr(self, 'textbox%d%d' % (i, j)).setText(str(members[2]))
                    elif(members[1] == '*'):
                        getattr(self, 'textbox%d%d' %(i, j)).setText(str(members[2])+' , *')
                    else:
                        getattr(self, 'textbox%d%d' % (i, j)).setText(str(members[2])+' , '+members[1])

                getattr(self, 'textbox%d%d' % (i, j)).setFont(font)
                getattr(self, 'textbox%d%d' % (i, j)).textChanged.connect(partial(self.on_change, i, j, use_color_A(i, j)))

                if use_color_A(i, j):
                    getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                    'background-color: %s;' % color)
                else:
                    getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                        'background-color: %s;' % color)

class Window (QMainWindow):
    def __init__(self):
        super().__init__()
        self.num=0
        self.flag=0
        self.w=AnotherWindow() 
        title="KenKen"
        top=100
        left=100
        width=350
        height=150
        iConName="home.png"
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(iConName))
        self.setGeometry(left,top,width,height)
        self.CreateButton()      
        self.size()
        self.show()
        # self.initUI()

    def show_new_window(self, checked):
       self.w.initUI(self.num)
       self.w.buttons()
       self.w.setGeometry(50,50,950,1000)
       self.w.display()
      
    def size(self):
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280,40)
    
    def on_click(self):
        textboxValue = self.textbox.text()
        if(int(textboxValue)>9 or int(textboxValue)<3):
            QMessageBox.question(self, 'Message - pythonspot.com', "Error" + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
            self.textbox.setText("")
        else:
            self.num=int(textboxValue)
            self.button.clicked.connect(self.show_new_window)
                  
    def CreateButton(self):
        # Create a button in the window
         self.button = QPushButton('Enter Size', self)
         self.button.move(20,80)
         # self.setCentralWidget(self.button)       
        # connect button to function on_click
         self.button.clicked.connect(self.on_click)
         

if __name__ == '__main__':
   # App=QApplication(sys.argv)
    # window=Window()
    # sys.exit(App.exec())
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()





       