import os
import shutil
import sqlite3

from part1_oop import validate_age, validate_email


class SchoolDatabase:
    def __init__(self, database_path="school_management.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_schema()

    def create_schema(self):
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK (age >= 0),
                email TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS instructors (
                instructor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK (age >= 0),
                email TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                instructor_id TEXT,
                FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
                    ON UPDATE CASCADE ON DELETE SET NULL
            );
            CREATE TABLE IF NOT EXISTS enrollments (
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            );
            """
        )
        self.connection.commit()

    @staticmethod
    def _required(value, label):
        value = str(value).strip()
        if not value:
            raise ValueError(f"{label} is required.")
        return value

    def add_student(self, student_id, name, age, email):
        self.connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?)",
            (
                self._required(student_id, "Student ID"),
                self._required(name, "Name"),
                validate_age(age),
                validate_email(email.strip()),
            ),
        )
        self.connection.commit()

    def add_instructor(self, instructor_id, name, age, email):
        self.connection.execute(
            "INSERT INTO instructors VALUES (?, ?, ?, ?)",
            (
                self._required(instructor_id, "Instructor ID"),
                self._required(name, "Name"),
                validate_age(age),
                validate_email(email.strip()),
            ),
        )
        self.connection.commit()

    def add_course(self, course_id, course_name, instructor_id=None):
        instructor_id = instructor_id.strip() if instructor_id else None
        self.connection.execute(
            "INSERT INTO courses VALUES (?, ?, ?)",
            (
                self._required(course_id, "Course ID"),
                self._required(course_name, "Course name"),
                instructor_id or None,
            ),
        )
        self.connection.commit()

    def update_student(self, original_id, student_id, name, age, email):
        self.connection.execute(
            "UPDATE students SET student_id=?, name=?, age=?, email=? WHERE student_id=?",
            (
                self._required(student_id, "Student ID"),
                self._required(name, "Name"),
                validate_age(age),
                validate_email(email.strip()),
                original_id,
            ),
        )
        self.connection.commit()

    def update_instructor(self, original_id, instructor_id, name, age, email):
        self.connection.execute(
            "UPDATE instructors SET instructor_id=?, name=?, age=?, email=? WHERE instructor_id=?",
            (
                self._required(instructor_id, "Instructor ID"),
                self._required(name, "Name"),
                validate_age(age),
                validate_email(email.strip()),
                original_id,
            ),
        )
        self.connection.commit()

    def update_course(self, original_id, course_id, course_name, instructor_id=None):
        instructor_id = instructor_id.strip() if instructor_id else None
        self.connection.execute(
            "UPDATE courses SET course_id=?, course_name=?, instructor_id=? WHERE course_id=?",
            (
                self._required(course_id, "Course ID"),
                self._required(course_name, "Course name"),
                instructor_id or None,
                original_id,
            ),
        )
        self.connection.commit()

    def delete_record(self, record_type, record_id):
        tables = {"Student": ("students", "student_id"), "Instructor": ("instructors", "instructor_id"), "Course": ("courses", "course_id")}
        if record_type not in tables:
            raise ValueError("Select a valid record.")
        table, column = tables[record_type]
        self.connection.execute(f"DELETE FROM {table} WHERE {column} = ?", (record_id,))
        self.connection.commit()

    def enroll_student(self, student_id, course_id):
        self.connection.execute(
            "INSERT OR IGNORE INTO enrollments VALUES (?, ?)",
            (student_id, course_id),
        )
        self.connection.commit()

    def assign_instructor(self, instructor_id, course_id):
        self.connection.execute(
            "UPDATE courses SET instructor_id=? WHERE course_id=?",
            (instructor_id, course_id),
        )
        self.connection.commit()

    def list_students(self):
        return self.connection.execute("SELECT * FROM students ORDER BY student_id").fetchall()

    def list_instructors(self):
        return self.connection.execute("SELECT * FROM instructors ORDER BY instructor_id").fetchall()

    def list_courses(self):
        return self.connection.execute(
            """
            SELECT c.course_id, c.course_name, c.instructor_id,
                   COUNT(e.student_id) AS enrolled_count
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.course_id
            GROUP BY c.course_id, c.course_name, c.instructor_id
            ORDER BY c.course_id
            """
        ).fetchall()

    def all_records(self):
        records = []
        for row in self.list_students():
            records.append(("Student", row["student_id"], row["name"], row["age"], row["email"]))
        for row in self.list_instructors():
            records.append(("Instructor", row["instructor_id"], row["name"], row["age"], row["email"]))
        for row in self.list_courses():
            details = f"Instructor: {row['instructor_id'] or 'Unassigned'}; Students: {row['enrolled_count']}"
            records.append(("Course", row["course_id"], row["course_name"], "", details))
        return records

    def search_records(self, query):
        query = f"%{query.strip()}%"
        rows = self.connection.execute(
            """
            SELECT 'Student' AS type, student_id AS id, name, CAST(age AS TEXT) AS detail, email AS extra
            FROM students WHERE name LIKE ? OR student_id LIKE ?
            UNION ALL
            SELECT 'Instructor', instructor_id, name, CAST(age AS TEXT), email
            FROM instructors WHERE name LIKE ? OR instructor_id LIKE ?
            UNION ALL
            SELECT 'Course', course_id, course_name, COALESCE(instructor_id, ''), ''
            FROM courses WHERE course_name LIKE ? OR course_id LIKE ?
            ORDER BY type, id
            """,
            (query, query, query, query, query, query),
        ).fetchall()
        return [(row["type"], row["id"], row["name"], row["detail"], row["extra"]) for row in rows]

    def export_csv(self, filename):
        import csv

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "ID", "Name", "Age/Instructor", "Email/Details"])
            writer.writerows(self.all_records())

    def backup(self, filename):
        destination = sqlite3.connect(filename)
        try:
            self.connection.backup(destination)
        finally:
            destination.close()

    def restore(self, filename):
        self.connection.close()
        shutil.copy2(filename, self.database_path)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_schema()

    def close(self):
        self.connection.close()


def print_database_summary(database):
    print(f"Database: {os.path.abspath(database.database_path)}")
    for table in ("students", "instructors", "courses", "enrollments"):
        rows = database.connection.execute(f"SELECT * FROM {table}").fetchall()
        print(f"\n{table.upper()} ({len(rows)} record(s))")
        for row in rows:
            print(dict(row))


if __name__ == "__main__":
    school_database = SchoolDatabase()
    print_database_summary(school_database)
    school_database.close()
