from PySide6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QWidget, QVBoxLayout, QTableWidget, QHeaderView, \
    QHBoxLayout, QPushButton, QLabel, QSpinBox
from PySide6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учёт пропусков студентов")
        self.resize(1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.setup_table()
        self.setup_pagination()

        self.create_actions()
        self.create_menus()
        self.create_toolbar()

    def setup_table(self):
        """Настройка внешнего вида таблицы"""
        self.table = QTableWidget()

        columns = [
            "ФИО ",
            "Группа",
            "По болезни",
            "По др. причинам",
            "Без уважит.",
            "Итого"
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.layout.addWidget(self.table)

    def setup_pagination(self):
        """Создаем ряд кнопок под таблицей"""
        pagination_layout = QHBoxLayout()

        self.btn_first = QPushButton("<<")
        self.btn_prev = QPushButton("<")
        self.page_label = QLabel("Страница 1 из 1")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">>")

        self.records_per_page_label = QLabel("Записей на стр:")
        self.records_per_page_spin = QSpinBox()
        self.records_per_page_spin.setRange(1, 100)
        self.records_per_page_spin.setValue(10)  # По умолчанию 10

        self.total_records_label = QLabel("Всего записей: 0")

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

        self.layout.addLayout(pagination_layout)

    def create_actions(self):
        """Здесь мы просто создаем список команд"""
        self.open_action = QAction("Открыть", self)
        self.save_action = QAction("Сохранить", self)
        self.exit_action = QAction("Выход", self)

        self.add_action = QAction("Добавить", self)
        self.search_action = QAction("Поиск", self)
        self.delete_action = QAction("Удалить", self)

        self.exit_action.triggered.connect(self.close)

    def create_menus(self):
        """Добавляем команды в верхнюю полоску меню"""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&Файл")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("&Студенты")
        edit_menu.addAction(self.add_action)
        edit_menu.addAction(self.search_action)
        edit_menu.addAction(self.delete_action)

    def create_toolbar(self):
        """Добавляем те же команды на панель иконок под меню"""
        toolbar = QToolBar("Главная панель")
        self.addToolBar(toolbar)

        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.search_action)
        toolbar.addAction(self.delete_action)

    def on_add_clicked(self):
        print("Нажата кнопка Добавить!")
        self.statusBar().showMessage("Открываем окно добавления...", 3000)