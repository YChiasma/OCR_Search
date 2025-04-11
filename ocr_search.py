import os
import json
import threading
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QLineEdit, QTextBrowser
import pytesseract
from PIL import Image

CACHE_FILE = "ocr_cache.json"

class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cache = self.load_cache()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Select a folder to process images:")
        layout.addWidget(self.label)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_button)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search extracted text...")
        layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_text)
        layout.addWidget(self.search_button)

        self.result_display = QTextBrowser()
        layout.addWidget(self.result_display)

        self.setLayout(layout)
        self.setWindowTitle("OCR Image Processor")

    def load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=4)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.process_folder(folder)

    def process_folder(self, folder):
        def run():
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath) and filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    if filename not in self.cache:
                        text = self.perform_ocr(filepath)
                        self.cache[filename] = text
                        self.save_cache()
            self.label.setText("Processing Complete!")
        threading.Thread(target=run).start()

    def perform_ocr(self, image_path):
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"Error processing {image_path}: {e}"

    def search_text(self):
        query = self.search_input.text().lower()
        results = [f"{fname}: {text[:200]}..." for fname, text in self.cache.items() if query in text.lower()]
        self.result_display.setText("\n".join(results) if results else "No matches found.")

if __name__ == "__main__":
    app = QApplication([])
    window = OCRApp()
    window.show()
    app.exec()
