from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import sys


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('iPhone Style Calculator')
        self.setFixedSize(320, 500)
        self.setStyleSheet('background-color: black;')
        self.expression = ''
        self.last_input = ''
        self.create_ui()

    def create_ui(self):
        layout = QVBoxLayout()
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet(
            'font-family: "Segoe UI", "Helvetica", "Arial", sans-serif; '
            'font-size: 36px; height: 80px; color: white; '
            'background-color: black; border: none;'
        )
        layout.addWidget(self.display)

        grid = QGridLayout()

        buttons = [
            ['AC', '+/-', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+']
        ]

        font_style = 'font-family: "Segoe UI", "Helvetica", "Arial", sans-serif; font-size: 20px; border-radius: 32px;'
        gray_style = f'{font_style} background-color: #a5a5a5; color: black;'
        dark_style = f'{font_style} background-color: #333333; color: white; padding-top: 2px;'
        orange_style = f'{font_style} background-color: orange; color: white;'

        for i in range(4):
            for j in range(4):
                text = buttons[i][j]
                button = QPushButton(text)
                button.setFixedSize(65, 65)
                button.setStyleSheet(gray_style if text in {'AC', '+/-', '%'}
                                     else orange_style if text in {'/', '*', '-', '+'}
                                     else dark_style)
                grid.addWidget(button, i, j)
                button.clicked.connect(self.on_click)

        zero_button = QPushButton('0')
        zero_button.setFixedSize(140, 65)
        zero_button.setStyleSheet(dark_style + ' text-align: left; padding-left: 26px; padding-top: 2px;')
        grid.addWidget(zero_button, 4, 0, 1, 2)
        zero_button.clicked.connect(self.on_click)

        dot_button = QPushButton('.')
        dot_button.setFixedSize(65, 65)
        dot_button.setStyleSheet(dark_style)
        grid.addWidget(dot_button, 4, 2)
        dot_button.clicked.connect(self.on_click)

        equal_button = QPushButton('=')
        equal_button.setFixedSize(65, 65)
        equal_button.setStyleSheet(orange_style)
        grid.addWidget(equal_button, 4, 3)
        equal_button.clicked.connect(self.on_click)

        layout.addLayout(grid)
        self.setLayout(layout)

    def on_click(self):
        button = self.sender()
        text = button.text()

        if text == 'AC':
            self.reset()
        elif text == '+/-':
            self.negative_positive()
        elif text == '%':
            self.percent()
        elif text == '=':
            self.equal()
        else:
            self.input_value(text)

    def reset(self):
        self.expression = ''
        self.last_input = ''
        self.display.setText('')
        self.update_font()

    def negative_positive(self):
        try:
            if self.expression:
                if self.expression.startswith('-'):
                    self.expression = self.expression[1:]
                else:
                    self.expression = '-' + self.expression
                self.display.setText(self.expression)
        except Exception:
            self.display.setText('Error')
            self.expression = ''
        self.update_font()

    def percent(self):
        try:
            if self.expression:
                value = float(self.expression)
                value /= 100
                self.expression = str(value)
                self.display.setText(self.format_result(value))
        except Exception:
            self.display.setText('Error')
            self.expression = ''
        self.update_font()

    def input_value(self, value):
        if value == '.' and '.' in self.expression.split()[-1]:
            return
        self.expression += value
        self.display.setText(self.expression)
        self.update_font()

    def equal(self):
        try:
            result = eval(self.expression)
            if isinstance(result, float):
                result = round(result, 6)
            self.display.setText(self.format_result(result))
            self.expression = str(result)
        except ZeroDivisionError:
            self.display.setText('Divide by 0 Error')
            self.expression = ''
        except Exception:
            self.display.setText('Error')
            self.expression = ''
        self.update_font()

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError
        return a / b

    def format_result(self, result):
        result_str = str(result)
        if '.' in result_str:
            result_str = str(round(float(result), 6))
            result_str = result_str.rstrip('0').rstrip('.') if '.' in result_str else result_str
        return result_str

    def update_font(self):
        text = self.display.text()
        length = len(text)
        if length > 12:
            font_size = '24px'
        elif length > 8:
            font_size = '30px'
        else:
            font_size = '36px'

        self.display.setStyleSheet(
            f'font-family: "Segoe UI", "Helvetica", "Arial", sans-serif; '
            f'font-size: {font_size}; height: 80px; color: white; '
            f'background-color: black; border: none;'
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())
