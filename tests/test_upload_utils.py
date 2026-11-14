import tempfile
import unittest
from pathlib import Path

from flask import Flask

from app.utils import delete_upload


class DeleteUploadTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.static_dir = self.temp_dir / "static"
        self.upload_dir = self.static_dir / "uploads"
        self.upload_dir.mkdir(parents=True)
        self.app = Flask(__name__, static_folder=str(self.static_dir))

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_deletes_file_inside_upload_directory(self):
        target = self.upload_dir / "faculty" / "portrait.jpg"
        target.parent.mkdir()
        target.write_bytes(b"image")

        with self.app.app_context():
            delete_upload("uploads/faculty/portrait.jpg")

        self.assertFalse(target.exists())

    def test_refuses_parent_directory_traversal(self):
        outside_file = self.temp_dir / "private.txt"
        outside_file.write_text("keep this file", encoding="utf-8")

        with self.app.app_context():
            delete_upload("uploads/../../private.txt")

        self.assertTrue(outside_file.exists())
        self.assertEqual(outside_file.read_text(encoding="utf-8"), "keep this file")

    def test_refuses_symlink_to_file_outside_upload_directory(self):
        outside_file = self.temp_dir / "private.txt"
        outside_file.write_text("keep this file", encoding="utf-8")
        link = self.upload_dir / "faculty" / "portrait.jpg"
        link.parent.mkdir()
        try:
            link.symlink_to(outside_file)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links are unavailable in this environment")

        with self.app.app_context():
            delete_upload("uploads/faculty/portrait.jpg")

        self.assertTrue(outside_file.exists())
        self.assertTrue(link.is_symlink())


if __name__ == "__main__":
    unittest.main()
