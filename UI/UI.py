from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QLabel,
                             QPlainTextEdit, QHBoxLayout, QVBoxLayout,
                             QApplication, QSizePolicy, QComboBox, QLineEdit,
                             QFileDialog, QListWidget)
from PyQt5.QtGui import (QResizeEvent, QFont)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys
import os
from Manager import Manager, Methods
import re
from typing import List


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.width: any = None
        self.height: any = None

        self.input_open_button: QPushButton = None
        self.input_clear_button: QPushButton = None
        self.input_list: QListWidget = None
        self.input_input_label: QLabel = None

        self.method_calculate_button: QPushButton = None
        self.method_reset_button: QPushButton = None
        self.method_combobox: QComboBox = None
        self.method_method_used_label: QLabel = None
        self.method_intial_interval_textbox: QPlainTextEdit = None

        self.output_save_button: QPushButton = None
        self.output_clear_button: QPushButton = None
        self.output_textbox: QPlainTextEdit = None
        self.output_output_label: QLabel = None

        # graph part with self.figure variables
        # 3d
        self.figure1 = plt.figure()
        self.canvas1 = FigureCanvas(self.figure1)

        # 2d
        self.figure2 = plt.figure()
        self.canvas2 = FigureCanvas(self.figure2)

        self.grid_layout: QGridLayout = None

        self.open_file_location: str = os.path.dirname(os.path.abspath(__file__))
        self.save_file_location: str = os.path.dirname(os.path.abspath(__file__))

        self.methods = list(Methods.keys())

        self.initUI()

    def initUI(self):
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.grid_layout.setHorizontalSpacing(50)

        # create 5 blocks
        self.create_input_block()
        self.create_method_used_block()
        self.create_output_block()
        self.create_graph_block()

        self.setGeometry(170, 300, 1600, 500)
        self.setMinimumSize(1600, 500)
        self.setWindowTitle('Project2-Optimization')

        self.width = self.frameGeometry().width()
        self.height = self.frameGeometry().height()
        self.show()

    def create_input_block(self):

        self.input_open_button = QPushButton("open")
        self.input_open_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.input_open_button.clicked.connect(self.open_file_dialog)

        self.input_clear_button = QPushButton("clear")
        self.input_clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.input_clear_button.clicked.connect(self.input_clear)

        self.input_input_label = QLabel('Input:')

        input_h_box = QHBoxLayout()
        input_h_box.addWidget(self.input_open_button)
        input_h_box.addSpacing(50)
        input_h_box.addWidget(self.input_clear_button)

        self.input_list = QListWidget()

        input_v_box = QVBoxLayout()
        input_v_box.addWidget(self.input_input_label)
        input_v_box.addWidget(self.input_list)

        input_v_box.addLayout(input_h_box)
        self.grid_layout.addLayout(input_v_box, 0, 0)

    def create_method_used_block(self):
        # Combo Box to be used
        self.method_combobox = QComboBox(self)
        self.method_combobox.addItems(self.methods)

        # Buttons to be used
        self.method_reset_button = QPushButton("reset")
        self.method_reset_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.method_reset_button.clicked.connect(self.method_reset)

        self.method_calculate_button = QPushButton("calculate")
        self.method_calculate_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.method_calculate_button.clicked.connect(self.method_calculate)

        # Qlabel to be used
        self.method_method_used_label = QLabel('Method Used:')

        self.method_intial_interval_textbox = QPlainTextEdit()

        method_h2_box = QHBoxLayout()
        method_h2_box.addWidget(self.method_reset_button)
        method_h2_box.addWidget(self.method_calculate_button)

        method_v_box = QVBoxLayout()
        method_v_box.addWidget(self.method_method_used_label)
        method_v_box.addWidget(self.method_combobox)
        method_v_box.addWidget(self.method_intial_interval_textbox)

        method_v_box.addLayout(method_h2_box)
        self.grid_layout.addLayout(method_v_box, 0, 1)

    def create_output_block(self):

        self.output_save_button = QPushButton("save")
        self.output_save_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.output_save_button.clicked.connect(self.save_file_dialog)

        self.output_clear_button = QPushButton("clear")
        self.output_clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.output_output_label = QLabel('Output:')

        output_h_box = QHBoxLayout()
        output_h_box.addWidget(self.output_save_button)
        output_h_box.addWidget(self.output_clear_button)

        self.output_textbox = QPlainTextEdit(QWidget().resize(640, 480))

        output_v_box = QVBoxLayout()
        output_v_box.addWidget(self.output_output_label)
        output_v_box.addWidget(self.output_textbox)

        output_v_box.addLayout(output_h_box)
        self.grid_layout.addLayout(output_v_box, 1, 0, 1, 2)

    # def create_variable_block(self):
    #
    #     self.variable_clear_button = QPushButton("clear")
    #     self.variable_clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    #
    #     self.variable_variable_label = QLabel('Variables:')
    #
    #     self.variable_textbox = QPlainTextEdit(QWidget().resize(640, 480))
    #     self.variable_textbox.setReadOnly(True)
    #
    #     output_v_box = QVBoxLayout()
    #     output_v_box.addWidget(self.variable_variable_label)
    #     output_v_box.addWidget(self.variable_textbox)
    #     output_v_box.addWidget(self.variable_clear_button)
    #
    #     self.grid_layout.addLayout(output_v_box, 1, 1)

    def create_graph_block(self):
        ''' plot some random stuff '''
        self.figure1.suptitle('3d')
        self.figure2.suptitle('2d')

        ax1 = self.figure1.add_subplot(111, projection='3d')
        x = y = np.arange(-3.0, 3.0, 0.05)
        X, Y = np.meshgrid(x, y)
        zs = np.array(X**3 + Y**3)
        Z = zs.reshape(X.shape)
        ax1.plot_surface(X, Y, Z)
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        ax1.set_zlabel('z')

        ax2 = self.figure2.add_subplot(111)
        ax2.contour(X, Y, Z)
        ax2.set_xlabel('x')
        ax2.set_ylabel('y')

        self.canvas1.draw()
        self.canvas2.draw()
        # self.figure2.legend()

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()

        hbox1.addWidget(self.canvas1)
        hbox2.addWidget(self.canvas2)

        self.grid_layout.addLayout(hbox1, 0, 2, 2, 1)
        self.grid_layout.addLayout(hbox2, 0, 3, 2, 1)

    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", self.open_file_location, "Text Files (*.txt)")
        temp_pos = filename.rfind('/')
        if temp_pos:
            self.open_file_location = filename[: temp_pos + 1]

        if filename:
            with open(filename, 'r', encoding='utf8') as file:
                read_data = file.read()
                read_data_list = read_data.splitlines()
                self.input_list.addItems(read_data_list)

    def save_file_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", self.save_file_location,
                                                  "Text Files (*.txt)")
        temp_pos = filename.rfind('/')
        self.save_file_location = filename[: temp_pos + 1]

        if filename:
            with open(filename, 'w') as file:
                file.write(self.output_textbox.toPlainText())

            self.output_textbox.clear()

    def input_clear(self):
        self.input_list.clear()

    def method_reset(self):
        self.method_intial_interval_textbox.setPlainText('')
        self.method_combobox.setCurrentIndex(0)

    def method_calculate(self):
        initial_interval = self.method_intial_interval_textbox.toPlainText()
        method = self.method_combobox.currentText()
        equation_str = self.input_list.currentItem()

        if equation_str is None or method == 'None----' or initial_interval == '':
            assert False

        equation_str = equation_str.text()
        # get initial point and intervals
        initial_point, intervals = get_ip_intervals(initial_interval)

        manager = Manager(equation_str, method, initial_point, intervals)
        manager.run()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        HeightIncreasement = self.frameGeometry().height() - self.height
        temp_size = 30

        if abs(HeightIncreasement) - temp_size >= 0:
            # no pointer could be used in python
            self.change_font(self.input_input_label, HeightIncreasement / temp_size)
            self.change_font(self.method_method_used_label, HeightIncreasement / temp_size)
            self.change_font(self.output_output_label, HeightIncreasement / temp_size)
            self.change_font(self.input_open_button, HeightIncreasement / temp_size)
            self.change_font(self.input_clear_button, HeightIncreasement / temp_size)
            self.change_font(self.method_calculate_button, HeightIncreasement / temp_size)
            self.change_font(self.method_reset_button, HeightIncreasement / temp_size)
            self.change_font(self.output_save_button, HeightIncreasement / temp_size)
            self.change_font(self.output_clear_button, HeightIncreasement / temp_size)
            self.change_font(self.method_combobox, HeightIncreasement / temp_size)

            self.width = self.frameGeometry().width()
            self.height = self.frameGeometry().height()

    @staticmethod
    def change_font(label: QLabel, increasement: int):
        font = label.font()
        font.setPointSize(font.pointSize() + increasement)
        if font.pointSize() > 8:
            label.setFont(font)


def get_ip_intervals(initial_interval: str):
    initial_interval = initial_interval.split('\n', 1)

    # initial point parts
    initial_point_list = re.split(r'[:=]', initial_interval[0].replace(" ", ""))
    # now initial_point_list contains 3 elements, which is 'initial' , [var..], [initial_point..]
    vars_form = re.findall(r'\w', initial_point_list[1])
    initial_point = list_string_float(re.findall(r'[-+]?\d*\.\d+|\d+', initial_point_list[2]))

    # interval parts
    intervals = []

    # if interval spotted
    interval_list = initial_interval[1].splitlines()

    if len(interval_list) == 2:
        for i in range(len(vars_form)):
            intervals.append(list_string_float(re.findall(r'[-+]?\d*\.\d+|\d+', interval_list[i+1])))

    return initial_point, intervals


def list_string_float(string_list: List[str]):
    float_list = []
    for i in range(len(string_list)):
        float_list.append(float(string_list[i]))
    return float_list


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UI()
    sys.exit(app.exec_())