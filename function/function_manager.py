from function.pdf_processor import PDFProcessor
from function.image_processor import ImageProcessor
import csv


class FunctionManager:

    def __init__(self, pdf_name):
        self.pdf_name = pdf_name
        self.pdf_path = f'source/pdf/{pdf_name}.pdf'
        self.image_path = f'source/image/{pdf_name}.png'

        self.pdf_processor = PDFProcessor(self.pdf_path, pdf_name)
        # self.pdf_processor.words_loading()
        self.pdf_processor.extract_text_and_coordinates()

        self.image_processor = ImageProcessor(self.image_path)

    def remove_words(self):
        self.pdf_processor.remove_words_from_image(self.image_processor)

    def make_matrix(self):
        self.image_processor.tabel_detection()
        self.image_processor.image_view()
        self.image_processor.make_initial_matrix()
        self.pdf_processor.add_words_to_matrix(self.image_processor)

    def make_csv_from_matrix(self):
        table_matrix = self.image_processor.table_matrix
        row = len(table_matrix)
        col = len(table_matrix[0])

        csv_matrix = [[0 for _ in range(col)] for _ in range(row)]
        for i in range(row):
            for j in range(col):
                element = table_matrix[i][j]
                csv_matrix[i][j] = element.word

        with open(f'result/{self.pdf_name}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(csv_matrix)

