import PyPDF2
import pdfplumber
import pytesseract
import os
import tempfile

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
from PIL import Image
from pdf2image import convert_from_path


class PDFParser:
    """Парсер для PDF-файлов."""

    def __init__(self, path):
        self.path = path
        # Объект файла PDF
        self.pdfFileObj = open(path, 'rb')
        # Объект считывателя PDF
        self.pdfReaded = PyPDF2.PdfReader(self.pdfFileObj)
        # Объект pdfplumber для повторного использования
        self.pdfplumber_obj = pdfplumber.open(path)

        # Cловарь для извлечения текста из каждого изображения
        self.text_per_page = {}

    def parse(self):
        """Парсинг файла."""

        try:
            for page_num, page in enumerate(extract_pages(self.path)):
                print(f"\rОбработка: {page_num}", end="", flush=True)

                # Инициализируем переменные, необходимые для извлечения текста со страницы
                lower_side = None
                upper_side = None
                pageObj = self.pdfReaded.pages[page_num]
                page_text = []
                line_format = []
                text_from_images = []
                text_from_tables = []
                page_content = []
                # Инициализируем количество исследованных таблиц
                table_num = 0
                first_element = True
                table_extraction_flag = False
                page_tables = self.pdfplumber_obj.pages[page_num]
                # Находим количество таблиц на странице
                tables = page_tables.find_tables()

                # Находим все элементы
                page_elements = [(element.y1, element) for element in page._objs]
                # Сортируем все элементы по порядку нахождения на странице
                page_elements.sort(key=lambda a: a[0], reverse=True)

                # Находим элементы, составляющие страницу
                for i, component in enumerate(page_elements):
                    # Извлекаем положение верхнего края элемента в PDF
                    pos = component[0]
                    # Извлекаем элемент структуры страницы
                    element = component[1]

                    # Проверяем, является ли элемент текстовым
                    if isinstance(element, LTTextContainer):
                        # Проверяем, находится ли текст в таблице
                        if table_extraction_flag == False:
                            # Используем функцию извлечения текста и формата для каждого текстового элемента
                            line_text, format_per_line = self.text_extraction(element)
                            # Добавляем текст каждой строки к тексту страницы
                            page_text.append(line_text)
                            # Добавляем формат каждой строки, содержащей текст
                            line_format.append(format_per_line)
                            page_content.append(line_text)
                        else:
                            # Пропускаем текст, находящийся в таблице
                            pass

                    # Проверяем элементы на наличие изображений
                    if isinstance(element, LTFigure):
                        try:
                            # Вырезаем изображение из PDF
                            cropped_pdf_path = self.crop_image(element, pageObj)
                            # Преобразуем обрезанный pdf в изображение
                            image_path = self.convert_to_images(cropped_pdf_path)
                            # Извлекаем текст из изображения
                            image_text = self.image_to_text(image_path)
                            text_from_images.append(image_text)
                            page_content.append(image_text)
                            # Добавляем условное обозначение в списки текста и формата
                            page_text.append('image')
                            line_format.append('image')
                        finally:
                            # Удаляем временные файлы
                            if 'cropped_pdf_path' in locals() and os.path.exists(cropped_pdf_path):
                                os.remove(cropped_pdf_path)
                            if 'image_path' in locals() and os.path.exists(image_path):
                                os.remove(image_path)

                    # Проверяем элементы на наличие таблиц
                    if isinstance(element, LTRect):
                        # Если первый прямоугольный элемент
                        if first_element == True and (table_num + 1) <= len(tables):
                            # Находим ограничивающий прямоугольник таблицы
                            lower_side = page.bbox[3] - tables[table_num].bbox[3]
                            upper_side = element.y1
                            # Извлекаем информацию из таблицы
                            table = self.extract_table(page_num, table_num)
                            # Преобразуем информацию таблицы в формат структурированной строки
                            table_string = self.table_converter(table)
                            # Добавляем строку таблицы в список
                            text_from_tables.append(table_string)
                            page_content.append(table_string)
                            # Устанавливаем флаг True, чтобы избежать повторения содержимого
                            table_extraction_flag = True
                            # Преобразуем в другой элемент
                            first_element = False
                            # Добавляем условное обозначение в списки текста и формата
                            page_text.append('table')
                            line_format.append('table')
    
                        # Проверяем, извлекли ли мы уже таблицы из этой страницы
                        if lower_side and upper_side and element.y0 >= lower_side and element.y1 <= upper_side:
                            pass
                        elif i + 1 < len(page_elements) and not isinstance(page_elements[i + 1][1], LTRect):
                            table_extraction_flag = False
                            first_element = True
                            table_num += 1
    
                    # Проверяем, извлекли ли мы уже таблицы из этой страницы
                    if lower_side and upper_side and element.y0 >= lower_side and element.y1 <= upper_side:
                        pass
                    elif i + 1 < len(page_elements) and not isinstance(page_elements[i + 1][1], LTRect):
                        table_extraction_flag = False
                        first_element = True
                        table_num += 1

                # Создаём ключ для словаря
                dctkey = 'Page_' + str(page_num)
                # Добавляем список списков как значение ключа страницы
                self.text_per_page[dctkey] = [page_text, line_format, text_from_images, text_from_tables, page_content]

        except Exception as e:
            print(f"Ошибка при обработке страницы {page_num}: {e}")
        finally:
            print()
            self.pdfFileObj.close()
            self.pdfplumber_obj.close()

        return ''.join([''.join(self.text_per_page[f'Page_{i}'][4]) for i in range(len(self.text_per_page))])

    def text_extraction(self, _element):
        """Извлечение текста из вложенного текстового элемента."""

        line_text = _element.get_text()

        # Находим форматы текста
        # Инициализируем список со всеми форматами, встречающимися в строке текста
        line_formats = []

        for text_line in _element:
            if isinstance(text_line, LTTextContainer):
                # Итеративно обходим каждый символ в строке текста
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Добавляем к символу название шрифта
                        line_formats.append(character.fontname)
                        # Добавляем к символу размер шрифта
                        line_formats.append(character.size)

        # Находим уникальные размеры и названия шрифтов в строке
        format_per_line = list(set(line_formats))

        # Возвращаем кортеж с текстом в каждой строке вместе с его форматом
        return line_text, format_per_line

    def crop_image(self, _element, page_obj):
        """Вырезка изображения из PDF."""

        # Получаем координаты для вырезания изображения из PDF
        [image_left, image_top, image_right, image_bottom] = [_element.x0, _element.y0, _element.x1, _element.y1]

        # Обрезаем страницу по координатам (left, bottom, right, top)
        page_obj.mediabox.lower_left = (image_left, image_bottom)
        page_obj.mediabox.upper_right = (image_right, image_top)

        # Сохраняем обрезанную страницу в новый PDF
        cropped_pdf_writer = PyPDF2.PdfWriter()
        cropped_pdf_writer.add_page(page_obj)

        # Создаем временный файл для обрезанного PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as cropped_pdf_file:
            cropped_pdf_writer.write(cropped_pdf_file)

            return cropped_pdf_file.name

    def convert_to_images(self, input_file):
        """Конвертация изображения."""

        images = convert_from_path(input_file)
        image = images[0]

        # Создаем временный файл для изображения
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as output_file:
            image.save(output_file, "PNG")

            return output_file.name

    def image_to_text(self, image_path):
        """Приведение изображение к тексту."""

        # Считываем изображение
        img = Image.open(image_path)
        # Извлекаем текст из изображения
        text = pytesseract.image_to_string(img, lang='rus')

        return text

    def extract_table(self, page_num, table_num):
        """Извлечение таблиц."""

        # Используем уже открытый объект pdfplumber
        table_page = self.pdfplumber_obj.pages[page_num]
        # Извлекаем соответствующую таблицу
        table = table_page.extract_tables()[table_num]

        return table

    def table_converter(self, table):
        """Конвертация таблиц."""

        table_string = ''

        # Итеративно обходим каждую строку в таблице
        for row_num in range(len(table)):
            row = table[row_num]
            # Удаляем разрыв строки из текста с переносом
            cleaned_row = [
                item.replace('\n', ' ') if item is not None and '\n' in item
                else 'None' if item is None
                else item
                for item in row
            ]
            # Преобразуем таблицу в строку
            table_string += ('|' + '|'.join(cleaned_row) + '|' + '\n')

        # Удаляем последний разрыв строки
        table_string = table_string[:-1]

        return table_string

