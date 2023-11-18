class MatrixElement:
    def __init__(self):
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.word = ''

    def change_x1(self, x1):
        self.x1 = x1

    def change_x2(self, x2):
        self.x2 = x2

    def change_y1(self, y1):
        self.y1 = y1

    def change_y2(self, y2):
        self.y2 = y2

    def change_word(self, word):
        self.word += word
