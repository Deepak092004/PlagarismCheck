import os
from PyPDF2 import PdfReader
from docx import Document

def extract_text(file_path, extension):
    text = ""

    if extension == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    elif extension == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""

    elif extension == ".docx":
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif extension in [".py", ".java", ".c", ".cpp", ".js"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    return text
