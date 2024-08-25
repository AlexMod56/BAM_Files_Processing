from typing import Dict
import os

import flet
from flet import (
    Column,
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    FilePickerUploadEvent,
    Page,
    ProgressRing,
    Ref,
    Row,
    Text,
    icons,
    MainAxisAlignment,
    CrossAxisAlignment,
    ButtonStyle,
    RoundedRectangleBorder,
)

# Проверка имен файлов
def file_info_check(bam_file, bai_file):

    # Проверка совпадения имен файлов
    if not os.path.basename(bam_file).startswith(os.path.basename(bai_file).replace('.bai', '')):
        return "Имена файлов BAM и BAI должны быть одинаковыми"

    # Получение времени создания файлов
    bam_creation_time = os.path.getmtime(bam_file)
    bai_creation_time = os.path.getmtime(bai_file)

    # Проверка времени создания файлов
    if bai_creation_time < bam_creation_time:
        return "BAI файл создан раньше, чем BAM файл"

    # Возвращаем размер файла BAM
    return os.path.getsize(bam_file)

# Функция для подсчета количества строк
def count_lines_in_file(file_path):
    with open(file_path, 'r') as file:
        return sum(1 for _ in file)

def main(page: Page):

    # Название и ориентация в окне
    page.title = "BAM file processing tool"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    prog_bars: Dict[str, ProgressRing] = {}
    files = Ref[Column]()
    upload_button = Ref[ElevatedButton]()

    # Поиск файлов в системе для анализа
    def file_picker_result(e: FilePickerResultEvent):
        upload_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(value=0, bgcolor="#EEEEEE", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(Row([prog, Text(f.name)], alignment=MainAxisAlignment.CENTER))
        page.update()


    # Прогресс при загрузке
    def on_upload_progress(e: FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = FilePicker(on_result=file_picker_result, on_upload=on_upload_progress)
    text_field = Text()
    text_field_bed = Text()

    # Проверка загруженных файлов
    def on_file_upload(file_picker, page):

        files_upl = file_picker.result.files

        bam_file = next((f for f in files_upl if f.name.endswith('.bam')), None)
        bai_file = next((f for f in files_upl if f.name.endswith('.bai')), None)
        fasta_file = next((f for f in files_upl if f.name.endswith('.fa')), None)
        fai_file = next((f for f in files_upl if f.name.endswith('.fai')), None)
        bed_file = next((f for f in files_upl if f.name.endswith('.bed')), None)

        if not bam_file or not bai_file or not fasta_file or not fai_file:
            text_field.value = "Необходимо выбрать все файлы форматов: BAM, BAI, FASTA и FAI"
            text_field.color = "red"
            page.update()
            return

        if not bed_file:
            text_field_bed.value = "Можно дополнительно загрузить BED файл (опционально)"
            text_field_bed.color = "black"
            page.update()
        else:
            bed_file_path = bed_file.path
            bed_line_count = count_lines_in_file(bed_file_path)
            text_field_bed.value = f"Количество анализируемых регионов: {bed_line_count}"
            text_field_bed.color = "black"
            page.update()

        bam_file_path = bam_file.path
        bai_file_path = bai_file.path
        #fasta_file_path = fasta_file.path
        #fai_file_path = fai_file.path

        # Проверка файлов и получение размера
        result = file_info_check(bam_file_path, bai_file_path)

        if isinstance(result, str):  # Если результат — строка, это сообщение об ошибке
            text_field.value = result
            text_field.color = "red"
        else:
            text_field.value = f"Размер BAM файла: {result / (1024 * 1024):.2f} МБ"
            text_field.color = "black"

        page.update()

    # Очистка полей
    def clear_all_fields(e):

        # Очистка текстовых полей
        text_field.value = ""
        text_field.color = "black"
        text_field_bed.value = ""
        text_field_bed.color = "black"

        # Очистка списка файлов
        files.current.controls.clear()
        prog_bars.clear()

        # Разблокировка кнопки загрузки
        upload_button.current.disabled = True

        # Обновление страницы
        page.update()


    # Создание кнопок и их стилизация
    select_files_button = ElevatedButton(
        "Выбрать файлы",
        icon=icons.FOLDER_OPEN,
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
        width=250,
        height=75,
        style=ButtonStyle(shape=RoundedRectangleBorder(radius=5)),
    )

    upload_button_new = ElevatedButton(
        "Подтвердить загрузку",
        ref=upload_button,
        icon=icons.UPLOAD,
        on_click=lambda e: on_file_upload(file_picker, page),
        disabled=True,
        width=250,
        height=75,
        style=ButtonStyle(shape=RoundedRectangleBorder(radius=5)),
    )

    clear_button = ElevatedButton(
        "Очистить",
        icon=icons.CLEAR,
        on_click=clear_all_fields,
        width=250,
        height=75,
        style=ButtonStyle(shape=RoundedRectangleBorder(radius=5)),
    )

    page.overlay.append(file_picker)

    # Выравнивание всех элементов по центру
    page.add(
        Column(
            controls=[
                select_files_button,
                Column(ref=files),
                upload_button_new,
                clear_button,
                text_field,
                text_field_bed
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )

flet.app(target=main)