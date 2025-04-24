from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import sys

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('iPhone Style Calculator')
        self.setFixedSize(320, 500)
        self.setStyleSheet('background-color: black;')
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
        self.expression = ''

        buttons = [
            ['AC', '+/-', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+']
        ]

        # 스타일 설정 (폰트 적용)
        font_style = 'font-family: "Segoe UI", "Helvetica", "Arial", sans-serif; font-size: 20px; border-radius: 32px;'

        gray_style = f'{font_style} background-color: #a5a5a5; color: black;'
        dark_style = (
            'font-family: "Segoe UI", "Helvetica", "Arial", sans-serif;'
            'font-size: 20px;'
            'border-radius: 32px;'
            'background-color: #333333;'
            'color: white;'
            'padding-top: 2px;'  # 💡 살짝 아래로 내려줌!
)
        orange_style = f'{font_style} background-color: orange; color: white;'

        # 상단 4줄 버튼 자동 배치
        for i in range(4):
            for j in range(4):
                text = buttons[i][j]
                button = QPushButton(text)
                button.setFixedSize(65, 65)

                if text in {'AC', '+/-', '%'}:
                    button.setStyleSheet(gray_style)
                elif text in {'/', '*', '-', '+'}:
                    button.setStyleSheet(orange_style)
                else:
                    button.setStyleSheet(dark_style)

                grid.addWidget(button, i, j)
                button.clicked.connect(self.on_click)

        # 마지막 줄 수동 배치
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
            self.expression = ''
            self.display.setText('')
        elif text == '+/-':
            if self.expression.startswith('-'):
                self.expression = self.expression[1:]
            else:
                self.expression = '-' + self.expression
            self.display.setText(self.expression)
        elif text == '=':
            try:
                result = str(eval(self.expression))
                self.display.setText(result)
                self.expression = result
            except Exception:
                self.display.setText('Error')
                self.expression = ''
        else:
            self.expression += text
            self.display.setText(self.expression)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())
