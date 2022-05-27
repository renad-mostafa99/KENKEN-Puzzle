#from curses.textpad import Textbox
from PyQt5.QtWidgets import QMainWindow, QApplication,QPushButton,QDialog,QComboBox,QLabel,QVBoxLayout, QLineEdit,QMessageBox,QDesktopWidget,QWidget
from datetime import datetime
from functools import partial
import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import QRect
from PyQt5 import QtCore
import time

COLOR_A = '#0FC'
COLOR_B = '#CF6'
COLOR_ERR = '#F00'
COLOR_SOLVED = '#F03'


def use_color_A(i, j):
    return (i // 3 + j // 3) % 2 == 1
class AnotherWindow(QMainWindow):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def _init_(self):
        super()._init_()
        top=100
        left=100
        width=800
        height=800
        self.setGeometry(left,top,width,height)
        self.setWindowTitle("hello")
        layout = QVBoxLayout()
        self.input1=QLineEdit()
        self.input2=QLineEdit()
        layout.addWidget(self.input1)
        layout.addWidget(self.input2)
        self.CloseButton=QPushButton("close")
        layout.addWidget(self.CloseButton)
        self.setLayout(layout)
    def buttons(self):    
        button1 = QPushButton("Backtracking",self)
        button2 = QPushButton("Backtracking with forward checking",self)
        button3 = QPushButton("Backtracking with arc consistency",self)
        button4 = QPushButton("Close",self)
          #button.move(100,100)
        button1.setGeometry(QRect(10,700,100,50))
        button2.setGeometry(QRect(120,700,250,50))
        button3.setGeometry(QRect(380,700,250,50))
        button4.setGeometry(QRect(640,700,100,50))
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
   
    def display(self)  :
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
                'background-color: %s;' % COLOR_B)
            self.solve_button.setEnabled(True)
    def initUI(self,n):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        # Create textbox
        for i in range(n):
            for j in range(n):
                # create a QLineEdit
                setattr(self, 'textbox%d%d' % (i, j), QLineEdit(self))
                getattr(self, 'textbox%d%d' % (i, j)).move(20 + 40 * j, 20 + 40 * i)
                getattr(self, 'textbox%d%d' % (i, j)).resize(40, 40)
                getattr(self,'textbox%d%d' % (i, j)).setAlignment(Qt.AlignCenter)
                font = QFont()
                font.setFamily("Comic Sans MS")
                font.setPointSize(16)
                getattr(self, 'textbox%d%d' % (i, j)).setFont(font)
                getattr(self, 'textbox%d%d' % (i, j)).textChanged.connect(
                partial(self.on_change, i, j, use_color_A(i, j)))

                if use_color_A(i, j):
                    getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                    'background-color: %s;' % COLOR_A)
                else:
                    getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                    'background-color: %s;' % COLOR_B)
        # centering the window


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
        #self.initUI()
    def show_new_window(self, checked):
       print(self.num)
       self.w.initUI(self.num)
       self.w.buttons()
       self.w.setGeometry(50,50,800,800)
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
         #self.setCentralWidget(self.button)       
        # connect button to function on_click
         self.button.clicked.connect(self.on_click)
         
   
   

if __name__ == '__main__':
   # App=QApplication(sys.argv)
    #window=Window()
    #sys.exit(App.exec())
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()





       