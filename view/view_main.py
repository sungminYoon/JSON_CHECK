"""
Created by SungMin Yoon on 2021-11-11..
Copyright (c) 2021 year NCC (National Cancer Center). All rights reserved.
"""

# 파이참 터미널에서 우측 명령어를 복사 붙여 넣기 해서 open cv 를 설치 합니다. -> pip3 install opencv-python
import cv2 as cv
from PySide6.QtGui import QImage, QPixmap
from PySide6 import QtWidgets, QtCore


class ViewMain(QtWidgets.QGraphicsView):
    screen_rect = None  # 화면에 보여지는 이미지 사각형 크기

    # QT 예제 기본 VIEW 구조
    def __init__(self, parent=None):
        super(ViewMain, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.q_graphic = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.q_graphic)
        self.setScene(self.scene)

    def setup(self):
        self.screen_rect: QtCore.QRectF = QtCore.QRectF(0.0, 0.0, 513, 513)
        self.setSceneRect(QtCore.QRectF(self.screen_rect))

    def set_image(self, cv_img):

        # 컬러 이미지로 변환
        cv_color_image = cv.cvtColor(cv_img, cv.COLOR_RGB2BGR)
        h, w = cv_color_image.shape[:2]

        # 화면에 보이는 이미지
        q_image = QImage(cv_color_image, w, h, QImage.Format_RGB888)
        p_image = QPixmap.fromImage(q_image)
        self.q_graphic.setPixmap(p_image)
        self.repaint()
        return cv_color_image

