import json
import sys
import typing
from dataclasses import dataclass

from graphical_tree import GraphicalTree, Vertex
from PyQt6 import QtWidgets, uic


@dataclass(frozen=True)
class Grammar:
    VT: typing.List[str]
    VN: typing.List[str]
    P: typing.Dict[str, typing.List[str]]
    S: str


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('mainWindow.ui', self) # Load the .ui file
        self.show() # Show the GUI
        self.pathButton.clicked.connect(self.getPath)
        self.treeButton.clicked.connect(self.generateSequenses)
        self.pathLine.textChanged.connect(self.checkEmptyPathLine)
        self.pushButton.clicked.connect(self.drawTree)
    def getPath(self):
        path = QtWidgets.QFileDialog.getOpenFileName()
        print(path)
        self.pathLine.setText(path[0])
        self.gramText.setEnabled(False)

    def checkEmptyPathLine(self):
        if self.pathLine.text() == '':
            self.gramText.setEnabled(True)

    def throwMessageBox(self, windowTitle: str, message: str):
        mes = QtWidgets.QMessageBox(self)
        mes.show()
        mes.setWindowTitle(windowTitle)
        mes.setText(message)
    def generateSequenses(self):

        try:
            if not self.gramText.isEnabled():
                with open(self.pathLine.text(), 'r') as file:
                    self.G = Grammar(**json.load(file))
            else:
                print(self.gramText.toPlainText())
                self.G = Grammar(**json.loads(self.gramText.toPlainText()))
        except (json.JSONDecodeError, TypeError):
            self.throwMessageBox("Ошибка", "Файл грамматики некоректен")
            return

        self.range_ = (self.rangeSpin1.value(), self.rangeSpin2.value())
        if self.range_[0] > self.range_[1]:
            self.range_[0], self.range_[1] = self.range_[1], self.range_[0]

        stack = [([], self.G.S)]
        was_in_stack = set()
        counter = 1
        self.ans = []
        try:
            while stack:
                prev, sequence = stack.pop()
                prev = prev.copy()
                prev.append(sequence)
                if sequence in was_in_stack:
                    continue
                was_in_stack.add(sequence)
                only_term = True
                for i, symbol in enumerate(sequence):
                    if symbol in self.G.VN:
                        only_term = False
                        for elem in self.G.P[symbol]:
                            scopy = sequence[:i] + elem + sequence[i + 1:]
                            if len(scopy) <= self.range_[1] + 3:
                                stack.append((prev, scopy))
                if only_term and self.range_[0] <= len(sequence) <= self.range_[1]:
                    self.ans.append(prev)
                    #print(f"[{counter}]", sequence if sequence else "λ")
                    counter += 1
        except KeyError:
            self.throwMessageBox("Ошибка", "Грамматика задана некорректно!")
            return

        answers = ""
        for i in range(len(self.ans)):
            for j in self.ans[i]:
                answers += str(str(i + 1) + ") " + str(j) + str("-->")
            answers = answers[:len(answers) - 3]
            answers += "\n"
        self.textEdit.setText(answers)

    def drawTree(self):
        if self.textEdit.toPlainText() == '':
            self.throwMessageBox("Ошибка", "Сгенерируйте цепочки")
            return
        if self.spinBox.value() < 1 or self.spinBox.value() > len(self.ans):
            self.throwMessageBox("Ошибка", "Укажите число соответствующее номеру цепочки")
            return
        choised_ans = self.ans[self.spinBox.value() - 1]

        def get_changes(current, next):
            if len(next) < len(current):
                return "λ"
            for i, ch in enumerate(current[::-1]):
                i = len(current) - i - 1
                if ch in self.G.VN:
                    return next[i: i + len(next) - len(current) + 1]

        def get_right_vertex(tree):
            if not tree.children and tree.data in self.G.VN:
                return tree
            for vert in tree.children[::-1]:
                v = get_right_vertex(vert)
                if v:
                    return v

        tree = Vertex(choised_ans[0])
        for curr, next in zip(choised_ans, choised_ans[1:]):
            changes = get_changes(curr, next)
            v = get_right_vertex(tree)
            v.children = list(map(Vertex, changes))

        gt = GraphicalTree(tree)
        gt.start()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()


