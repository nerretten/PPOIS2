from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox, QMessageBox, \
    QTableWidget, QHeaderView, QHBoxLayout, QPushButton, QComboBox, QLabel, QWidget


class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить студента")

        main_layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.surname_input = QLineEdit()
        self.name_input = QLineEdit()
        self.patronymic_input = QLineEdit()
        self.group_input = QLineEdit()
        self.sick_spin = QSpinBox()
        self.other_spin = QSpinBox()
        self.unjustified_spin = QSpinBox()

        form_layout.addRow("Фамилия:", self.surname_input)
        form_layout.addRow("Имя:", self.name_input)
        form_layout.addRow("Отчество:", self.patronymic_input)
        form_layout.addRow("Группа:", self.group_input)
        form_layout.addRow("По болезни:", self.sick_spin)
        form_layout.addRow("Другие:", self.other_spin)
        form_layout.addRow("Без уважит.:", self.unjustified_spin)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText("ОК")
        self.buttons.button(QDialogButtonBox.Cancel).setText("Отмена")

        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.buttons)

        self.setLayout(main_layout)

    def validate_and_accept(self):
        if not self.surname_input.text().strip() or not self.name_input.text().strip() or not self.group_input.text():
            QMessageBox.warning(self, "Ошибка", "Фамилия, Имя и номер группы обязательны!")
            return
        self.accept()

    def get_data(self):
        """Возвращает словарь с введенными данными"""
        return {
            "surname": self.surname_input.text(),
            "name": self.name_input.text(),
            "patronymic": self.patronymic_input.text(),
            "group": self.group_input.text(),
            "sick_skip": self.sick_spin.value(),
            "other_skip": self.other_spin.value(),
            "non_legitimate_skip": self.unjustified_spin.value()
        }


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск студентов")
        self.resize(800, 500)
        self.main_layout = QVBoxLayout(self)

        self.criteria_combo = QComboBox()
        self.criteria_combo.addItems([
            "1. По номеру группы или фамилии",
            "2. По фамилии или виду пропуска",
            "3. По фамилии или диапазону пропусков"
        ])
        self.main_layout.addWidget(self.criteria_combo)

        self.form = QFormLayout()
        self.surname_input = QLineEdit()
        self.group_input = QLineEdit()
        self.skip_type_combo = QComboBox()
        self.skip_type_combo.addItem("По болезни", "sick_skip")
        self.skip_type_combo.addItem("По другим причинам", "other_skip")
        self.skip_type_combo.addItem("Без уважительной причины", "unjustified_skip")

        self.min_spin = QSpinBox()
        self.max_spin = QSpinBox()
        self.max_spin.setValue(100)

        # Оборачиваем элементы диапазона в один виджет для удобного скрытия
        self.range_widget = QWidget()
        range_layout = QHBoxLayout(self.range_widget)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.addWidget(self.min_spin)
        range_layout.addWidget(self.max_spin)

        self.form.addRow("Фамилия:", self.surname_input)
        self.form.addRow("Группа:", self.group_input)
        self.form.addRow("Тип пропуска:", self.skip_type_combo)
        self.form.addRow("Диапазон (от/до):", self.range_widget)
        self.main_layout.addLayout(self.form)

        self.search_btn = QPushButton("Найти")
        self.main_layout.addWidget(self.search_btn)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(["ФИО", "Группа", "Бол.", "Др.", "Без.", "Итого"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.result_table)

        pagination_layout = QHBoxLayout()
        self.btn_first = QPushButton("<<")
        self.btn_prev = QPushButton("<")
        self.page_label = QLabel("Страница 1 из 1")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">>")
        self.records_per_page_label = QLabel("Записей на стр:")
        self.records_per_page_spin = QSpinBox()
        self.records_per_page_spin.setRange(1, 100)
        self.records_per_page_spin.setValue(10)
        self.total_records_label = QLabel("Всего найдено: 0")

        pagination_layout.addWidget(self.btn_first)
        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.btn_next)
        pagination_layout.addWidget(self.btn_last)
        pagination_layout.addSpacing(20)
        pagination_layout.addWidget(self.records_per_page_label)
        pagination_layout.addWidget(self.records_per_page_spin)
        pagination_layout.addWidget(self.total_records_label)

        self.main_layout.addLayout(pagination_layout)
        self.setLayout(self.main_layout)

        # Подключаем логику скрытия полей
        self.criteria_combo.currentIndexChanged.connect(self.update_fields_visibility)
        self.update_fields_visibility()  # Вызываем при старте, чтобы скрыть лишнее

    def update_fields_visibility(self):
        """Скрывает/показывает поля в зависимости от выбранного критерия"""
        idx = self.criteria_combo.currentIndex()
        self._set_row_visible(self.group_input, idx == 0)
        self._set_row_visible(self.skip_type_combo, idx in (1, 2))
        self._set_row_visible(self.range_widget, idx == 2)

    def _set_row_visible(self, widget, visible):
        """Безопасное скрытие виджета и его подписи (Label) в QFormLayout"""
        widget.setVisible(visible)
        label = self.form.labelForField(widget)
        if label:
            label.setVisible(visible)


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление студентов")
        self.resize(400, 300)
        self.main_layout = QVBoxLayout(self)

        self.criteria_combo = QComboBox()
        self.criteria_combo.addItems([
            "1. По номеру группы или фамилии",
            "2. По фамилии или виду пропуска",
            "3. По фамилии или диапазону пропусков"
        ])
        self.main_layout.addWidget(self.criteria_combo)

        self.form = QFormLayout()
        self.surname_input = QLineEdit()
        self.group_input = QLineEdit()
        self.skip_type_combo = QComboBox()
        self.skip_type_combo.addItem("По болезни", "sick_skip")
        self.skip_type_combo.addItem("По другим причинам", "other_skip")
        self.skip_type_combo.addItem("Без уважительной причины", "unjustified_skip")

        self.min_spin = QSpinBox()
        self.max_spin = QSpinBox()
        self.max_spin.setValue(100)

        self.range_widget = QWidget()
        range_layout = QHBoxLayout(self.range_widget)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.addWidget(self.min_spin)
        range_layout.addWidget(self.max_spin)

        self.form.addRow("Фамилия:", self.surname_input)
        self.form.addRow("Группа:", self.group_input)
        self.form.addRow("Тип пропуска:", self.skip_type_combo)
        self.form.addRow("Диапазон (от/до):", self.range_widget)
        self.main_layout.addLayout(self.form)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setStyleSheet("background-color: #ffcccc;")
        self.delete_btn.clicked.connect(self.accept)
        self.main_layout.addWidget(self.delete_btn)

        self.criteria_combo.currentIndexChanged.connect(self.update_fields_visibility)
        self.update_fields_visibility()

    def update_fields_visibility(self):
        idx = self.criteria_combo.currentIndex()
        self._set_row_visible(self.group_input, idx == 0)
        self._set_row_visible(self.skip_type_combo, idx in (1, 2))
        self._set_row_visible(self.range_widget, idx == 2)

    def _set_row_visible(self, widget, visible):
        widget.setVisible(visible)
        label = self.form.labelForField(widget)
        if label:
            label.setVisible(visible)