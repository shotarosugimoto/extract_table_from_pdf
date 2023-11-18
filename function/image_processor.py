from function.matrix_erement import MatrixElement

import cv2
import numpy as np
import pandas as pd
from operator import itemgetter


class ImageProcessor:

    def __init__(self, image_path):
        self.image_path = image_path
        self.base_image = cv2.imread(image_path)
        self.processed_image = self.base_image.copy()
        self.processed_image[:] = (255, 255, 255)
        self.height, self.width = self.base_image.shape[:2]
        self.horizontal_lines = pd.DataFrame([['', '', '', '']])
        self.horizontal_lines.columns = ['x1', 'x2', 'y1', 'y2']
        self.vertical_lines = pd.DataFrame([['', '', '', '']])
        self.vertical_lines.columns = ['x1', 'x2', 'y1', 'y2']

        self.table_matrix = [[MatrixElement()]]

    def remove_word(self, x1, x2, y1, y2, pdf_width, pdf_height):
        x1 *= self.width/pdf_width
        x2 *= self.width / pdf_width
        y1 *= self.height/pdf_height
        y2 *= self.height / pdf_height
        points = np.array([[x1, y1], [x1, y2], [x2, y2], [x2, y1]], np.float32)
        points = np.int32(points)
        points = points.reshape((-1, 1, 2))
        cv2.fillPoly(self.processed_image, [points], (255, 255, 255))
        self.image_view()

    def tabel_detection(self):
        bgr_img = self.base_image
        img = bgr_img[:, :, 0]
        height, width = img.shape
        min_length_width = width * 0.5
        min_length_height = height * 0.1
        gap = 3
        judge_img = cv2.bitwise_not(img)
        th, judge_img = cv2.threshold(judge_img, 127, 255, cv2.THRESH_BINARY)

        lines = cv2.HoughLinesP(judge_img, rho=1, theta=np.pi / 360, threshold=100, minLineLength=min_length_width,
                                maxLineGap=10)

        line_list = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # 傾きが threshold_slope px以内の線を横線と判断
            threshold_slope = 3
            if abs(y1 - y2) < threshold_slope:
                x1 = line[0][0]
                y1 = line[0][1]
                x2 = line[0][2]
                y2 = line[0][3]
                line = (x1, y1, x2, y2)
                line_list.append(line)

        # y座標をキーとして並び変え
        line_list.sort(key=itemgetter(1, 0, 2, 3))

        hoz_line = 0
        hoz_line_list = []
        y1 = 0
        for line in line_list:
            judge_y1 = line[1]
            # ほぼ同じ位置の横線は除外
            if abs(judge_y1 - y1) < 3 and hoz_line_list != []:
                y1 = judge_y1
            else:
                y1 = judge_y1
                hoz_line_list.append(line)
                self.horizontal_lines.loc[hoz_line] = [
                    line[0], line[2], line[1], line[3]
                ]
                white_line = 3
                cv2.line(self.processed_image, (line[0], line[1]), (line[2], line[3]), (0, 0, 255), white_line)
                hoz_line = hoz_line + 1

        gap = 3
        lines = cv2.HoughLinesP(judge_img, rho=1, theta=np.pi / 360, threshold=100, minLineLength=min_length_height,
                                maxLineGap=gap)
        line_list = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            threshold_slope = 3
            if abs(x1 - x2) < threshold_slope:
                x1 = line[0][0]
                y1 = line[0][1]
                x2 = line[0][2]
                y2 = line[0][3]
                line = (x1, y1, x2, y2)
                line_list.append(line)
        line_list.sort(key=itemgetter(0, 1, 2, 3))
        ver_line = 0
        ver_line_list = []
        x1 = 0
        for line in line_list:
            judge_x1 = line[0]
            # ほぼ同じ位置の縦線は除外
            if abs(judge_x1 - x1) < 5 and ver_line_list != []:
                x1 = judge_x1
            else:
                white_line = 3
                cv2.line(self.processed_image, (line[0], line[1]), (line[2], line[3]), (0, 0, 255), white_line)
                x1 = judge_x1
                self.vertical_lines.loc[ver_line] = [
                    line[0], line[2], line[3], line[1]
                ]
                ver_line = ver_line + 1
                ver_line_list.append(line)
        for i in range(len(self.horizontal_lines)):
            y = self.horizontal_lines.at[i, 'y1']
            flag = False
            for j in range(len(self.vertical_lines)):
                y1 = self.vertical_lines.at[j, 'y1']
                y2 = self.vertical_lines.at[j, 'y2']
                if y1-3 <= y <= y2 + 3:
                    flag = True

            if not flag:
                print(i)
                self.horizontal_lines.drop(i, inplace=True)
                print(self.horizontal_lines)

        print('horizontal_list_pd')
        print(self.horizontal_lines)
        print('vertical_line_list')
        print(self.vertical_lines)

    def make_initial_matrix(self):
        row = self.horizontal_lines.shape[0] - 1
        col = self.vertical_lines.shape[0] - 1
        self.table_matrix = [[MatrixElement() for _ in range(col)] for _ in range(row)]

        y1_correct = self.horizontal_lines.at[0, 'y1']
        y2_correct = self.horizontal_lines.at[row, 'y1']
        for i in range(col):
            self.vertical_lines[i, 'y1'] = y1_correct
            self.vertical_lines[i, 'y2'] = y2_correct

        for i in range(row):
            y1 = self.horizontal_lines.at[i, 'y1']
            y2 = self.horizontal_lines.at[i+1, 'y1']
            for j in range(col):
                element = self.table_matrix[i][j]
                element.change_y1(y1)
                element.change_y2(y2)

        for i in range(col):
            x1 = self.vertical_lines.at[i, 'x1']
            x2 = self.vertical_lines.at[i+1, 'x1']
            for j in range(row):
                element = self.table_matrix[j][i]
                element.change_x1(x1)
                element.change_x2(x2)

    def add_word_to_matrix(self, x1, x2, y1, y2, pdf_width, pdf_height, word):
        row = self.horizontal_lines.shape[0] - 1
        col = self.vertical_lines.shape[0] - 1
        x1 *= self.width / pdf_width
        x2 *= self.width / pdf_width
        y1 *= self.height / pdf_height
        y2 *= self.height / pdf_height

        for i in range(row):
            for j in range(col):
                element = self.table_matrix[i][j]
                if element.x1 < x1 < element.x2 and element.y1 < y1 < element.y2:
                    element.change_word(word)
                    return

    def view_matrix(self):
        row = self.horizontal_lines.shape[0] - 1
        col = self.vertical_lines.shape[0] - 1
        for i in range(row):
            for j in range(col):
                element = self.table_matrix[i][j]
                print(element.x1, element.x2, element.y1, element.y2, element.word)

    def image_view(self):
        cv2.imshow('Image', self.processed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
