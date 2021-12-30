"""
Created by SungMin Yoon on 2021-11-10..
Copyright (c) 2021 year NCC (National Cancer Center). All rights reserved.
"""


import sys
from PySide6.QtWidgets import QApplication
from windows import Window


if __name__ == '__main__':
    print('main')

    app = QApplication(sys.argv)
    window: Window = Window()
    sys.exit(app.exec())

