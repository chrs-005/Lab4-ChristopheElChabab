import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from part4_database import SchoolDatabase


class SchoolManagementTk:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("1050x720")
        self.database = SchoolDatabase()
        self.selected_type = None
        self.selected_id = None
        self._build_interface()
        self.refresh()

    def _build_interface(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="x", padx=10, pady=10)

        self.student_frame = ttk.Frame(notebook, padding=10)
        self.instructor_frame = ttk.Frame(notebook, padding=10)
        self.course_frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.student_frame, text="Student")
        notebook.add(self.instructor_frame, text="Instructor")
        notebook.add(self.course_frame, text="Course")

        self.student_id = tk.StringVar()
        self.student_name = tk.StringVar()
        self.student_age = tk.StringVar()
        self.student_email = tk.StringVar()
        self._entry(self.student_frame, "Student ID", self.student_id, 0)
        self._entry(self.student_frame, "Name", self.student_name, 1)
        self._entry(self.student_frame, "Age", self.student_age, 2)
        self._entry(self.student_frame, "Email", self.student_email, 3)
        ttk.Button(self.student_frame, text="Add Student", command=self.add_student).grid(row=4, column=0, padx=5, pady=8)
        ttk.Button(self.student_frame, text="Update Student", command=self.update_student).grid(row=4, column=1, padx=5, pady=8)

        self.instructor_id = tk.StringVar()
        self.instructor_name = tk.StringVar()
        self.instructor_age = tk.StringVar()
        self.instructor_email = tk.StringVar()
        self._entry(self.instructor_frame, "Instructor ID", self.instructor_id, 0)
        self._entry(self.instructor_frame, "Name", self.instructor_name, 1)
        self._entry(self.instructor_frame, "Age", self.instructor_age, 2)
        self._entry(self.instructor_frame, "Email", self.instructor_email, 3)
        ttk.Button(self.instructor_frame, text="Add Instructor", command=self.add_instructor).grid(row=4, column=0, padx=5, pady=8)
        ttk.Button(self.instructor_frame, text="Update Instructor", command=self.update_instructor).grid(row=4, column=1, padx=5, pady=8)

        self.course_id = tk.StringVar()
        self.course_name = tk.StringVar()
        self.course_instructor = tk.StringVar()
        self._entry(self.course_frame, "Course ID", self.course_id, 0)
        self._entry(self.course_frame, "Course Name", self.course_name, 1)
        ttk.Label(self.course_frame, text="Instructor").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.course_instructor_box = ttk.Combobox(self.course_frame, textvariable=self.course_instructor, state="readonly", width=28)
        self.course_instructor_box.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.course_frame, text="Add Course", command=self.add_course).grid(row=3, column=0, padx=5, pady=8)
        ttk.Button(self.course_frame, text="Update Course", command=self.update_course).grid(row=3, column=1, padx=5, pady=8)

        assignments = ttk.LabelFrame(self.root, text="Registration and Assignment", padding=10)
        assignments.pack(fill="x", padx=10, pady=(0, 10))
        self.registration_student = tk.StringVar()
        self.registration_course = tk.StringVar()
        self.assignment_instructor = tk.StringVar()
        self.assignment_course = tk.StringVar()
        self.registration_student_box = ttk.Combobox(assignments, textvariable=self.registration_student, state="readonly")
        self.registration_course_box = ttk.Combobox(assignments, textvariable=self.registration_course, state="readonly")
        self.assignment_instructor_box = ttk.Combobox(assignments, textvariable=self.assignment_instructor, state="readonly")
        self.assignment_course_box = ttk.Combobox(assignments, textvariable=self.assignment_course, state="readonly")
        ttk.Label(assignments, text="Student").grid(row=0, column=0, padx=4)
        self.registration_student_box.grid(row=0, column=1, padx=4)
        ttk.Label(assignments, text="Course").grid(row=0, column=2, padx=4)
        self.registration_course_box.grid(row=0, column=3, padx=4)
        ttk.Button(assignments, text="Register Student", command=self.register_student).grid(row=0, column=4, padx=8)
        ttk.Label(assignments, text="Instructor").grid(row=1, column=0, padx=4, pady=8)
        self.assignment_instructor_box.grid(row=1, column=1, padx=4, pady=8)
        ttk.Label(assignments, text="Course").grid(row=1, column=2, padx=4, pady=8)
        self.assignment_course_box.grid(row=1, column=3, padx=4, pady=8)
        ttk.Button(assignments, text="Assign Instructor", command=self.assign_instructor).grid(row=1, column=4, padx=8, pady=8)

        tools = ttk.Frame(self.root, padding=(10, 0))
        tools.pack(fill="x")
        self.search_text = tk.StringVar()
        ttk.Label(tools, text="Search").pack(side="left")
        ttk.Entry(tools, textvariable=self.search_text, width=32).pack(side="left", padx=5)
        ttk.Button(tools, text="Search", command=self.search).pack(side="left", padx=3)
        ttk.Button(tools, text="Show All", command=self.refresh).pack(side="left", padx=3)
        ttk.Button(tools, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=3)
        ttk.Button(tools, text="Save", command=self.save_database).pack(side="right", padx=3)
        ttk.Button(tools, text="Load", command=self.load_database).pack(side="right", padx=3)

        columns = ("type", "id", "name", "detail", "extra")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=16)
        headings = ("Type", "ID", "Name/Course", "Age", "Email/Details")
        widths = (100, 110, 210, 90, 360)
        for column, heading, width in zip(columns, headings, widths):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    @staticmethod
    def _entry(parent, label, variable, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent, textvariable=variable, width=32).grid(row=row, column=1, sticky="ew", padx=5, pady=5)

    def _perform(self, operation, success_message):
        try:
            operation()
            self.refresh()
            messagebox.showinfo("Success", success_message)
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror("Error", str(error))

    def add_student(self):
        self._perform(
            lambda: self.database.add_student(self.student_id.get(), self.student_name.get(), self.student_age.get(), self.student_email.get()),
            "Student added.",
        )

    def add_instructor(self):
        self._perform(
            lambda: self.database.add_instructor(self.instructor_id.get(), self.instructor_name.get(), self.instructor_age.get(), self.instructor_email.get()),
            "Instructor added.",
        )

    def add_course(self):
        self._perform(
            lambda: self.database.add_course(self.course_id.get(), self.course_name.get(), self.course_instructor.get()),
            "Course added.",
        )

    def update_student(self):
        original_id = self.selected_id if self.selected_type == "Student" else self.student_id.get()
        self._perform(
            lambda: self.database.update_student(original_id, self.student_id.get(), self.student_name.get(), self.student_age.get(), self.student_email.get()),
            "Student updated.",
        )

    def update_instructor(self):
        original_id = self.selected_id if self.selected_type == "Instructor" else self.instructor_id.get()
        self._perform(
            lambda: self.database.update_instructor(original_id, self.instructor_id.get(), self.instructor_name.get(), self.instructor_age.get(), self.instructor_email.get()),
            "Instructor updated.",
        )

    def update_course(self):
        original_id = self.selected_id if self.selected_type == "Course" else self.course_id.get()
        self._perform(
            lambda: self.database.update_course(original_id, self.course_id.get(), self.course_name.get(), self.course_instructor.get()),
            "Course updated.",
        )

    def register_student(self):
        self._perform(
            lambda: self.database.enroll_student(self.registration_student.get(), self.registration_course.get()),
            "Student registered in course.",
        )

    def assign_instructor(self):
        self._perform(
            lambda: self.database.assign_instructor(self.assignment_instructor.get(), self.assignment_course.get()),
            "Instructor assigned to course.",
        )

    def delete_selected(self):
        if not self.selected_type:
            messagebox.showerror("Error", "Select a record first.")
            return
        self._perform(
            lambda: self.database.delete_record(self.selected_type, self.selected_id),
            "Record deleted.",
        )

    def search(self):
        self._fill_tree(self.database.search_records(self.search_text.get()))

    def refresh(self):
        students = [row["student_id"] for row in self.database.list_students()]
        instructors = [row["instructor_id"] for row in self.database.list_instructors()]
        courses = [row["course_id"] for row in self.database.list_courses()]
        self.registration_student_box["values"] = students
        self.registration_course_box["values"] = courses
        self.assignment_instructor_box["values"] = instructors
        self.assignment_course_box["values"] = courses
        self.course_instructor_box["values"] = [""] + instructors
        self._fill_tree(self.database.all_records())

    def _fill_tree(self, records):
        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert("", "end", values=record)

    def _on_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self.selected_type, self.selected_id = values[0], values[1]
        if self.selected_type == "Student":
            row = self.database.connection.execute("SELECT * FROM students WHERE student_id=?", (self.selected_id,)).fetchone()
            self.student_id.set(row["student_id"])
            self.student_name.set(row["name"])
            self.student_age.set(row["age"])
            self.student_email.set(row["email"])
        elif self.selected_type == "Instructor":
            row = self.database.connection.execute("SELECT * FROM instructors WHERE instructor_id=?", (self.selected_id,)).fetchone()
            self.instructor_id.set(row["instructor_id"])
            self.instructor_name.set(row["name"])
            self.instructor_age.set(row["age"])
            self.instructor_email.set(row["email"])
        else:
            row = self.database.connection.execute("SELECT * FROM courses WHERE course_id=?", (self.selected_id,)).fetchone()
            self.course_id.set(row["course_id"])
            self.course_name.set(row["course_name"])
            self.course_instructor.set(row["instructor_id"] or "")

    def save_database(self):
        filename = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite database", "*.db")])
        if filename:
            self._perform(lambda: self.database.backup(filename), "Database saved.")

    def load_database(self):
        filename = filedialog.askopenfilename(filetypes=[("SQLite database", "*.db")])
        if filename:
            self._perform(lambda: self.database.restore(filename), "Database loaded.")

    def close(self):
        self.database.close()
        self.root.destroy()


if __name__ == "__main__":
    application_root = tk.Tk()
    SchoolManagementTk(application_root)
    application_root.mainloop()
