import json
import re


def validate_age(age):
    age = int(age)
    if age < 0:
        raise ValueError("Age must be non-negative.")
    return age


def validate_email(email):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Enter a valid email address.")
    return email


class Person:
    def __init__(self, name, age, email):
        if not name.strip():
            raise ValueError("Name is required.")
        self.name = name.strip()
        self.age = validate_age(age)
        self._email = validate_email(email.strip())

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = validate_email(value.strip())

    def introduce(self):
        return f"My name is {self.name}, and I am {self.age} years old."


class Student(Person):
    def __init__(self, name, age, email, student_id, registered_courses=None):
        super().__init__(name, age, email)
        if not student_id.strip():
            raise ValueError("Student ID is required.")
        self.student_id = student_id.strip()
        self.registered_courses = list(registered_courses or [])

    def register_course(self, course):
        course_id = course.course_id if isinstance(course, Course) else str(course)
        if course_id not in self.registered_courses:
            self.registered_courses.append(course_id)
        if isinstance(course, Course):
            course.add_student(self)

    def introduce(self):
        return f"{super().introduce()} My student ID is {self.student_id}."

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "student_id": self.student_id,
            "registered_courses": self.registered_courses,
        }


class Instructor(Person):
    def __init__(self, name, age, email, instructor_id, assigned_courses=None):
        super().__init__(name, age, email)
        if not instructor_id.strip():
            raise ValueError("Instructor ID is required.")
        self.instructor_id = instructor_id.strip()
        self.assigned_courses = list(assigned_courses or [])

    def assign_course(self, course):
        course_id = course.course_id if isinstance(course, Course) else str(course)
        if course_id not in self.assigned_courses:
            self.assigned_courses.append(course_id)
        if isinstance(course, Course):
            course.instructor = self.instructor_id

    def introduce(self):
        return f"{super().introduce()} My instructor ID is {self.instructor_id}."

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "instructor_id": self.instructor_id,
            "assigned_courses": self.assigned_courses,
        }


class Course:
    def __init__(self, course_id, course_name, instructor=None, enrolled_students=None):
        if not course_id.strip() or not course_name.strip():
            raise ValueError("Course ID and course name are required.")
        self.course_id = course_id.strip()
        self.course_name = course_name.strip()
        self.instructor = instructor
        self.enrolled_students = list(enrolled_students or [])

    def add_student(self, student):
        student_id = student.student_id if isinstance(student, Student) else str(student)
        if student_id not in self.enrolled_students:
            self.enrolled_students.append(student_id)
        if isinstance(student, Student) and self.course_id not in student.registered_courses:
            student.registered_courses.append(self.course_id)

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor": self.instructor,
            "enrolled_students": self.enrolled_students,
        }


class SchoolManagementSystem:
    def __init__(self):
        self.students = {}
        self.instructors = {}
        self.courses = {}

    def add_student(self, student):
        if student.student_id in self.students:
            raise ValueError("Student ID already exists.")
        self.students[student.student_id] = student

    def add_instructor(self, instructor):
        if instructor.instructor_id in self.instructors:
            raise ValueError("Instructor ID already exists.")
        self.instructors[instructor.instructor_id] = instructor

    def add_course(self, course):
        if course.course_id in self.courses:
            raise ValueError("Course ID already exists.")
        self.courses[course.course_id] = course

    def register_student(self, student_id, course_id):
        self.students[student_id].register_course(self.courses[course_id])

    def assign_instructor(self, instructor_id, course_id):
        self.instructors[instructor_id].assign_course(self.courses[course_id])

    def to_dict(self):
        return {
            "students": [student.to_dict() for student in self.students.values()],
            "instructors": [instructor.to_dict() for instructor in self.instructors.values()],
            "courses": [course.to_dict() for course in self.courses.values()],
        }

    def save_data(self, filename):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)

    @classmethod
    def load_data(cls, filename):
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        system = cls()
        for item in data.get("students", []):
            system.add_student(Student(**item))
        for item in data.get("instructors", []):
            system.add_instructor(Instructor(**item))
        for item in data.get("courses", []):
            system.add_course(Course(**item))
        return system


if __name__ == "__main__":
    school = SchoolManagementSystem()
    student = Student("Student One", 20, "student@example.com", "S001")
    instructor = Instructor("Instructor One", 35, "instructor@example.com", "I001")
    course = Course("C001", "Software Tools")
    school.add_student(student)
    school.add_instructor(instructor)
    school.add_course(course)
    school.register_student("S001", "C001")
    school.assign_instructor("I001", "C001")
    print(student.introduce())
    print(instructor.introduce())
    print(f"{course.course_name}: {len(course.enrolled_students)} enrolled student(s)")
