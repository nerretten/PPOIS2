import xml.sax as sax
from xml.dom import minidom
from typing import List


class Student:
    def __init__(self, name: str, surname: str, patronymic: str,
                 group: str, sick_skip: int, other_skip: int,
                 unjustified_skip: int):
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.group = group
        self.sick_skip = sick_skip
        self.other_skip = other_skip
        self.unjustified_skip = unjustified_skip

    @property
    def all_skips(self) -> int:
        return self.sick_skip + self.other_skip + self.unjustified_skip


class StudentSaxHandler(sax.ContentHandler):
    def __init__(self):
        self.temp_students: List[Student] = []

    def startElement(self, name, attrs):
        if name == 'student':
            student = Student(
                name=attrs['name'],
                surname=attrs['surname'],
                patronymic=attrs['patronymic'],
                group=attrs['group'],
                sick_skip=int(attrs['sick_skip']),
                other_skip=int(attrs['other_skip']),
                unjustified_skip=int(attrs['unjustified_skip'])
            )
            self.temp_students.append(student)


class StudentModel:
    def __init__(self):
        self.students: List[Student] = []

    def add_student(self, student: Student):
        self.students.append(student)

    def get_all_students(self) -> List[Student]:
        return self.students

    def save_to_xml(self, filename: str):
        doc = minidom.Document()
        root = doc.createElement('students')
        doc.appendChild(root)
        for student in self.students:
            student_node = doc.createElement('student')
            student_node.setAttribute('name', student.name)
            student_node.setAttribute('surname', student.surname)
            student_node.setAttribute('patronymic', student.patronymic)
            student_node.setAttribute('group', student.group)
            student_node.setAttribute('sick_skip', str(student.sick_skip))
            student_node.setAttribute('other_skip', str(student.other_skip))
            student_node.setAttribute('unjustified_skip', str(student.unjustified_skip))

            root.appendChild(student_node)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(doc.toprettyxml(indent='  '))

    def load_from_xml(self, filename: str):
        handler = StudentSaxHandler()
        parser = sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(filename)
        self.students = handler.temp_students

    def search_students(self, criteria_type: int, **kwargs) -> List[Student]:
        results = []

        # Безопасно получаем строки, убираем лишние пробелы и приводим к нижнему регистру
        surname_query = kwargs.get('surname', '').strip().lower()
        group_query = kwargs.get('group', '').strip()
        skip_attr = kwargs.get('skip_type')

        for s in self.students:
            match = True  # Изначально считаем, что студент подходит, и пытаемся его "отсеять"

            if criteria_type == 1:
                # Если оба поля оставили пустыми — ничего не ищем (чтобы не выводить всю базу)
                if not group_query and not surname_query:
                    match = False
                else:
                    # Если поле Группа заполнено, но не совпадает — отсеиваем
                    if group_query and s.group != group_query:
                        match = False
                    # Если поле Фамилия заполнено, но не совпадает — отсеиваем
                    if surname_query and s.surname.lower() != surname_query:
                        match = False

            elif criteria_type == 2:
                if surname_query and s.surname.lower() != surname_query:
                    match = False

                # Поиск по виду пропуска означает, что таких пропусков должно быть больше 0
                val = getattr(s, skip_attr, 0)
                if val <= 0:
                    match = False

            elif criteria_type == 3:
                if surname_query and s.surname.lower() != surname_query:
                    match = False

                val = getattr(s, skip_attr, 0)
                min_val = kwargs.get('min_val', 0)
                max_val = kwargs.get('max_val', 100)

                # Если количество пропусков не попадает в диапазон — отсеиваем
                if not (min_val <= val <= max_val):
                    match = False

            # Если студент прошел все фильтры, добавляем его в результат
            if match:
                results.append(s)

        return results

    def delete_student(self, criteria_type: int, **kwargs):
        initial_count = len(self.students)
        # Так как удаление использует тот же поиск, исправление поиска автоматически чинит и удаление!
        to_delete = self.search_students(criteria_type, **kwargs)

        # Перезаписываем список студентов, оставляя только тех, кого нет в to_delete
        self.students = [s for s in self.students if s not in to_delete]

        return initial_count - len(self.students)