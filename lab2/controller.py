from models import StudentModel, Student
from view.main_window import MainWindow
from view.dialogs import AddStudentDialog, SearchDialog, DeleteDialog
from PySide6.QtWidgets import QTableWidgetItem, QFileDialog, QMessageBox


class PaginationManager:
    """Универсальный класс для управления любой таблицей с пагинацией"""

    def __init__(self, table, btn_first, btn_prev, btn_next, btn_last,
                 page_label, records_per_page_spin, total_records_label):
        self.table = table
        self.btn_first = btn_first
        self.btn_prev = btn_prev
        self.btn_next = btn_next
        self.btn_last = btn_last
        self.page_label = page_label
        self.records_per_page_spin = records_per_page_spin
        self.total_records_label = total_records_label

        self.data = []
        self.current_page = 1

        # Подключаем кнопки к методам самого менеджера
        self.btn_first.clicked.connect(self.first_page)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_last.clicked.connect(self.last_page)
        self.records_per_page_spin.valueChanged.connect(self.change_page_size)

    def set_data(self, data):
        """Загрузка новых данных и сброс на первую страницу"""
        self.data = data
        self.current_page = 1
        self.update_view()

    def update_view(self):
        """Отрисовка текущей страницы в таблице"""
        total = len(self.data)
        rpp = self.records_per_page_spin.value()
        max_page = max(1, (total + rpp - 1) // rpp)

        if self.current_page > max_page:
            self.current_page = max_page

        start = (self.current_page - 1) * rpp
        end = start + rpp
        page_data = self.data[start:end]

        self.table.setRowCount(0)
        for student in page_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            full_name = f"{student.surname} {student.name} {student.patronymic}"
            self.table.setItem(row, 0, QTableWidgetItem(full_name))
            self.table.setItem(row, 1, QTableWidgetItem(student.group))
            self.table.setItem(row, 2, QTableWidgetItem(str(student.sick_skip)))
            self.table.setItem(row, 3, QTableWidgetItem(str(student.other_skip)))
            self.table.setItem(row, 4, QTableWidgetItem(str(student.unjustified_skip)))
            self.table.setItem(row, 5, QTableWidgetItem(str(student.all_skips)))

        self.page_label.setText(f"Страница {self.current_page} из {max_page}")
        self.total_records_label.setText(f"Всего записей: {total}")

    # Логика переключения страниц
    def first_page(self):
        self.current_page = 1
        self.update_view()

    def prev_page(self):
        self.current_page = max(1, self.current_page - 1)
        self.update_view()

    def next_page(self):
        rpp = self.records_per_page_spin.value()
        max_page = max(1, (len(self.data) + rpp - 1) // rpp)
        if self.current_page < max_page:
            self.current_page += 1
            self.update_view()

    def last_page(self):
        rpp = self.records_per_page_spin.value()
        self.current_page = max(1, (len(self.data) + rpp - 1) // rpp)
        self.update_view()

    def change_page_size(self):
        self.current_page = 1
        self.update_view()


class Controller:
    def __init__(self, model: StudentModel, view: MainWindow):
        self.model = model
        self.view = view

        # Создаем менеджер пагинации для главного окна
        self.main_pagination = PaginationManager(
            self.view.table, self.view.btn_first, self.view.btn_prev,
            self.view.btn_next, self.view.btn_last, self.view.page_label,
            self.view.records_per_page_spin, self.view.total_records_label
        )

        self._connect_signals()
        self.update_main_table()

    def _connect_signals(self):
        self.view.open_action.triggered.connect(self.open_file)
        self.view.save_action.triggered.connect(self.save_file)
        self.view.add_action.triggered.connect(self.on_add_clicked)
        self.view.search_action.triggered.connect(self.on_search_clicked)
        self.view.delete_action.triggered.connect(self.on_delete_clicked)

    def update_main_table(self):
        # Просто передаем всех студентов в менеджер
        self.main_pagination.set_data(self.model.get_all_students())

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self.view, "Открыть базу студентов", "", "XML Files (*.xml)")
        if file_path:
            try:
                self.model.load_from_xml(file_path)
                self.update_main_table()
                self.view.statusBar().showMessage(f"Загружено из {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Не удалось прочитать файл: {e}")

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self.view, "Сохранить базу студентов", "", "XML Files (*.xml)")
        if file_path:
            if not file_path.endswith('.xml'):
                file_path += '.xml'
            try:
                self.model.save_to_xml(file_path)
                self.view.statusBar().showMessage(f"Данные сохранены в {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Не удалось сохранить файл: {e}")

    def on_add_clicked(self):
        dialog = AddStudentDialog(self.view)
        if dialog.exec():
            data = dialog.get_data()
            new_student = Student(
                name=data['name'], surname=data['surname'], patronymic=data['patronymic'],
                group=data['group'], sick_skip=data['sick_skip'],
                other_skip=data['other_skip'],
                unjustified_skip=data['non_legitimate_skip']
            )
            self.model.add_student(new_student)
            self.update_main_table()
            self.view.statusBar().showMessage("Студент добавлен в базу", 3000)

    def on_search_clicked(self):
        dialog = SearchDialog(self.view)

        # Создаем второй независимый менеджер пагинации для диалогового окна поиска
        search_pagination = PaginationManager(
            dialog.result_table, dialog.btn_first, dialog.btn_prev,
            dialog.btn_next, dialog.btn_last, dialog.page_label,
            dialog.records_per_page_spin, dialog.total_records_label
        )

        def perform_search():
            c_type = dialog.criteria_combo.currentIndex() + 1
            kwargs = {
                "surname": dialog.surname_input.text(),
                "group": dialog.group_input.text(),
                "skip_type": dialog.skip_type_combo.currentData(),
                "min_val": dialog.min_spin.value(),
                "max_val": dialog.max_spin.value()
            }
            # Ищем студентов и передаем результат в менеджер пагинации поиска
            results = self.model.search_students(c_type, **kwargs)
            search_pagination.set_data(results)

        dialog.search_btn.clicked.connect(perform_search)
        dialog.exec()

    def on_delete_clicked(self):
        dialog = DeleteDialog(self.view)
        if dialog.exec():
            c_type = dialog.criteria_combo.currentIndex() + 1
            kwargs = {
                "surname": dialog.surname_input.text(),
                "group": dialog.group_input.text(),
                "skip_type": dialog.skip_type_combo.currentData(),
                "min_val": dialog.min_spin.value(),
                "max_val": dialog.max_spin.value()
            }

            deleted_count = self.model.delete_student(c_type, **kwargs)

            if deleted_count > 0:
                QMessageBox.information(self.view, "Успех", f"Успешно удалено записей: {deleted_count}")
                self.update_main_table()
            else:
                QMessageBox.warning(self.view, "Результат", "Записи, удовлетворяющие условиям, не найдены.")