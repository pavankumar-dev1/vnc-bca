import csv
import io
import unittest

from app import create_app, models
from config import TestingConfig


class CsvFormulaEscapingTests(unittest.TestCase):
    def test_formula_and_control_character_prefixes_are_escaped(self):
        dangerous_values = (
            "=1+1",
            "+SUM(1,2)",
            "-1+2",
            "@SUM(A1:A2)",
            "\\t=1+1",
            "\\r=1+1",
            "\\n=1+1",
            "  =1+1",
        )

        from app.routes.admin import _escape_csv_row

        for value in dangerous_values:
            with self.subTest(value=repr(value)):
                self.assertEqual(_escape_csv_row({"cell": value})["cell"], "'" + value)

    def test_safe_text_and_non_string_values_are_unchanged(self):
        from app.routes.admin import _escape_csv_row

        row = {
            "name": "Professor Pavan",
            "display_order": -1,
            "is_leadership": False,
        }
        self.assertEqual(_escape_csv_row(row), row)


class CsvExportRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        with self.client.session_transaction() as session:
            session["logged_in"] = True
            session["admin_username"] = "test-admin"
            session["role"] = "admin"

    def _read_rows(self, response):
        self.assertEqual(response.status_code, 200)
        return list(csv.DictReader(io.StringIO(response.get_data(as_text=True))))

    def test_faculty_export_escapes_formula_in_user_supplied_name(self):
        formula_name = '=HYPERLINK("https://example.invalid","Open")'
        with self.app.app_context():
            models.db.session.add(models.Faculty(
                name=formula_name,
                department="BCA",
                designation="Lecturer",
                qualification="MCA",
                email="",
                phone="",
                display_order=0,
                is_leadership=False,
            ))
            models.db.session.commit()

        rows = self._read_rows(self.client.get("/admin/faculty/export.csv"))
        exported = next(row for row in rows if row["department"] == "BCA" and row["qualification"] == "MCA")
        self.assertEqual(exported["name"], "'" + formula_name)

    def test_notice_export_escapes_formula_after_leading_tab(self):
        formula_description = "\\t=HYPERLINK(\"https://example.invalid\",\"Open\")"
        with self.app.app_context():
            models.db.session.add(models.Notice(
                title="CSV safety test",
                description=formula_description,
            ))
            models.db.session.commit()

        rows = self._read_rows(self.client.get("/admin/notices/export.csv"))
        exported = next(row for row in rows if row["title"] == "CSV safety test")
        self.assertEqual(exported["description"], "'" + formula_description)


if __test__ == "__main__":
    unittest.main()
