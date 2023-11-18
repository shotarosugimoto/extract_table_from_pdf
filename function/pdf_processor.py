from function.image_processor import ImageProcessor

from pdf2image import convert_from_path
import PyPDF2
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.pdfpage import PDFPage
from pdfminer3.layout import LAParams, LTTextContainer
import pandas as pd
import fitz


class PDFProcessor:

    def __init__(self, pdf_path, pdf_name):
        self.pdf_name = pdf_name
        self.pdf_path = pdf_path
        self.width = 0
        self.height = 0
        images = convert_from_path(self.pdf_path, dpi=300)
        for image in images:
            image.save(f'source/image/{pdf_name}.png', 'png')

        list1 = ['', '', '', '', '', '']
        self.word_table = pd.DataFrame([list1])
        self.word_table.columns = ['page', 'word', 'x1', 'x2', 'y1', 'y2']

    @staticmethod
    def pdfminer_config(line_overlap, word_margin, char_margin, line_margin, detect_vertical):
        la_params = LAParams(
            line_overlap=line_overlap,
            word_margin=word_margin,
            char_margin=char_margin,
            line_margin=line_margin,
            detect_vertical=detect_vertical
        )
        resource_manager = PDFResourceManager()
        device = PDFPageAggregator(resource_manager, laparams=la_params)
        interpreter = PDFPageInterpreter(resource_manager, device)
        return interpreter, device

    def words_loading(self):
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            self.width = float(reader.pages[0].mediabox.width)
            self.height = float(reader.pages[0].mediabox.height)

        with open(self.pdf_path, 'rb') as fp:
            dx1 = 0
            dx2 = 0
            dy1 = 0
            dy2 = 0
            if self.pdf_name == 'test1':
                dy1 = 5
            if self.pdf_name == 'test2':
                dy1 = 3
                dy2 = -1
            if self.pdf_name == 'test3':
                dx1 = 1
            int_page = 0
            ii_index = 0
            # interpreter = PDFPageInterpreter(resourceManager, device)
            interpreter, device = self.pdfminer_config(
                line_overlap=0.1,
                word_margin=0.1,
                char_margin=0.1,
                line_margin=0.05,
                detect_vertical=False
            )
            for page in PDFPage.get_pages(fp):
                int_page = int_page + 1
                interpreter.process_page(page)
                layout = device.get_result()
                for lt in layout:
                    if isinstance(lt, LTTextContainer):
                        self.word_table.loc[ii_index] = [
                            int_page,
                            lt.get_text().strip(),
                            lt.x0 + dx1,
                            lt.x1 + dx2,
                            self.height-lt.y1 + dy1,
                            self.height-lt.y0 + dy2,
                        ]
                        print(lt.get_text().strip())
                        ii_index = ii_index + 1

    def remove_words_from_image(self, image_processor: ImageProcessor):
        for i in range(len(self.word_table)):
            row = self.word_table.loc[i]
            image_processor.remove_word(
                x1=row['x1'],
                x2=row['x2'],
                y1=row['y1'],
                y2=row['y2'],
                pdf_width=self.width,
                pdf_height=self.height,
            )

    def extract_text_and_coordinates(self):
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            self.width = float(reader.pages[0].mediabox.width)
            self.height = float(reader.pages[0].mediabox.height)
        # PDFファイルを開く
        doc = fitz.open(self.pdf_path)

        ii_index = 0
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # ページからテキストと座標を抽出
            check_x = 0
            for text in page.get_text("rawdict", sort=True)["blocks"]:
                if "lines" in text:  # テキストブロックを確認
                    for line in text["lines"]:
                        for span in line["spans"]:
                            for char in span["chars"]:
                                if char['c'] == ' ':
                                    continue
                                if abs(check_x - char['bbox'][0]) > 5:
                                    self.word_table.loc[ii_index] = [
                                        page_num,
                                        char['c'],
                                        char['bbox'][0],
                                        char['bbox'][2],
                                        char['bbox'][1],
                                        char['bbox'][3],
                                    ]
                                    ii_index += 1
                                else:
                                    self.word_table.at[ii_index-1, 'word'] += char['c']
                                check_x = char['bbox'][2]
        print(self.word_table)
        doc.close()

    def add_words_to_matrix(self, image_processor: ImageProcessor):
        for i in range(len(self.word_table)):
            row = self.word_table.loc[i]
            image_processor.add_word_to_matrix(
                x1=row['x1'],
                x2=row['x2'],
                y1=row['y1'],
                y2=row['y2'],
                pdf_width=self.width,
                pdf_height=self.height,
                word=row['word']
            )

    def find_table(self):
        doc = fitz.open(self.pdf_path)
        page = doc[0]
        tabs = page.find_tables()
        tab = tabs[1]
        df = tab.to_pandas()
        print(df)
        df.to_csv('result/aaa.csv', index=False)