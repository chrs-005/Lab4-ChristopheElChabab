import sqlite3
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from part4_database import SchoolDatabase


class SchoolManagementQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Management System")
        self.resize(1100, 720)
        self.database = SchoolDatabase()
        self.selected_type = None
        self.selected_id = None
        self._build_interface()
        self.refresh()

    def _build_interface(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        self.setCentralWidget(central)

        tabs = QTabWidget()
        tabs.addTab(self._student_tab(), "Student")
        tabs.addTab(self._instructor_tab(), "Instructor")
        tabs.addTab(self._course_tab(), "Course")
        layout.addWidget(tabs)

        assignment_row = QHBoxLayout()
        assignment_row.addWidget(QLabel("Student"))
        self.registration_student = QComboBox()
        assignment_row.addWidget(self.registration_student)
        assignment_row.addWidget(QLabel("Course"))
        self.registration_course = QComboBox()
        assignment_row.addWidget(self.registration_course)
        register_button = QPushButton("Register Student")
        register_button.clicked.connect(self.register_student)
        assignment_row.addWidget(register_button)
        assignment_row.addSpacing(20)
        assignment_row.addWidget(QLabel("Instructor"))
        self.assignment_instructor = QComboBox()
        assignment_row.addWidget(self.assignment_instructor)
        assignment_row.addWidget(QLabel("Course"))
        self.assignment_course = QComboBox()
        assignment_row.addWidget(self.assignment_course)
        assign_button = QPushButton("Assign Instructor")
        assign_button.clicked.connect(self.assign_instructor)
        assignment_row.addWidget(assign_button)
        layout.addLayout(assignment_row)

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search"))
        self.search_text = QLineEdit()
        self.search_text.setPlaceholderText("Name, ID, or course")
        search_row.addWidget(self.search_text)
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        search_row.addWidget(search_button)
        show_all_button = QPushButton("Show All")
        show_all_button.clicked.connect(self.refresh)
        search_row.addWidget(show_all_button)
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected)
        search_row.addWidget(delete_button)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_database)
        search_row.addWidget(save_button)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_database)
        search_row.addWidget(load_button)
        export_button = QPushButton("Export CSV")
        export_button.clicked.connect(self.export_csv)
        search_row.addWidget(export_button)
        layout.addLayout(search_row)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Type", "ID", "Name/Course", "Age", "Email/Details"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

    def _student_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.student_id = QLineEdit()
        self.student_name = QLineEdit()
        self.student_age = QLineEdit()
        self.student_email = QLineEdit()
        form.addRow("Student ID", self.student_id)
        form.addRow("Name", self.student_name)
        form.addRow("Age", self.student_age)
        form.addRow("Email", self.student_email)
        buttons = QHBoxLayout()
        add_button = QPushButton("Add Student")
        add_button.clicked.connect(self.add_student)
        update_button = QPushButton("Update Student")
        update_button.clicked.connect(self.update_student)
        buttons.addWidget(add_button)
        buttons.addWidget(update_button)
        form.addRow(buttons)
        return widget

    def _instructor_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.instructor_id = QLineEdit()
        self.instructor_name = QLineEdit()
        self.instructor_age = QLineEdit()
        self.instructor_email = QLineEdit()
        form.addRow("Instructor ID", self.instructor_id)
        form.addRow("Name", self.instructor_name)
        form.addRow("Age", self.instructor_age)
        form.addRow("Email", self.instructor_email)
        buttons = QHBoxLayout()
        add_button = QPushButton("Add Instructor")
        add_button.clicked.connect(self.add_instructor)
        update_button = QPushButton("Update Instructor")
        update_button.clicked.connect(self.update_instructor)
        buttons.addWidget(add_button)
        buttons.addWidget(update_button)
        form.addRow(buttons)
        return widget

    def _course_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.course_id = QLineEdit()
        self.course_name = QLineEdit()
        self.course_instructor = QComboBox()
        form.addRow("Course ID", self.course_id)
        form.addRow("Course Name", self.course_name)
        form.addRow("Instructor", self.course_instructor)
        buttons = QHBoxLayout()
        add_button = QPushButton("Add Course")
        add_button.clicked.connect(self.add_course)
        update_button = QPushButton("Update Course")
        update_button.clicked.connect(self.update_course)
        buttons.addWidget(add_button)
        buttons.addWidget(update_button)
        form.addRow(buttons)
        return widget

    def _perform(self, operation, success_message):
        try:
            operation()
            self.refresh()
            QMessageBox.information(self, "Success", success_message)
        except (ValueError, sqlite3.Error) as error:
            QMessageBox.critical(self, "Error", str(error))

    def add_student(self):
        self._perform(
            lambda: self.database.add_student(self.student_id.text(), self.student_name.text(), self.student_age.text(), self.student_email.text()),
            "Student added.",
        )

    def add_instructor(self):
        self._perform(
            lambda: self.database.add_instructor(self.instructor_id.text(), self.instructor_name.text(), self.instructor_age.text(), self.instructor_email.text()),
            "Instructor added.",
        )

    def add_course(self):
        self._perform(
            lambda: self.database.add_course(self.course_id.text(), self.course_name.text(), self.course_instructor.currentText()),
            "Course added.",
        )

    def update_student(self):
        original_id = self.selected_id if self.selected_type == "Student" else self.student_id.text()
        self._perform(
            lambda: self.database.update_student(original_id, self.student_id.text(), self.student_name.text(), self.student_age.text(), self.student_email.text()),
            "Student updated.",
        )

    def update_instructor(self):
        original_id = self.selected_id if self.selected_type == "Instructor" else self.instructor_id.text()
        self._perform(
            lambda: self.database.update_instructor(original_id, self.instructor_id.text(), self.instructor_name.text(), self.instructor_age.text(), self.instructor_email.text()),
            "Instructor updated.",
        )

    def update_course(self):
        original_id = self.selected_id if self.selected_type == "Course" else self.course_id.text()
        self._perform(
            lambda: self.database.update_course(original_id, self.course_id.text(), self.course_name.text(), self.course_instructor.currentText()),
            "Course updated.",
        )

    def register_student(self):
        self._perform(
            lambda: self.database.enroll_student(self.registration_student.currentText(), self.registration_course.currentText()),
            "Student registered in course.",
        )

    def assign_instructor(self):
        self._perform(
            lambda: self.database.assign_instructor(self.assignment_instructor.currentText(), self.assignment_course.currentText()),
            "Instructor assigned to course.",
        )

    def delete_selected(self):
        if not self.selected_type:
            QMessageBox.critical(self, "Error", "Select a record first.")
            return
        self._perform(lambda: self.database.delete_record(self.selected_type, self.selected_id), "Record deleted.")

    def search(self):
        self._fill_table(self.database.search_records(self.search_text.text()))

    def refresh(self):
        students = [row["student_id"] for row in self.database.list_students()]
        instructors = [row["instructor_id"] for row in self.database.list_instructors()]
        courses = [row["course_id"] for row in self.database.list_courses()]
        self._set_combo(self.registration_student, students)
        self._set_combo(self.registration_course, courses)
        self._set_combo(self.assignment_instructor, instructors)
        self._set_combo(self.assignment_course, courses)
        self._set_combo(self.course_instructor, [""] + instructors)
        self._fill_table(self.database.all_records())

    @staticmethod
    def _set_combo(combo, values):
        current = combo.currentText()
        combo.clear()
        combo.addItems(values)
        index = combo.findText(current)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _fill_table(self, records):
        self.table.setRowCount(len(records))
        for row_index, record in enumerate(records):
            for column_index, value in enumerate(record):
                self.table.setItem(row_index, column_index, QTableWidgetItem(str(value)))

    def _on_select(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row_index = selected[0].row()
        self.selected_type = self.table.item(row_index, 0).text()
        self.selected_id = self.table.item(row_index, 1).text()
        if self.selected_type == "Student":
            row = self.database.connection.execute("SELECT * FROM students WHERE student_id=?", (self.selected_id,)).fetchone()
            self.student_id.setText(row["student_id"])
            self.student_name.setText(row["name"])
            self.student_age.setText(str(row["age"]))
            self.student_email.setText(row["email"])
        elif self.selected_type == "Instructor":
            row = self.database.connection.execute("SELECT * FROM instructors WHERE instructor_id=?", (self.selected_id,)).fetchone()
            self.instructor_id.setText(row["instructor_id"])
            self.instructor_name.setText(row["name"])
            self.instructor_age.setText(str(row["age"]))
            self.instructor_email.setText(row["email"])
        else:
            row = self.database.connection.execute("SELECT * FROM courses WHERE course_id=?", (self.selected_id,)).fetchone()
            self.course_id.setText(row["course_id"])
            self.course_name.setText(row["course_name"])
            index = self.course_instructor.findText(row["instructor_id"] or "")
            self.course_instructor.setCurrentIndex(max(index, 0))

    def save_database(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Database", "", "SQLite Database (*.db)")
        if filename:
            self._perform(lambda: self.database.backup(filename), "Database saved.")

    def load_database(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Database", "", "SQLite Database (*.db)")
        if filename:
            self._perform(lambda: self.database.restore(filename), "Database loaded.")

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV File (*.csv)")
        if filename:
            self._perform(lambda: self.database.export_csv(filename), "Records exported.")

    def closeEvent(self, event):
        self.database.close()
        event.accept()


if __name__ == "__main__":
    application = QApplication(sys.argv)
    window = SchoolManagementQt()
    window.show()
    sys.exit(application.exec_())
