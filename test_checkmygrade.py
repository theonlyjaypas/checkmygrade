# IMPORT LIBRARIES
import unittest
import os
import time

import checkmygrade
from checkmygrade import Student, Course, Professor, Grades, LoginUser

TEST_STUDENT_CSV   = "test_Student.csv"
TEST_COURSE_CSV    = "test_Course.csv"
TEST_PROFESSOR_CSV = "test_Professor.csv"
TEST_LOGIN_CSV     = "test_Login.csv"


def _patch_csvs():
    checkmygrade.STUDENT_CSV   = TEST_STUDENT_CSV
    checkmygrade.COURSE_CSV    = TEST_COURSE_CSV
    checkmygrade.PROFESSOR_CSV = TEST_PROFESSOR_CSV
    checkmygrade.LOGIN_CSV     = TEST_LOGIN_CSV


def _cleanup():
    for f in [TEST_STUDENT_CSV, TEST_COURSE_CSV, TEST_PROFESSOR_CSV, TEST_LOGIN_CSV]:
        if os.path.exists(f):
            os.remove(f)


_patch_csvs()


class TestStudent(unittest.TestCase):

    GRADE_POOL  = ["A", "A-", "B+", "B", "B-"]
    COURSE_POOL = ["DATA200", "DATA201", "DATA202", "DATA203", "DATA204"]

    @classmethod
    def setUpClass(cls):
        _patch_csvs()
        _cleanup()

        print("\n" + "=" * 60)
        print("TestStudent — inserting 1000 student records ...")
        start = time.time()
        for i in range(1, 1001):
            Student(
                email_address=f"student{i:04d}@test.edu",
                first_name=f"First{i}",
                last_name=f"Last{i}",
                course_id=cls.COURSE_POOL[i % 5],
                grades=cls.GRADE_POOL[i % 5],
                marks=str(round(60.0 + (i % 40) + (i % 3) * 0.5, 1)),
            ).add_new_student()
        elapsed = time.time() - start
        print(f"  Inserted 1000 records in {elapsed:.4f} seconds.")
        print("=" * 60)

    @classmethod
    def tearDownClass(cls):
        _cleanup()

    def test_01_record_count(self):
        records = Student("", "", "", "", "", "").load()
        self.assertEqual(len(records), 1000,
                         "Expected 1000 student records in CSV.")

    def test_02_add_duplicate_rejected(self):
        before = len(Student("", "", "", "", "", "").load())
        Student("student0001@test.edu", "X", "Y", "DATA200", "A", "95") \
            .add_new_student()
        after = len(Student("", "", "", "", "", "").load())
        self.assertEqual(before, after, "Duplicate email should be rejected.")

    def test_03_add_empty_fields_rejected(self):
        before = len(Student("", "", "", "", "", "").load())
        Student("", "NoEmail", "User", "DATA200", "A", "90").add_new_student()
        after = len(Student("", "", "", "", "", "").load())
        self.assertEqual(before, after, "Empty email should be rejected.")

    def test_04_search_existing_student(self):
        print("\n  [search] student0500@test.edu", end=" — ")
        result = Student("", "", "", "", "", "").search_student(
            "student0500@test.edu")
        self.assertIsNotNone(result, "student0500 should be found.")
        self.assertEqual(result["First_name"], "First500")

    def test_05_search_missing_student(self):
        print("\n  [search] nobody@test.edu", end=" — ")
        result = Student("", "", "", "", "", "").search_student(
            "nobody@test.edu")
        self.assertIsNone(result, "Non-existent student should return None.")

    def test_06_search_timing_all_records(self):
        s     = Student("", "", "", "", "", "")
        total = 0.0
        print("\n  [search timing across 10 lookups]")
        for i in range(100, 1001, 100):
            email = f"student{i:04d}@test.edu"
            t0    = time.time()
            result = s.search_student(email)
            total += time.time() - t0
            self.assertIsNotNone(result, f"{email} must be found.")
        print(f"  Total time for 10 searches: {total:.6f} seconds.")

    def test_07_sort_marks_ascending(self):
        print("\n  [sort] marks ascending — ", end="")
        sorted_r = Student("", "", "", "", "", "").sort_records(
            "marks", ascending=True)
        marks = [float(r["Marks"]) for r in sorted_r]
        self.assertEqual(marks, sorted(marks),
                         "Marks should be in ascending order.")

    def test_08_sort_marks_descending(self):
        print("\n  [sort] marks descending — ", end="")
        sorted_r = Student("", "", "", "", "", "").sort_records(
            "marks", ascending=False)
        marks = [float(r["Marks"]) for r in sorted_r]
        self.assertEqual(marks, sorted(marks, reverse=True),
                         "Marks should be in descending order.")

    def test_09_sort_email_ascending(self):
        print("\n  [sort] email ascending — ", end="")
        sorted_r = Student("", "", "", "", "", "").sort_records(
            "email", ascending=True)
        emails = [r["Email_address"].lower() for r in sorted_r]
        self.assertEqual(emails, sorted(emails),
                         "Emails should be in ascending order.")

    def test_10_sort_email_descending(self):
        print("\n  [sort] email descending — ", end="")
        sorted_r = Student("", "", "", "", "", "").sort_records(
            "email", ascending=False)
        emails = [r["Email_address"].lower() for r in sorted_r]
        self.assertEqual(emails, sorted(emails, reverse=True),
                         "Emails should be in descending order.")

    def test_11_update_student(self):
        Student("student0001@test.edu", "", "", "", "", "").update_student_record(
            first_name="UpdatedFirst", grades="A+", marks="99"
        )
        result = Student("", "", "", "", "", "").search_student(
            "student0001@test.edu")
        self.assertIsNotNone(result)
        self.assertEqual(result["First_name"], "UpdatedFirst")
        self.assertEqual(result["grades"], "A+")
        self.assertEqual(result["Marks"], "99")

    def test_12_update_nonexistent_student(self):
        before = len(Student("", "", "", "", "", "").load())
        Student("ghost@test.edu", "", "", "", "", "").update_student_record(
            first_name="Ghost"
        )
        after = len(Student("", "", "", "", "", "").load())
        self.assertEqual(before, after)

    def test_13_delete_student(self):
        before = len(Student("", "", "", "", "", "").load())
        Student("student1000@test.edu", "", "", "", "", "").delete_new_student()
        after = len(Student("", "", "", "", "", "").load())
        self.assertEqual(after, before - 1)
        result = Student("", "", "", "", "", "").search_student(
            "student1000@test.edu")
        self.assertIsNone(result)

    def test_14_delete_nonexistent_student(self):
        before = len(Student("", "", "", "", "", "").load())
        Student("nobody@test.edu", "", "", "", "", "").delete_new_student()
        after = len(Student("", "", "", "", "", "").load())
        self.assertEqual(before, after)

    def test_15_average_marks_all_courses(self):
        avg = Student("", "", "", "", "", "").get_average_marks()
        self.assertIsNotNone(avg)
        self.assertIsInstance(avg, float)
        self.assertGreater(avg, 0)

    def test_16_median_marks_all_courses(self):
        med = Student("", "", "", "", "", "").get_median_marks()
        self.assertIsNotNone(med)
        self.assertIsInstance(med, float)
        self.assertGreater(med, 0)

    def test_17_average_marks_by_course(self):
        avg = Student("", "", "", "", "", "").get_average_marks("DATA200")
        self.assertIsNotNone(avg)
        self.assertIsInstance(avg, float)

    def test_18_stats_nonexistent_course(self):
        avg = Student("", "", "", "", "", "").get_average_marks("FAKE999")
        self.assertIsNone(avg)


class TestCourse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _patch_csvs()
        _cleanup()

    @classmethod
    def tearDownClass(cls):
        _cleanup()

    def test_01_add_course(self):
        Course("CS101", "Intro to CS", "3", "Basic programming concepts") \
            .add_new_course()
        records = Course("", "", "", "").load()
        self.assertTrue(any(r["Course_id"] == "CS101" for r in records),
                        "CS101 should be in CSV after add.")

    def test_02_add_second_course(self):
        Course("DATA200", "Data Science", "3", "Python and data science") \
            .add_new_course()
        records = Course("", "", "", "").load()
        self.assertEqual(len(records), 2)

    def test_03_add_duplicate_rejected(self):
        before = len(Course("", "", "", "").load())
        Course("CS101", "Duplicate", "3", "Dup desc").add_new_course()
        after = len(Course("", "", "", "").load())
        self.assertEqual(before, after, "Duplicate course ID should be rejected.")

    def test_04_add_empty_id_rejected(self):
        before = len(Course("", "", "", "").load())
        Course("", "No ID Course", "3", "desc").add_new_course()
        after = len(Course("", "", "", "").load())
        self.assertEqual(before, after)

    def test_05_update_course_name(self):
        Course("CS101", "", "", "").update_course(
            course_name="Introduction to Computer Science")
        records = Course("", "", "", "").load()
        match = next((r for r in records if r["Course_id"] == "CS101"), None)
        self.assertIsNotNone(match)
        self.assertEqual(match["Course_name"], "Introduction to Computer Science")

    def test_06_update_course_credits(self):
        Course("CS101", "", "", "").update_course(credits="4")
        records = Course("", "", "", "").load()
        match = next((r for r in records if r["Course_id"] == "CS101"), None)
        self.assertIsNotNone(match)
        self.assertEqual(match["Credits"], "4")

    def test_07_update_course_description(self):
        Course("CS101", "", "", "").update_course(
            description="Updated description for CS101")
        records = Course("", "", "", "").load()
        match = next((r for r in records if r["Course_id"] == "CS101"), None)
        self.assertIsNotNone(match)
        self.assertEqual(match["Description"], "Updated description for CS101")

    def test_08_update_nonexistent_course(self):
        before = len(Course("", "", "", "").load())
        Course("GHOST999", "", "", "").update_course(course_name="Ghost")
        after = len(Course("", "", "", "").load())
        self.assertEqual(before, after)

    def test_09_delete_course(self):
        before = len(Course("", "", "", "").load())
        Course("CS101", "", "", "").delete_new_course()
        after = len(Course("", "", "", "").load())
        self.assertEqual(after, before - 1)
        records = Course("", "", "", "").load()
        self.assertFalse(any(r["Course_id"] == "CS101" for r in records))

    def test_10_delete_nonexistent_course(self):
        before = len(Course("", "", "", "").load())
        Course("NOTEXIST", "", "", "").delete_new_course()
        after = len(Course("", "", "", "").load())
        self.assertEqual(before, after)


class TestProfessor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _patch_csvs()
        _cleanup()

    @classmethod
    def tearDownClass(cls):
        _cleanup()

    def test_01_add_professor(self):
        Professor("prof1@test.edu", "Dr. Smith", "Senior Professor", "DATA200") \
            .add_new_professor()
        records = Professor("", "", "", "").load()
        self.assertTrue(
            any(r["Professor_id"] == "prof1@test.edu" for r in records),
            "prof1 should be in CSV after add.")

    def test_02_add_second_professor(self):
        Professor("prof2@test.edu", "Dr. Jones", "Associate Professor",
                  "DATA201").add_new_professor()
        records = Professor("", "", "", "").load()
        self.assertEqual(len(records), 2)

    def test_03_add_duplicate_rejected(self):
        before = len(Professor("", "", "", "").load())
        Professor("prof1@test.edu", "Duplicate", "Assistant",
                  "DATA200").add_new_professor()
        after = len(Professor("", "", "", "").load())
        self.assertEqual(before, after,
                         "Duplicate professor ID should be rejected.")

    def test_04_add_empty_id_rejected(self):
        before = len(Professor("", "", "", "").load())
        Professor("", "No ID Prof", "Junior", "DATA200").add_new_professor()
        after = len(Professor("", "", "", "").load())
        self.assertEqual(before, after)

    def test_05_modify_professor_name(self):
        Professor("prof1@test.edu", "", "", "").modify_professor_details(
            professor_name="Dr. John Smith")
        records = Professor("", "", "", "").load()
        match = next(
            (r for r in records if r["Professor_id"] == "prof1@test.edu"), None)
        self.assertIsNotNone(match)
        self.assertEqual(match["Professor_Name"], "Dr. John Smith")

    def test_06_modify_professor_rank(self):
        Professor("prof1@test.edu", "", "", "").modify_professor_details(
            rank="Distinguished Professor")
        records = Professor("", "", "", "").load()
        match = next(
            (r for r in records if r["Professor_id"] == "prof1@test.edu"), None)
        self.assertIsNotNone(match)
        self.assertEqual(match["Rank"], "Distinguished Professor")

    def test_07_modify_professor_course(self):
        Professor("prof1@test.edu", "", "", "").modify_professor_details(
            course_id="DATA202")
        records = Professor("", "", "", "").load()
        match = next(
            (r for r in records if r["Professor_id"] == "prof1@test.edu"), None)
        self.assertIsNotNone(match)
        self.assertEqual(match["Course_id"], "DATA202")

    def test_08_modify_nonexistent_professor(self):
        before = len(Professor("", "", "", "").load())
        Professor("ghost@test.edu", "", "", "").modify_professor_details(
            rank="Ghost")
        after = len(Professor("", "", "", "").load())
        self.assertEqual(before, after)

    def test_09_delete_professor(self):
        before = len(Professor("", "", "", "").load())
        Professor("prof1@test.edu", "", "", "").delete_professore()
        after = len(Professor("", "", "", "").load())
        self.assertEqual(after, before - 1)
        records = Professor("", "", "", "").load()
        self.assertFalse(
            any(r["Professor_id"] == "prof1@test.edu" for r in records))

    def test_10_delete_nonexistent_professor(self):
        before = len(Professor("", "", "", "").load())
        Professor("nobody@test.edu", "", "", "").delete_professore()
        after = len(Professor("", "", "", "").load())
        self.assertEqual(before, after)


class TestLoginUser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _patch_csvs()
        _cleanup()

    @classmethod
    def tearDownClass(cls):
        _cleanup()

    def test_01_register_valid_admin(self):
        result = LoginUser("admin@test.edu", "Admin@1234", "admin").register()
        self.assertTrue(result)
        records = LoginUser("", "", "").load()
        self.assertTrue(
            any(r["User_id"] == "admin@test.edu" for r in records))

    def test_02_register_valid_student(self):
        result = LoginUser("student@test.edu", "Student@99", "student").register()
        self.assertTrue(result)

    def test_03_register_valid_professor(self):
        result = LoginUser("prof@test.edu", "Prof@2026!", "professor").register()
        self.assertTrue(result)

    def test_04_register_duplicate_rejected(self):
        result = LoginUser("admin@test.edu", "Admin@1234", "admin").register()
        self.assertFalse(result, "Duplicate user_id should be rejected.")

    def test_05_register_weak_password_rejected(self):
        for weak_pwd in ["password", "Password1", "Admin1234", "short@1A"]:
            LoginUser(f"user_{weak_pwd}@test.edu", weak_pwd, "student").register()
        result = LoginUser("weak@test.edu", "password", "student").register()
        self.assertFalse(result, "All-lowercase password should be rejected.")

    def test_06_register_invalid_role_rejected(self):
        result = LoginUser("role@test.edu", "Admin@1234", "superuser").register()
        self.assertFalse(result, "Invalid role should be rejected.")

    def test_07_register_empty_fields_rejected(self):
        self.assertFalse(LoginUser("", "Admin@1234", "admin").register())
        self.assertFalse(LoginUser("nopass@test.edu", "", "admin").register())

    def test_08_login_success(self):
        user = LoginUser("admin@test.edu", "Admin@1234", "")
        self.assertTrue(user.Login())
        self.assertTrue(user.is_logged_in)
        self.assertEqual(user.role, "admin")

    def test_09_login_wrong_password(self):
        user = LoginUser("admin@test.edu", "WrongPass@1", "")
        self.assertFalse(user.Login())
        self.assertFalse(user.is_logged_in)

    def test_10_login_nonexistent_user(self):
        user = LoginUser("ghost@test.edu", "Admin@1234", "")
        self.assertFalse(user.Login())

    def test_11_logout(self):
        user = LoginUser("admin@test.edu", "Admin@1234", "")
        user.Login()
        self.assertTrue(user.is_logged_in)
        user.Logout()
        self.assertFalse(user.is_logged_in)

    def test_12_logout_without_login(self):
        user = LoginUser("admin@test.edu", "Admin@1234", "")
        try:
            user.Logout()
        except Exception as e:
            self.fail(f"Logout raised an exception: {e}")

    def test_13_change_password_success(self):
        LoginUser("admin@test.edu", "Admin@1234", "").Change_password(
            "Admin@1234", "NewPass@99")
        user = LoginUser("admin@test.edu", "NewPass@99", "")
        self.assertTrue(user.Login())

    def test_14_change_password_wrong_old(self):
        LoginUser("admin@test.edu", "NewPass@99", "").Change_password(
            "WrongOld@1", "Another@55")
        user = LoginUser("admin@test.edu", "Another@55", "")
        self.assertFalse(user.Login())

    def test_15_change_password_weak_rejected(self):
        LoginUser("admin@test.edu", "NewPass@99", "").Change_password(
            "NewPass@99", "weak")
        user = LoginUser("admin@test.edu", "NewPass@99", "")
        self.assertTrue(user.Login())

    def test_16_encrypt_decrypt_roundtrip(self):
        u         = LoginUser("x", "TestPass@1", "student")
        encrypted = u.Encrypt_password("TestPass@1")
        self.assertNotEqual(encrypted, "TestPass@1",
                            "Password must not be stored in plaintext.")
        decrypted = u.decrypt_password(encrypted)
        self.assertEqual(decrypted, "TestPass@1",
                         "Decrypt(Encrypt(p)) must equal original password.")

    def test_17_password_stored_encrypted_in_csv(self):
        records = LoginUser("", "", "").load()
        match = next(
            (r for r in records if r["User_id"] == "student@test.edu"), None)
        self.assertIsNotNone(match)
        self.assertNotEqual(match["Password"], "Student@99",
                            "CSV must not contain plaintext password.")

    def test_18_get_role(self):
        role = LoginUser("prof@test.edu", "", "").get_role()
        self.assertEqual(role, "professor")


if __name__ == "__main__":
    unittest.main(verbosity=2)
