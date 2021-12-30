"""
Created by SungMin Yoon on 2021-11-10..
Copyright (c) 2021 year NCC (National Cancer Center). All rights reserved.
"""
import json
import cv2 as cv

from PySide6 import QtCore
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout

from view.view_main import ViewMain     # 화면 뷰 입니다.
from common import file_manager         # 사용자 파일 열기에 사용 됩니다.


class Window(QWidget):
    """
        * 용어 정리
        - 넘버: CT 이미지 번호 입니다.
        - roi 그룹: CT 이미지에 속한 각각의 roi 를 구분 하는 번호 입니다.
    """
    view = None             # 화면에 보여지는 image VIEW 입니다.
    img = None              # 화면에 보여지는 CV image 입니다.
    img_open_btn = None     # 사용자 이미지 열기 버튼 입니다.
    img_number = None         # 사용자 선택한 이미지 정보 입니다.
    json_open_btn = None    # 사용자 json 열기 버튼 입니다.
    json_data = None        # json 파일에서 읽어드린 json data 입니다.

    roi_list: list  # 컨투어 좌표 리스트 입니다.

    def __init__(self):
        super().__init__()
        print('Window: init')

        # roi 리스트 생성
        self.roi_list = []

        # 윈도우 세팅
        self.setWindowTitle('Test auto ROI')
        self.setGeometry(0, 0, 630, 540)

        # View 생성
        self.view = ViewMain()
        self.view.setup()

        # ui
        self.ui_setup()

    def ui_setup(self):
        print('ui_setup')

        # 레이아웃 생성
        form_box = QHBoxLayout()
        btn_box = QVBoxLayout()

        # image view 정렬
        self.view.setAlignment(QtCore.Qt.AlignTop)

        # 이미지 열기 버튼
        self.img_open_btn = QPushButton('IMAGE_OPEN')
        self.img_open_btn.clicked.connect(self.openButtonClicked)

        # json 열기 버튼
        self.json_open_btn = QPushButton('JSON_OPEN')
        self.json_open_btn.clicked.connect(self.jsonButtonClicked)

        # 버튼 박스에 위젯 넣기
        btn_box.addWidget(self.img_open_btn, alignment=QtCore.Qt.AlignTop)
        btn_box.addWidget(self.json_open_btn, alignment=QtCore.Qt.AlignTop)

        # 폼박스에 위젯 넣기
        form_box.addLayout(btn_box)
        form_box.addWidget(self.view, alignment=QtCore.Qt.AlignRight)

        # 레이아웃에 폼박스 등록
        self.setLayout(form_box)
        self.show()

    def openButtonClicked(self):
        print('openButtonClicked')

        # 사용자가 선택한 파일경로
        file_path = file_manager.file_open()

        # 경로가 없으면 리턴!
        if file_path is 0:
            return

        # 사용자가 선택한 파일이름
        last_name = file_path[file_path.rfind('/') + 1:]
        image_folder = file_path.replace(last_name, '', 1)

        # 파일 이름에서 이미지 "넘버(세자리)"만 가져오기
        a = last_name[-7]
        b = last_name[-6]
        c = last_name[-5]
        number = f'{a}{b}{c}'

        # 사용자 선택 이미지 "넘버" int 형 변환 저장
        self.img_number = int(number)
        print('select image number = ', self.img_number)

        # 이미지 경로 확인
        path = f'{image_folder}{last_name}'

        # 이미지 경로를 사용해 cv 이미지를 만들고
        cv_image = cv.imread(path, 0)

        # 보여지는 뷰에 이미지 경로 입력
        self.img = self.view.set_image(cv_image)

    def jsonButtonClicked(self):
        print('jsonButtonClicked')

        # 변수 초기화
        self.json_data = None
        self.roi_list.clear()

        # 사용자가 선택한 파일경로
        file_path = file_manager.file_open()

        # 경로가 없으면 리턴!
        if file_path is 0:
            return

        # 사용자가 선택한 파일이름
        last_name = file_path[file_path.rfind('/') + 1:]
        json_folder = file_path.replace(last_name, '', 1)

        # json 파일 이름 들을 가저 옵니다.
        _json_list = file_manager.file_json_list(json_folder)
        print(_json_list)

        # 리스트 에서 마지막 json 파일을 가지고 옵니다.
        if len(_json_list) > 0:
            _json = _json_list[-1]
            path = f'{json_folder}{_json}'

            # json 파일을 읽고 파싱 합니다.
            with open(path, 'r') as f:
                self.json_data = json.load(f)
                self.json_parsing()

        # 파싱 완료 후 roi 를 그려 줍니다.
        self.draw_roi()

    # json 데이터를 분석 합니다.
    def json_parsing(self):
        print('json_parsing')

        # 딕셔너리 data 를 하나씩 꺼내 옵니다.
        for data in self.json_data:

            # 딕셔너리 에서 값을 가지고 옵니다.
            number = data["number"]
            contours = data["contours"]

            # 컨투어즈 에서 키 값을 가져 옵니다.
            for key in contours:

                # 문자열로 변환 합니다.
                str_key = f"{key}"

                # key 값(roi 그룹 넘버)을 사용해 포지션 그룹 데이터를 가지고 옵니다.
                position_group = contours[str_key]

                # roi 리스트에 "이미지 넘버, roi 그룹 넘버, 좌표 그룹을 저장 합니다."
                t = (number, str_key, position_group)
                self.roi_list.append(t)

    def draw_roi(self):
        print('draw_roi')

        # 점표시 리스트
        dot_line = []

        ''' 점 표시 '''
        # roi 리스트 에서 객체를 가져 옵니다.
        for obj in self.roi_list:
            number, group, position_list = obj

            # 이미지 넘버 숫자와 객체의 "넘버"가 일치 하면
            if number == self.img_number:

                # 좌표 정보 리스트에서 가져오기
                i = 0
                for position in position_list:

                    # 점의 시작과 끝을 표시
                    if i == 0:
                        point = 'start'
                    if len(position_list)-1 == i:
                        point = 'end'
                    if 0 < i < len(position_list)-1:
                        point = 'middle'
                    i = i + 1

                    # 딕셔너리 에서 포지션 값을 가지고 옵니다.
                    x = position["x"]
                    y = position["y"]

                    # 좌표를 인트형으로 변환하고
                    int_x = int(x)
                    int_y = int(y)

                    # 튜퓰에 넣은 다음
                    farthest = (int_x, int_y)

                    # 점 그리기
                    cv.circle(self.img, farthest, 1, (0, 0, 255), -1)

                    # 그룹과 점, 포인트 저장
                    t = (group, int_x, int_y, point)
                    dot_line.append(t)

        ''' 선 그리기 '''
        # 선 표시 카운트
        count = 0

        # 선의 처음과 끝
        start = None
        end = None

        for _ in dot_line:

            # 인덱스 오버 방지
            if count < len(dot_line)-1:

                # 객체 가져오기
                obj1 = dot_line[count]
                obj2 = dot_line[count + 1]

                # 객체를 변수에 대입
                group1, x1, y1, point1 = obj1
                group2, x2, y2, point2 = obj2

                # int 형 변환
                int_group1 = int(group1)
                int_group2 = int(group2)

                # 좌표 튜플
                pt1 = (x1, y1)
                pt2 = (x2, y2)

                # 점의 처음과 끝을 저장
                if point1 == 'start':
                    start = pt1
                if point2 == 'end':
                    end = pt2

                # roi 그룹이 동일 할때만 선 그리기
                if int_group1 == int_group2:

                    # 선 그리기
                    self.img = cv.line(self.img, pt1, pt2, (255, 0, 0), 1)

                # 처음과 마지막 점 선 그려 주기
                if end is not None:
                    self.img = cv.line(self.img, start, end, (255, 0, 0), 1)
                    end = None

            # 다음
            count = count + 1

        ''' 화면 표시 '''
        # 화면을 업데이트 합니다.
        self.view.set_image(self.img)
        self.view.repaint()


