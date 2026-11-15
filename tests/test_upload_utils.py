import io
import tempfile
import unittest
from pathlib import Path

from flask import Flask
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.utils import delete_upload, save_upload


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

    def _make_image_upload(self, filename, image_format):
        image_stream = io.BytesIO()
        Image.new("RGB", (2, 2), color=(255, 0, 0)).save(
            image_stream, format=image_format
        )
        image_stream.seek(0)
        return FileStorage(stream=image_stream, filename=filename)

    def test_saves_a_valid_image_matching_its_extension(self):
        upload = self._make_image_upload("portrait.png", "PNG")

        with self.app.app_context():
            stored_path = save_upload(upload, "faculty")

        self.assertTrue((self.static_dir / stored_path).is_file())

    def test_rejects_non_image_bytes_with_an_image_extension(self):
        upload = FileStorage(
            stream=io.BytesIO(b"this is not an image"),
            filename="portrait.png",
        )

        with self.app.app_context():
            with self.assertRaisesRegex(ValueError, "valid image"):
                save_upload(upload, "faculty")

        self.assertEqual(list(self.upload_dir.rglob("*")), [])

    def test_rejects_image_bytes_that_do_not_match_the_extension(self):
        upload = self._make_image_upload("portrait.png", "JPEG")

        with self.app.app_context():
            with self.assertRaisesRegex(ValueError, "do not match"):
                save_upload(upload, "faculty")

        self.assertEqual(list(self.upload_dir.rglob("*")), [])

    def test_rejects_non_pdf_bytes_with_a_pdf_extension(self):
        upload = FileStorage(
            stream=io.BytesIO(b"not a PDF document"),
            filename="notice.pdf",
        )

        with self.app.app_context():
            with self.assertRaisesRegex(ValueError, "valid PDF"):
                save_upload(upload, "notices", allowed={"pdf"})

        self.assertEqual(list(self.upload_dir.rglob("*")), [])

    def test_saves_a_pdf_with_a_pdf_header(self):
        upload = FileStorage(
            stream=io.BytesIO(b"%PDF-1.7\nminimal test document"),
            filename="notice.pdf",
        )

        with self.app.app_context():
            stored_path = save_upload(upload, "notices", allowed={"pdf"})

        self.assertTrue((self.static_dir / stored_path).is_file())


if __name__ == "__main__":
    unittest.main()
