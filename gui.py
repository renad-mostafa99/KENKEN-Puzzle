# from curses.textpad import Textbox
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QTextEdit, QMessageBox, QDesktopWidget, \
    QLabel
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
import algorithm_csp
import timeit
# @ <component>: <usage>

# @ stderr: reporting errors
# @ stdin: receiving input
from sys import stderr, stdin

# @ product: creation of the variables' domains
# @ permutations: determine the satisfiability of an operation
from itertools import product, permutations

# @ reduce: determine the result of an operation
from functools import reduce

# @ seed: seed the pseudorandom number generator
# @ random, shuffle, randint, choice: generate a random kenken puzzle
from random import seed, random, shuffle, randint, choice

# @ time: benchmarking
from time import time

# @ writer: output benchmarking data in a csv format
from csv import writer

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


def conflicting(A, a, B, b):
    """
    Evaluates to true if:
      * there exists mA so that ma is a member of A and
      * there exists mb so that mb is a member of B and
      * RowXorCol(mA, mB) evaluates to true and
      * the value of mA in 'assignment' a is equal to
        the value of mb in 'assignment' b
    """
    for i in range(len(A)):
        for j in range(len(B)):
            mA = A[i]
            mB = B[j]

            ma = a[i]
            mb = b[j]
            if RowXorCol(mA, mB) and ma == mb:
                return True

    return False


def validate(cliques):
    for member in cliques:
        target = member[2]
        if target < 0:
            return False

    return True


def RowXorCol(xy1, xy2):
    """
    Evaluates to true if the given positions are in the same row / column
    but are in different columns / rows
    """
    return (xy1[0] == xy2[0]) != (xy1[1] == xy2[1])


def conflicting(A, a, B, b):
    """
    Evaluates to true if:
      * there exists mA so that ma is a member of A and
      * there exists mb so that mb is a member of B and
      * RowXorCol(mA, mB) evaluates to true and
      * the value of mA in 'assignment' a is equal to
        the value of mb in 'assignment' b
    """
    for i in range(len(A)):
        for j in range(len(B)):
            mA = A[i]
            mB = B[j]

            ma = a[i]
            mb = b[j]
            if RowXorCol(mA, mB) and ma == mb:
                return True

    return False


def gdomains(size, cliques):
    """
    @ https://docs.python.org/2/library/itertools.html
    @ product('ABCD', repeat=2) = [AA AB AC AD BA BB BC BD CA CB CC CD DA DB DC DD]
    For every clique in cliques:
        * Initialize the domain of each variable to contain every product
        of the set [1...board-size] that are of length 'clique-size'.
        For example:
            board-size = 3 and clique-size = 2
            products = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
        * Discard any value (assignment of the members of the clique) that:
        * is resulting in the members of the clique 'conflicting' with each other
        * does not 'satisfy' the given operation
    """
    domains = {}
    for clique in cliques:
        members, operator, target = clique

        domains[members] = list(
            product(range(1, size + 1), repeat=len(members)))

        def qualifies(values): return not conflicting(
            members, values, members, values) and satisfies(values, operation(operator), target)

        domains[members] = list(filter(qualifies, domains[members]))

    return domains


def satisfies(values, operation, target):
    """
    Evaluates to true if the result of applying the operation
    on a permutation of the given values is equal to the specified target
    """
    for p in permutations(values):
        if reduce(operation, p) == target:
            return True

    return False


def gneighbors(cliques):
    """
    Determine the neighbors of each variable for the given puzzle
        For every clique in cliques
        * Initialize its neighborhood as empty
        * For every clique in cliques other than the clique at hand,
            if they are probable to 'conflict' they are considered neighbors
    """
    neighbors = {}
    
    for members, _, _ in cliques:
        neighbors[members] = []

    for A, _, _ in cliques:
        for B, _, _ in cliques:
            if A != B and B not in neighbors[A]:
                if conflicting(A, [-1] * len(A), B, [-1] * len(B)):
                    neighbors[A].append(B)
                    neighbors[B].append(A)

    return neighbors




class Kenken(algorithm_csp.CSP):

    def __init__(self, size, cliques):
        """
        In my implementation, I consider the cliques themselves as variables.
        A clique is of the format (((X1, Y1), ..., (XN, YN)), <operation>, <target>)
        where
            * (X1, Y1), ..., (XN, YN) are the members of the clique
            * <operation> is either addition, subtraction, division or multiplication
            * <target> is the value that the <operation> should produce
              when applied on the members of the clique
        """
        #validate(size, cliques)

        variables = [members for members, _, _ in cliques]

        domains = gdomains(size, cliques)

        neighbors = gneighbors(cliques)

        algorithm_csp.CSP.__init__(
            self, variables, domains, neighbors, self.constraint)

        self.size = size

        # Used in benchmarking
        self.checks = 0

        # Used in displaying
        self.padding = 0

        self.meta = {}
        for members, operator, target in cliques:
            self.meta[members] = (operator, target)
            self.padding = max(self.padding, len(str(target)))

    # def nconflicts(self, var, val, assignment):

    # def assign(self, var, val, assignment):

    # def unassign(self, var, assignment):

    def constraint(self, A, a, B, b):
        """
        Any two variables satisfy the constraint if they are the same
        or they are not 'conflicting' i.e. every member of variable A
        which shares the same row or column with a member of variable B
        must not have the same value assigned to it
        """
        self.checks += 1

        return A == B or not conflicting(A, a, B, b)
        
        

    def display(self, assignment):
        """
        Print the kenken puzzle in a format easily readable by a human
        """
        if assignment:
            atomic = {}
            for members in self.variables:
                values = assignment.get(members)

                if values:
                    for i in range(len(members)):
                        atomic[members[i]] = values[i]
                else:
                    for member in members:
                        atomic[member] = None
        else:
            atomic = {
                member: None for members in self.variables for member in members}

        atomic = sorted(
            atomic.items(), key=lambda item: item[0][1] * self.size + item[0][0])

        def padding(c, offset): return (c * (self.padding + 2 - offset))

        def embrace(inner, beg, end): return beg + inner + end

        mentioned = set()

        def meta(member):
            for var, val in self.meta.items():
                if member in var and var not in mentioned:
                    mentioned.add(var)
                    return str(val[1]) + " " + (val[0] if val[0] != "." else " ")

            return ""

        def fit(word): return padding(" ", len(word)) + word + padding(" ", 0)

        cpadding = embrace(2 * padding(" ", 0), "|", "") * self.size + "|"

        def show(row):

            rpadding = "".join(["|" + fit(meta(item[0]))
                               for item in row]) + "|"

            data = "".join(["|" + fit(str(item[1] if item[1] else ""))
                           for item in row]) + "|"

            print(rpadding, data, cpadding, sep="\n")

        rpadding = embrace(2 * padding("-", 0), "+", "") * self.size + "+"

        print(rpadding)
        for i in range(1, self.size + 1):

            show(list(filter(lambda item: item[0][1] == i, atomic)))

            print(rpadding)
    
    

    def info(self):
        """
        Print debugging info
        """

        print("\nVariables:")
        for var in self.variables:
            print(var)

        print("\nDomains:")
        for var in self.variables:
            print("domains[", var, "] =", self.domains[var])

        print("\nNeighbors:")
        for var in self.variables:
            print("neighbors[", var, "] =", self.neighbors[var])


def benchmark(kenken, algorithm):
    """
    Used in order to benchmark the given algorithm in terms of
      * The number of nodes it visits
      * The number of constraint checks it performs
      * The number of assignments it performs
      * The completion time
    """
    kenken.checks = kenken.nassigns = 0

    dt = time()

    assignment = algorithm(kenken)

    dt = time() - dt

    return assignment, (kenken.checks, kenken.nassigns, dt)


def gather(iterations, out):
    """
    Benchmark each one of the following algorithms for various kenken puzzles
      * For every one of the following algorithms
       * For every possible size of a kenken board
         * Create 'iterations' random kenken puzzles of the current size
           and evaluate the algorithm on each one of them in order to get
           statistically sound data. Then calculate the average evaluation
           of the algorithm for the current size.
      * Save the results into a csv file
    """
    def bt(ken): return algorithm_csp.backtracking_search(ken)

    def bt_mrv(ken): return algorithm_csp.backtracking_search(
        ken, select_unassigned_variable=algorithm_csp.mrv)

    def fc(ken): return algorithm_csp.backtracking_search(
        ken, inference=algorithm_csp.forward_checking)

    def fc_mrv(ken): return algorithm_csp.backtracking_search(
        ken, inference=algorithm_csp.forward_checking, select_unassigned_variable=algorithm_csp.mrv)
        
        
    def mac(ken): return algorithm_csp.backtracking_search(
        ken, inference=algorithm_csp.mac)

    def mconflicts(ken): return algorithm_csp.min_conflicts(ken)
    algorithms = {
        "BT": bt,
        "BT+MRV": bt_mrv,
        "FC": fc,
        "FC+MRV": fc_mrv,
        "MAC": mac,
        "MIN_CONFLICTS": mconflicts
    }

    with open(out, "w+") as file:

        out = writer(file)

        out.writerow(["Algorithm", "Size", "Result",
                     "Constraint checks", "Assignments", "Completion time"])

        for name, algorithm in algorithms.items():
            for size in range(3, 10):
                checks, assignments, dt = (0, 0, 0)
                for iteration in range(1, iterations + 1):
                
                    size, cliques = generate(size)

                    assignment, data = benchmark(
                        Kenken(size, cliques), algorithm)

                    print("algorithm =",  name, "size =", size, "iteration =", iteration,
                          "result =", "Success" if assignment else "Failure", file=stderr)

                    checks += data[0] / iterations
                    assignments += data[1] / iterations
                    dt += data[2] / iterations

                out.writerow([name, size, checks, assignments, dt])


class AnotherWindow(QMainWindow):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    
    def _init_(self):
        super()._init_()
        
        #window data 
        top = 100
        left = 100
        width = 800
        height = 1000
        #buttons flages 
        
        self.flagBT = 0
        self.flagfc = 0
        self.flagAC = 0
        #time variable
        
        self.BT_time
        self.FC_time
        self.AC_time
        
        self.cliques = []
        self.size = 0
        self.setGeometry(left, top, width, height)
        self.setWindowTitle("hello")
        layout = QVBoxLayout()
        
        self.input1 = QTextEdit()
        self.input2 = QTextEdit()
        layout.addWidget(self.input1)
        layout.addWidget(self.input2)
        
        self.CloseButton = QPushButton("close")
        layout.addWidget(self.CloseButton)
        self.setLayout(layout)
        # def buttons(self):
        #button1 = QPushButton("Backtracking", self)
        #button2 = QPushButton("Forward checking", self)
        #button3 = QPushButton("Arc consistency", self)
        #button4 = QPushButton("Close", self)
        # button.move(100,100)
        #button1.setGeometry(QRect(30, 900, 150, 50))
        #button2.setGeometry(QRect(200, 900, 200, 50))
        #button3.setGeometry(QRect(420, 900, 200, 50))
        #button4.setGeometry(QRect(640, 900, 100, 50))
        #button1.clicked.connect(self. Backtracking)
        #button2.clicked.connect(self. Backtracking_with_forward_checking)
        # button3.clicked.connect(self.Backtracking_with_arc_consistency)
        # button4.clicked.connect(self.Close)""

    def Backtracking(self):
    
        self.flagfc = 1
        self.flagAC = 1
        ken = Kenken(self.size, self.cliques)
        time1 = timeit.default_timer()
        assignment = algorithm_csp.backtracking_search(ken)
        time2 = timeit.default_timer()
        self.BT_time = time2-time1
        print(self.BT_time)
        self.label_1.setText("Backtracking time : " + str(self.BT_time))
        
        for members in assignment:
            flag = 0
            for member in members:
                value = assignment[members][flag]
                x, y = member
                i = x-1
                j = y-1
                flag = flag+1
                font = QFont()
                font.setFamily("Comic Sans MS")
                font.setPointSize(15)
                
                m=""
                m= getattr(self, 'textbox%d%d' % (i, j)).toPlainText()
                
                
                if(self.flagBT == 1):
                    k = ''
                    o=0
                    for o in range(9):
                        if(m[o]==' ' and m[o+1]==' '):
                            break
                        else:
                            k += m[o] 
                    getattr(self, 'textbox%d%d' % (i, j)).setText(
                        k+"   "+str(value).capitalize())
                else:
                    getattr(self, 'textbox%d%d' % (i, j)).setText(
                        m+"\n"+"\n"+"   "+str(value).capitalize())
        self.flagBT = 0
        print(assignment)


    def Backtracking_with_forward_checking(self):
        self.flagBT = 1
        self.flagAC = 1
        ken = Kenken(self.size, self.cliques)
        time1 = timeit.default_timer()
        assignment = algorithm_csp.backtracking_search(
        ken, inference=algorithm_csp.forward_checking)
        time2 = timeit.default_timer()
        self.FC_time = time2 - time1
        print(self.FC_time)
        self.label_2.setText("Backtracking with forword checking time : " + str(self.FC_time))
        
        for members in assignment:
            flag = 0
            for member in members:
                value = assignment[members][flag]
                x, y = member
                i = x-1
                j = y-1
                flag = flag+1
                #setattr(self, 'textbox%d%d' % (i, j), QTextEdit(self))
                #getattr(self, 'textbox%d%d' % (i, j)).move(20 + 92 * j, 20 + 92 * i)
                #getattr(self, 'textbox%d%d' % (i, j)).resize(90, 90)
                #getattr(self, 'textbox%d%d' % (i, j)).setAlignment(Qt.AlignCenter)
                font = QFont()
                font.setFamily("Comic Sans MS")
                font.setPointSize(15)
                
                m=""
                m= getattr(self, 'textbox%d%d' % (i, j)).toPlainText()
                
                if(self.flagfc == 1):
                    k = ''
                    o=0
                    for o in range(9):
                        if(m[o]==' ' and m[o+1]==' '):
                            break
                        else:
                            k += m[o] 
                    getattr(self, 'textbox%d%d' % (i, j)).setText(
                        k+"   "+str(value).capitalize())
                else:
                    getattr(self, 'textbox%d%d' % (i, j)).setText(
                        m+"\n"+"\n"+"   "+str(value).capitalize())
        self.flagfc = 0
        print(assignment)


    def Backtracking_with_arc_consistency(self):
        self.flagfc = 1
        self.flagBT = 1
        ken = Kenken(self.size, self.cliques)
        time1 = timeit.default_timer()
        assignment = algorithm_csp.backtracking_search(ken, inference=algorithm_csp.mac)
        time2 = timeit.default_timer()
        self.AC_time = time2 - time1
        print(self.AC_time)
        self.label_3.setText("Backtracking with arc consistency time : " + str(self.AC_time))
        for members in assignment:
            flag = 0
            for member in members:
                value = assignment[members][flag]
                x, y = member
                i = x-1
                j = y-1
                flag = flag+1
                #setattr(self, 'textbox%d%d' % (i, j), QTextEdit(self))
                #getattr(self, 'textbox%d%d' % (i, j)).move(20 + 92 * j, 20 + 92 * i)
                #getattr(self, 'textbox%d%d' % (i, j)).resize(90, 90)
                #getattr(self, 'textbox%d%d' % (i, j)).setAlignment(Qt.AlignCenter)
                font = QFont()
                font.setFamily("Comic Sans MS")
                font.setPointSize(15)
                
                m=""
                m= getattr(self, 'textbox%d%d' % (i, j)).toPlainText()
                
                if(self.flagAC == 1):
                    k = ''
                    o=0
                    for o in range(9):
                        if(m[o]==' ' and m[o+1]==' '):
                            break
                        else:
                            k += m[o] 
                    getattr(self, 'textbox%d%d' % (i, j)).setText(
                        k+"   "+str(value).capitalize())
                else:
                    getattr(self, 'textbox%d%d' % (i, j)).setText(
                        m+"\n"+"\n"+"   "+str(value).capitalize())
        self.flagAC = 0

                    
    def Close(self):
        sys.exit()


    def display(self):
        self.show()

    def on_change(self, i, j, is_color_A):
        n = getattr(self, 'textbox%d%d' % (i, j)).toPlainText()
        if len(n) == 1 and not n.isdigit() or len(n) > 1:
            getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                'background-color: %s;' % COLOR_ERR)
            self.button1.setEnabled(True)
            self.button2.setEnabled(True)
            self.button3.setEnabled(True)
        elif is_color_A:
            getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                'background-color: %s;' % COLOR_A)
            self.button1.setEnabled(True)
            self.button2.setEnabled(True)
            self.button3.setEnabled(True)
        else:
            getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                'background-color: %s;' % COLOR_A)
            self.button1.setEnabled(True)
            self.button2.setEnabled(True)
            self.button3.setEnabled(True)
    
    
    def on_clear_click(self):
       # self.console_text.setText('Welcome. Esc to exit')
        for i in range(self.siz):
            for j in range(self.siz):
                getattr(self, 'textbox%d%d' % (i, j)).setText(" ")
                #getattr(self,'textbox%d%d' % (i, j)).setStyleSheet('color: black;')
                #if use_color_A(i, j):
                 #   getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                      #  'background-color: %s;' % COLOR_A)
                #else:
                 #   getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                  #      'background-color: %s;' % COLOR_B)

                
    def initUI(self, n):
        self.siz = n
        #buttons flags
        self.flagBT = 0
        self.flagfc = 0
        self.flagAC = 0
        
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.size, self.cliques = generate(n)
        self.button1 = QPushButton('Backtracking', self)
        self.button1.resize(360, 30)
        self.button1.move(20, 385)
        consolas = QFont()
        consolas.setFamily("Consolas")
        consolas.setPointSize(12)
        
        # self.button1.setFont(consolas)
        self.button1.setGeometry(QRect(10, 900, 100, 50))
        # connect the solve button to function on_solve_click
        self.button1.clicked.connect(self.Backtracking)
        self.button2 = QPushButton("Backtracking with forward checking", self)
        self.button3 = QPushButton("Backtracking with arc consistency", self)
        self.button4 = QPushButton("Close", self)
        self.button2.setGeometry(QRect(120, 900, 250, 50))
        self.button3.setGeometry(QRect(380, 900, 250, 50))
        self.button4.setGeometry(QRect(640, 900, 100, 50))
        #time view on gui 
        
        self.label_1 = QLabel("Backtracking time : ", self)
        self.label_1.setGeometry(QRect(900, 50, 800, 300))
        self.label_2 = QLabel("Backtracking with Forword Checking time: ", self)
        self.label_2.setGeometry(QRect(900, 100, 800, 300))
        self.label_3 = QLabel("Backtracking with arc consistency time: ", self)
        self.label_3.setGeometry(QRect(900, 150, 800, 300))
        
        
        consolas = QFont()
        consolas.setFamily("Consolas")
        consolas.setPointSize(15)
        self.label_1.setFont(consolas)
        self.label_2.setFont(consolas)
        self.label_3.setFont(consolas)
        #button1.clicked.connect(self. Backtracking)
        
        self.button2.clicked.connect(self. Backtracking_with_forward_checking)
        self.button3.clicked.connect(self.Backtracking_with_arc_consistency)
        self.button4.clicked.connect(self.Close)
        print(self.cliques)
        self.setWindowTitle('KENKEN PUZZLE')
        valid = validate(self.cliques)
        
        while(valid == False):
            self.size, self.cliques = generate(n)
            valid = validate(self.cliques)
        
        for members in self.cliques:
            random_number = randint(0, 16777215)
            hex_number = str(hex(random_number))
            color = '#' + hex_number[2:]
            flag = 0
            for member in members[0]:
                x, y = member
                i = x-1
                j = y-1
                flag = flag+1
                setattr(self, 'textbox%d%d' % (i, j), QTextEdit(self))
                getattr(self, 'textbox%d%d' % (i, j)).move(
                    20 + 92 * j, 20 + 92 * i)
                getattr(self, 'textbox%d%d' % (i, j)).resize(90, 90)
                getattr(self, 'textbox%d%d' % (i, j)).setAlignment(Qt.AlignTop)
                font = QFont()
                font.setFamily("Comic Sans MS")
                font.setPointSize(11)
                if(flag == 1):
                    if(members[1] == '.'):
                        getattr(self, 'textbox%d%d' %
                                (i, j)).setText(str(members[2]))
                    elif(members[1] == '*'):
                        getattr(self, 'textbox%d%d' %
                                (i, j)).setText(str(members[2])+' , *')
                    else:
                        getattr(self, 'textbox%d%d' % (i, j)).setText(
                            str(members[2])+' , '+members[1])

                getattr(self, 'textbox%d%d' % (i, j)).setFont(font)

                if use_color_A(i, j):
                    getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                        'background-color: %s;' % color)
                else:
                    getattr(self, 'textbox%d%d' % (i, j)).setStyleSheet(
                        'background-color: %s;' % color)
        
class Window (QMainWindow):
    def __init__(self):
        super().__init__()
        self.num = 0
        self.flag = 0
        self.w = AnotherWindow()
        title = "KenKen"
        top = 100
        left = 100
        width = 350
        height = 150
        iConName = "home.png"
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(iConName))
        self.setGeometry(left, top, width, height)
        self.CreateButton()
        self.size()
        self.show()
        # self.initUI()

    def show_new_window(self, checked):
        self.w.initUI(self.num)
       # self.w.buttons()
        self.w.setGeometry(50, 50, 950, 1000)
        self.w.display()

    def size(self):
        self.textbox = QTextEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)

    def on_click(self):
        textboxValue = self.textbox.toPlainText()
        if(int(textboxValue) > 9 or int(textboxValue) < 3):
            QMessageBox.question(self, 'Message - pythonspot.com',
                                 "Error" + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
            self.textbox.setText("")
        else:
            self.num = int(textboxValue)
            self.button.clicked.connect(self.show_new_window)

    def CreateButton(self):
        # Create a button in the window
        self.button = QPushButton('Enter Size', self)
        self.button.move(20, 80)
        # self.setCentralWidget(self.button)
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)


if __name__ == '__main__':
   # App=QApplication(sys.argv)
    # window=Window()
    # sys.exit(App.exec())

    #size, cliques = generate(list(stdin))

    #ken = Kenken(size, cliques)

    #assignment = algorithm_csp.backtracking_search(ken)

    # ken.display(assignment)
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()
    
    
    
    
    
