import csv
import os
import re
import base64
import time
import statistics

STUDENT_CSV   = "student.csv"
COURSE_CSV    = "course.csv"
PROFESSOR_CSV = "professor.csv"
LOGIN_CSV     = "login.csv"


class Student:
    fields = ["Email_address", "First_name", "Last_name", "Course_id", "grades", "Marks"]

    def __init__(self, email_address, first_name, last_name, course_id, grades, marks):
        self.email_address = email_address
        self.first_name    = first_name
        self.last_name     = last_name
        self.course_id     = course_id
        self.grades        = grades
        self.marks         = marks

    def load(self):
        if not os.path.exists(STUDENT_CSV):
            return []
        with open(STUDENT_CSV, newline='') as f:
            return list(csv.DictReader(f))

    def save(self, records):
        with open(STUDENT_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(records)

    def display_records(self):
        records = self.load()
        print("\n--- Student Records ---")
        if not records:
            print("No records found.")
            return
        for r in records:
            print(f"Email: {r['Email_address']} | Name: {r['First_name']} {r['Last_name']} | "
                  f"Course ID: {r['Course_id']} | Grade: {r['grades']} | Marks: {r['Marks']}")

    def add_new_student(self):
        if not self.email_address or not self.first_name or not self.last_name or not self.course_id:
            print("Error: Email, first name, last name, and course ID cannot be empty.")
            return
        records = self.load()
        for r in records:
            if r['Email_address'] == self.email_address:
                print("Error: Email must be unique. Student already exists.")
                return
        records.append({
            "Email_address": self.email_address,
            "First_name":    self.first_name,
            "Last_name":     self.last_name,
            "Course_id":     self.course_id,
            "grades":        self.grades,
            "Marks":         self.marks,
        })
        self.save(records)
        print(f"Student '{self.first_name} {self.last_name}' added successfully.")

    def delete_new_student(self):
        records     = self.load()
        new_records = [r for r in records if r['Email_address'] != self.email_address]
        if len(new_records) < len(records):
            self.save(new_records)
            print(f"Student '{self.email_address}' deleted successfully.")
        else:
            print("Student not found.")

    def check_my_grades(self):
        for r in self.load():
            if r['Email_address'] == self.email_address:
                print(f"Grade for {r['First_name']} {r['Last_name']} "
                      f"(Course {r['Course_id']}): {r['grades']}")
                return
        print("Student not found.")

    def update_student_record(self, first_name=None, last_name=None,
                               course_id=None, grades=None, marks=None):
        records = self.load()
        for r in records:
            if r['Email_address'] == self.email_address:
                if first_name:        r['First_name'] = first_name
                if last_name:         r['Last_name']  = last_name
                if course_id:         r['Course_id']  = course_id
                if grades:            r['grades']     = grades
                if marks is not None: r['Marks']      = marks
                self.save(records)
                print(f"Record updated for '{r['First_name']} {r['Last_name']}'.")
                return
        print("Student not found.")

    def check_my_marks(self):
        for r in self.load():
            if r['Email_address'] == self.email_address:
                print(f"Marks for {r['First_name']} {r['Last_name']} "
                      f"(Course {r['Course_id']}): {r['Marks']}")
                return
        print("Student not found.")

    def search_student(self, email):
        records = self.load()
        start   = time.time()
        result  = None
        for r in records:
            if r['Email_address'] == email:
                result = r
                break
        elapsed = time.time() - start
        if result:
            print(f"\n--- Search Result ---")
            print(f"Email: {result['Email_address']} | Name: {result['First_name']} {result['Last_name']} | "
                  f"Course ID: {result['Course_id']} | Grade: {result['grades']} | Marks: {result['Marks']}")
        else:
            print("Student not found.")
        print(f"Time taken to search: {elapsed:.6f} seconds.")
        return result

    def sort_records(self, sort_by='email', ascending=True):
        records = self.load()
        key_map = {
            'email': lambda r: r['Email_address'].lower(),
            'name':  lambda r: (r['Last_name'].lower(), r['First_name'].lower()),
            'marks': lambda r: self._to_float(r['Marks']),
            'grade': lambda r: r['grades'].lower(),
        }
        key_fn   = key_map.get(sort_by, key_map['email'])
        start    = time.time()
        sorted_r = sorted(records, key=key_fn, reverse=not ascending)
        elapsed  = time.time() - start
        order_s  = "ascending" if ascending else "descending"
        print(f"\n--- Students sorted by {sort_by} ({order_s}) ---")
        if not sorted_r:
            print("No records found.")
        for r in sorted_r:
            print(f"Email: {r['Email_address']} | Name: {r['First_name']} {r['Last_name']} | "
                  f"Course ID: {r['Course_id']} | Grade: {r['grades']} | Marks: {r['Marks']}")
        print(f"Time taken to sort: {elapsed:.6f} seconds.")
        return sorted_r

    def _to_float(self, val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    def _get_marks_list(self, course_id=None):
        records = self.load()
        marks = []
        for r in records:
            if course_id and r['Course_id'] != course_id:
                continue
            try:
                marks.append(float(r['Marks']))
            except (TypeError, ValueError):
                pass
        return marks

    def get_average_marks(self, course_id=None):
        marks = self._get_marks_list(course_id)
        label = f"course '{course_id}'" if course_id else "all courses"
        if not marks:
            print(f"No numeric marks data found for {label}.")
            return None
        avg = statistics.mean(marks)
        print(f"Average marks ({label}): {avg:.2f}")
        return avg

    def get_median_marks(self, course_id=None):
        marks = self._get_marks_list(course_id)
        label = f"course '{course_id}'" if course_id else "all courses"
        if not marks:
            print(f"No numeric marks data found for {label}.")
            return None
        med = statistics.median(marks)
        print(f"Median marks ({label}): {med:.2f}")
        return med

    def generate_report_by_student(self, email):
        records         = self.load()
        student_records = [r for r in records if r['Email_address'] == email]
        print(f"\n--- Grade Report: Student '{email}' ---")
        if not student_records:
            print("No records found for this student.")
            return
        for r in student_records:
            print(f"Name: {r['First_name']} {r['Last_name']} | "
                  f"Course: {r['Course_id']} | Grade: {r['grades']} | Marks: {r['Marks']}")

    def generate_report_by_course(self, course_id):
        records        = self.load()
        course_records = [r for r in records if r['Course_id'] == course_id]
        print(f"\n--- Grade Report: Course '{course_id}' ---")
        if not course_records:
            print("No records found for this course.")
            return
        for r in course_records:
            print(f"  {r['Email_address']} | {r['First_name']} {r['Last_name']} | "
                  f"Grade: {r['grades']} | Marks: {r['Marks']}")
        marks = self._get_marks_list(course_id)
        if marks:
            print(f"  --- Statistics ---")
            print(f"  Average Marks: {statistics.mean(marks):.2f}")
            print(f"  Median Marks:  {statistics.median(marks):.2f}")


class Course:
    fields = ["Course_id", "Course_name", "Credits", "Description"]

    def __init__(self, course_id, course_name, credits, description):
        self.course_id   = course_id
        self.course_name = course_name
        self.credits     = credits
        self.description = description

    def load(self):
        if not os.path.exists(COURSE_CSV):
            return []
        with open(COURSE_CSV, newline='') as f:
            return list(csv.DictReader(f))

    def save(self, records):
        with open(COURSE_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(records)

    def display_courses(self):
        records = self.load()
        print("\n--- Course Records ---")
        if not records:
            print("No courses found.")
            return
        for r in records:
            print(f"Course ID: {r['Course_id']} | Name: {r['Course_name']} | "
                  f"Credits: {r['Credits']} | Description: {r['Description']}")

    def add_new_course(self):
        if not self.course_id or not self.course_name:
            print("Error: Course ID and name cannot be empty.")
            return
        records = self.load()
        for r in records:
            if r['Course_id'] == self.course_id:
                print("Error: Course ID must be unique.")
                return
        records.append({
            "Course_id":   self.course_id,
            "Course_name": self.course_name,
            "Credits":     self.credits,
            "Description": self.description,
        })
        self.save(records)
        print(f"Course '{self.course_name}' (ID: {self.course_id}) added successfully.")

    def delete_new_course(self):
        records     = self.load()
        new_records = [r for r in records if r['Course_id'] != self.course_id]
        if len(new_records) < len(records):
            self.save(new_records)
            print(f"Course '{self.course_id}' deleted successfully.")
        else:
            print("Course not found.")

    def update_course(self, course_name=None, credits=None, description=None):
        records = self.load()
        for r in records:
            if r['Course_id'] == self.course_id:
                if course_name: r['Course_name'] = course_name
                if credits:     r['Credits']     = credits
                if description: r['Description'] = description
                self.save(records)
                print(f"Course '{self.course_id}' updated successfully.")
                return
        print("Course not found.")


class Professor:
    fields = ["Professor_id", "Professor_Name", "Rank", "Course_id"]

    def __init__(self, professor_id, professor_name, rank, course_id):
        self.professor_id   = professor_id
        self.professor_name = professor_name
        self.rank           = rank
        self.course_id      = course_id

    def load(self):
        if not os.path.exists(PROFESSOR_CSV):
            return []
        with open(PROFESSOR_CSV, newline='') as f:
            return list(csv.DictReader(f))

    def save(self, records):
        with open(PROFESSOR_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(records)

    def professors_details(self):
        records = self.load()
        print("\n--- Professor Records ---")
        if not records:
            print("No professors found.")
            return
        for r in records:
            print(f"ID: {r['Professor_id']} | Name: {r['Professor_Name']} | "
                  f"Rank: {r['Rank']} | Course ID: {r['Course_id']}")

    def add_new_professor(self):
        if not self.professor_id or not self.professor_name:
            print("Error: Professor ID and name cannot be empty.")
            return
        records = self.load()
        for r in records:
            if r['Professor_id'] == self.professor_id:
                print("Error: Professor ID must be unique.")
                return
        records.append({
            "Professor_id":   self.professor_id,
            "Professor_Name": self.professor_name,
            "Rank":           self.rank,
            "Course_id":      self.course_id,
        })
        self.save(records)
        print(f"Professor '{self.professor_name}' added successfully.")

    def delete_professore(self):
        records     = self.load()
        new_records = [r for r in records if r['Professor_id'] != self.professor_id]
        if len(new_records) < len(records):
            self.save(new_records)
            print(f"Professor '{self.professor_id}' deleted successfully.")
        else:
            print("Professor not found.")

    def modify_professor_details(self, professor_name=None, rank=None, course_id=None):
        records = self.load()
        for r in records:
            if r['Professor_id'] == self.professor_id:
                if professor_name: r['Professor_Name'] = professor_name
                if rank:           r['Rank']           = rank
                if course_id:      r['Course_id']      = course_id
                self.save(records)
                print(f"Professor '{r['Professor_Name']}' details updated successfully.")
                return
        print("Professor not found.")

    def show_course_details_by_professor(self):
        for r in self.load():
            if r['Professor_id'] == self.professor_id:
                print(f"\n--- Courses taught by {r['Professor_Name']} ---")
                course  = Course(r['Course_id'], "", "", "")
                matches = [c for c in course.load() if c['Course_id'] == r['Course_id']]
                if not matches:
                    print(f"No course found with ID '{r['Course_id']}'.")
                for c in matches:
                    print(f"Course ID: {c['Course_id']} | Name: {c['Course_name']} | "
                          f"Credits: {c['Credits']} | Description: {c['Description']}")
                return
        print("Professor not found.")

    def generate_report_by_professor(self):
        for r in self.load():
            if r['Professor_id'] == self.professor_id:
                print(f"\n--- Grade Report: Professor '{r['Professor_Name']}' ---")
                Student("", "", "", "", "", "").generate_report_by_course(r['Course_id'])
                return
        print("Professor not found.")


class Grades:
    _rubric = [
        {"Grade_id": "1", "Grade": "A", "Marks_range": "90-100"},
        {"Grade_id": "2", "Grade": "B", "Marks_range": "80-89"},
        {"Grade_id": "3", "Grade": "C", "Marks_range": "70-79"},
        {"Grade_id": "4", "Grade": "D", "Marks_range": "60-69"},
        {"Grade_id": "5", "Grade": "F", "Marks_range": "0-59"},
    ]

    def __init__(self, grade_id, grade, marks_range):
        self.grade_id    = grade_id
        self.grade       = grade
        self.marks_range = marks_range

    def display_grade_report(self):
        print("\n--- Grade Rubric ---")
        if not Grades._rubric:
            print("No grade records found.")
            return
        for g in Grades._rubric:
            print(f"Grade ID: {g['Grade_id']} | Grade: {g['Grade']} | "
                  f"Marks Range: {g['Marks_range']}")

    def add_grade(self):
        if not self.grade_id or not self.grade:
            print("Error: Grade ID and grade cannot be empty.")
            return
        for g in Grades._rubric:
            if g['Grade_id'] == self.grade_id:
                print("Error: Grade ID must be unique.")
                return
        Grades._rubric.append({
            "Grade_id":    self.grade_id,
            "Grade":       self.grade,
            "Marks_range": self.marks_range,
        })
        print(f"Grade '{self.grade}' (ID: {self.grade_id}) added successfully.")

    def delete_grade(self):
        original       = len(Grades._rubric)
        Grades._rubric = [g for g in Grades._rubric if g['Grade_id'] != self.grade_id]
        if len(Grades._rubric) < original:
            print(f"Grade ID '{self.grade_id}' deleted successfully.")
        else:
            print("Grade record not found.")

    def modify_grade(self, grade=None, marks_range=None):
        for g in Grades._rubric:
            if g['Grade_id'] == self.grade_id:
                if grade:       g['Grade']       = grade
                if marks_range: g['Marks_range'] = marks_range
                print(f"Grade ID '{self.grade_id}' updated successfully.")
                return
        print("Grade record not found.")


class LoginUser:
    fields       = ["User_id", "Password", "Role"]
    _KEY         = "CheckMyGrade2026"
    _VALID_ROLES = {"student", "professor", "admin"}

    def __init__(self, user_id, password, role):
        self.user_id      = user_id
        self.password     = password
        self.role         = role.lower().strip() if role else ""
        self.is_logged_in = False

    def Encrypt_password(self, password):
        key   = self._KEY
        xored = bytes([ord(c) ^ ord(key[i % len(key)]) for i, c in enumerate(password)])
        return base64.b64encode(xored).decode("utf-8")

    def decrypt_password(self, encrypted):
        key   = self._KEY
        xored = base64.b64decode(encrypted.encode("utf-8"))
        return "".join(chr(b ^ ord(key[i % len(key)])) for i, b in enumerate(xored))

    @staticmethod
    def _is_strong(pwd):
        return (len(pwd) >= 8
                and re.search(r"[A-Z]", pwd)
                and re.search(r"\d", pwd)
                and re.search(r"[!@#$%^&*()\-_+=]", pwd))

    def load(self):
        if not os.path.exists(LOGIN_CSV):
            return []
        with open(LOGIN_CSV, newline="") as f:
            return list(csv.DictReader(f))

    def save(self, records):
        with open(LOGIN_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(records)

    def get_role(self):
        for r in self.load():
            if r["User_id"] == self.user_id:
                return r["Role"].lower()
        return None

    def register(self):
        if not self.user_id or not self.password:
            print("Error: User ID and password cannot be empty.")
            return False
        if self.role not in self._VALID_ROLES:
            print(f"Error: Role must be one of {sorted(self._VALID_ROLES)}.")
            return False
        if not self._is_strong(self.password):
            print("Error: Password must be >=8 chars and include an uppercase "
                  "letter, a digit, and a special character (!@#$%^&*()-_+=).")
            return False
        records = self.load()
        for r in records:
            if r["User_id"] == self.user_id:
                print("Error: User already exists.")
                return False
        records.append({
            "User_id":  self.user_id,
            "Password": self.Encrypt_password(self.password),
            "Role":     self.role,
        })
        self.save(records)
        print(f"User '{self.user_id}' registered as '{self.role}' (password encrypted).")
        return True

    def Login(self):
        for r in self.load():
            if r["User_id"] == self.user_id:
                if self.decrypt_password(r["Password"]) == self.password:
                    self.is_logged_in = True
                    self.role         = r["Role"].lower()
                    print(f"Login successful. Welcome, {self.user_id}  [role: {self.role}]")
                    return True
        print("Login failed: invalid user ID or password.")
        return False

    def Logout(self):
        if self.is_logged_in:
            self.is_logged_in = False
            print(f"'{self.user_id}' logged out successfully.")
        else:
            print(f"'{self.user_id}' is not currently logged in.")

    def Change_password(self, old_password, new_password):
        if not self._is_strong(new_password):
            print("Error: New password must be >=8 chars and include an uppercase "
                  "letter, a digit, and a special character.")
            return
        records = self.load()
        for r in records:
            if r["User_id"] == self.user_id:
                if self.decrypt_password(r["Password"]) == old_password:
                    r["Password"] = self.Encrypt_password(new_password)
                    self.save(records)
                    self.password = new_password
                    print(f"Password changed successfully for '{self.user_id}'.")
                else:
                    print("Password change failed: old password is incorrect.")
                return
        print("User not found.")


current_user = None


def _logged_in():
    return current_user is not None and current_user.is_logged_in


def _role():
    return current_user.role if _logged_in() else ""


def _require_login():
    if not _logged_in():
        print("  Access denied — please log in first (Login Menu -> Login).")
        return False
    return True


def _require_role(*roles):
    if not _require_login():
        return False
    if _role() not in roles:
        print(f"  Access denied — this section requires role: {' / '.join(roles)}.")
        return False
    return True


def _student_menu_full():
    while True:
        print("\n--- STUDENT MENU ---")
        print(" 1. Display All Records")
        print(" 2. Add Student")
        print(" 3. Delete Student")
        print(" 4. Update Student Record")
        print(" 5. Check My Grades")
        print(" 6. Check My Marks")
        print(" 7. Search Student (with timing)")
        print(" 8. Sort Students (with timing)")
        print(" 9. Average & Median Marks")
        print("10. Report by Student")
        print("11. Report by Course")
        print("12. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            Student("", "", "", "", "", "").display_records()
        elif choice == "2":
            email = input("Email: ").strip()
            fn    = input("First Name: ").strip()
            ln    = input("Last Name: ").strip()
            cid   = input("Course ID: ").strip()
            grade = input("Grade (e.g. A, B+): ").strip()
            marks = input("Marks (numeric): ").strip()
            Student(email, fn, ln, cid, grade, marks).add_new_student()
        elif choice == "3":
            email = input("Email to delete: ").strip()
            Student(email, "", "", "", "", "").delete_new_student()
        elif choice == "4":
            email = input("Email: ").strip()
            fn    = input("New First Name  (Enter to skip): ").strip() or None
            ln    = input("New Last Name   (Enter to skip): ").strip() or None
            cid   = input("New Course ID   (Enter to skip): ").strip() or None
            grade = input("New Grade       (Enter to skip): ").strip() or None
            marks = input("New Marks       (Enter to skip): ").strip() or None
            Student(email, "", "", "", "", "").update_student_record(fn, ln, cid, grade, marks)
        elif choice == "5":
            email = input("Email: ").strip()
            Student(email, "", "", "", "", "").check_my_grades()
        elif choice == "6":
            email = input("Email: ").strip()
            Student(email, "", "", "", "", "").check_my_marks()
        elif choice == "7":
            email = input("Search by Email: ").strip()
            Student("", "", "", "", "", "").search_student(email)
        elif choice == "8":
            print("Sort by: 1) Email  2) Name  3) Marks  4) Grade")
            sb_map  = {"1": "email", "2": "name", "3": "marks", "4": "grade"}
            sort_by = sb_map.get(input("Select: ").strip(), "email")
            asc     = input("Order - 1) Ascending  2) Descending: ").strip()
            Student("", "", "", "", "", "").sort_records(sort_by, asc != "2")
        elif choice == "9":
            cid = input("Course ID (Enter to skip for all): ").strip() or None
            s   = Student("", "", "", "", "", "")
            s.get_average_marks(cid)
            s.get_median_marks(cid)
        elif choice == "10":
            email = input("Student Email: ").strip()
            Student("", "", "", "", "", "").generate_report_by_student(email)
        elif choice == "11":
            cid = input("Course ID: ").strip()
            Student("", "", "", "", "", "").generate_report_by_course(cid)
        elif choice == "12":
            break


def _student_menu_restricted():
    email = current_user.user_id
    while True:
        print(f"\n--- STUDENT MENU  [{email}] ---")
        print("1. Check My Grades")
        print("2. Check My Marks")
        print("3. My Grade Report")
        print("4. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            Student(email, "", "", "", "", "").check_my_grades()
        elif choice == "2":
            Student(email, "", "", "", "", "").check_my_marks()
        elif choice == "3":
            Student("", "", "", "", "", "").generate_report_by_student(email)
        elif choice == "4":
            break


def student_menu():
    if not _require_login():
        return
    if _role() == "student":
        _student_menu_restricted()
    else:
        _student_menu_full()


def course_menu():
    if not _require_role("admin", "professor"):
        return
    while True:
        print("\n--- COURSE MENU ---")
        print("1. Display Courses")
        print("2. Add Course")
        print("3. Delete Course")
        print("4. Update Course")
        print("5. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            Course("", "", "", "").display_courses()
        elif choice == "2":
            cid     = input("Course ID: ").strip()
            cname   = input("Course Name: ").strip()
            credits = input("Credits: ").strip()
            desc    = input("Description: ").strip()
            Course(cid, cname, credits, desc).add_new_course()
        elif choice == "3":
            cid = input("Course ID to delete: ").strip()
            Course(cid, "", "", "").delete_new_course()
        elif choice == "4":
            cid     = input("Course ID: ").strip()
            cname   = input("New Course Name   (Enter to skip): ").strip() or None
            credits = input("New Credits       (Enter to skip): ").strip() or None
            desc    = input("New Description   (Enter to skip): ").strip() or None
            Course(cid, "", "", "").update_course(cname, credits, desc)
        elif choice == "5":
            break


def professor_menu():
    if not _require_role("admin", "professor"):
        return
    while True:
        print("\n--- PROFESSOR MENU ---")
        print("1. Display Professors")
        print("2. Add Professor")
        print("3. Delete Professor")
        print("4. Modify Professor Details")
        print("5. Show Course by Professor")
        print("6. Report by Professor")
        print("7. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            Professor("", "", "", "").professors_details()
        elif choice == "2":
            pid   = input("Professor ID (email): ").strip()
            pname = input("Professor Name: ").strip()
            rank  = input("Rank: ").strip()
            cid   = input("Course ID: ").strip()
            Professor(pid, pname, rank, cid).add_new_professor()
        elif choice == "3":
            pid = input("Professor ID to delete: ").strip()
            Professor(pid, "", "", "").delete_professore()
        elif choice == "4":
            pid   = input("Professor ID: ").strip()
            pname = input("New Name       (Enter to skip): ").strip() or None
            rank  = input("New Rank       (Enter to skip): ").strip() or None
            cid   = input("New Course ID  (Enter to skip): ").strip() or None
            Professor(pid, "", "", "").modify_professor_details(pname, rank, cid)
        elif choice == "5":
            pid = input("Professor ID: ").strip()
            Professor(pid, "", "", "").show_course_details_by_professor()
        elif choice == "6":
            pid = input("Professor ID: ").strip()
            Professor(pid, "", "", "").generate_report_by_professor()
        elif choice == "7":
            break


def grades_menu():
    if not _require_role("admin", "professor"):
        return
    while True:
        print("\n--- GRADES MENU ---")
        print("1. Display Grade Rubric")
        print("2. Add Grade Entry")
        print("3. Delete Grade Entry")
        print("4. Modify Grade Entry")
        print("5. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            Grades("", "", "").display_grade_report()
        elif choice == "2":
            gid = input("Grade ID: ").strip()
            gv  = input("Grade (e.g. A, B+): ").strip()
            rng = input("Marks Range (e.g. 90-100): ").strip()
            Grades(gid, gv, rng).add_grade()
        elif choice == "3":
            gid = input("Grade ID to delete: ").strip()
            Grades(gid, "", "").delete_grade()
        elif choice == "4":
            gid = input("Grade ID: ").strip()
            gv  = input("New Grade        (Enter to skip): ").strip() or None
            rng = input("New Marks Range  (Enter to skip): ").strip() or None
            Grades(gid, "", "").modify_grade(gv, rng)
        elif choice == "5":
            break


def login_menu():
    global current_user
    while True:
        status = (f"Logged in as: {current_user.user_id}  [role: {current_user.role}]"
                  if _logged_in() else "Not logged in")
        print(f"\n--- LOGIN MENU  ({status}) ---")
        print("1. Register")
        print("2. Login")
        print("3. Logout")
        print("4. Change Password")
        print("5. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            uid  = input("User ID (email): ").strip()
            pwd  = input("Password: ").strip()
            role = input("Role (student / professor / admin): ").strip()
            LoginUser(uid, pwd, role).register()
        elif choice == "2":
            if _logged_in():
                print(f"Already logged in as '{current_user.user_id}'. Logout first.")
                continue
            uid  = input("User ID: ").strip()
            pwd  = input("Password: ").strip()
            user = LoginUser(uid, pwd, "")
            if user.Login():
                current_user = user
        elif choice == "3":
            if _logged_in():
                current_user.Logout()
                current_user = None
            else:
                print("No user is currently logged in.")
        elif choice == "4":
            uid     = input("User ID: ").strip()
            old_pwd = input("Old Password: ").strip()
            new_pwd = input("New Password: ").strip()
            LoginUser(uid, old_pwd, "").Change_password(old_pwd, new_pwd)
        elif choice == "5":
            break


def main():
    while True:
        print("\n===== CHECK MY GRADE SYSTEM =====")
        if _logged_in():
            print(f"  Logged in as : {current_user.user_id}")
            print(f"  Role         : {current_user.role}")
        else:
            print("  Status: Not logged in  (go to Login Menu to sign in)")

        print("\n1. Student Menu")
        print("2. Course Menu       [professor / admin]")
        print("3. Professor Menu    [professor / admin]")
        print("4. Grades Menu       [professor / admin]")
        print("5. Login Menu")
        print("6. Exit")

        main_choice = input("\nSelect option: ").strip()

        if main_choice == "1":
            student_menu()
        elif main_choice == "2":
            course_menu()
        elif main_choice == "3":
            professor_menu()
        elif main_choice == "4":
            grades_menu()
        elif main_choice == "5":
            login_menu()
        elif main_choice == "6":
            print("Exiting System.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
