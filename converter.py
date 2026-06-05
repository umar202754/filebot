import os
import subprocess
from pathlib import Path
from PIL import Image
import tempfile

TEMP_DIR = tempfile.gettempdir()

def pdf_to_docx(input_path: str) -> str:
    from pdf2docx import Converter
    output_path = input_path.replace(".pdf", "_converted.docx")
    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()
    return output_path

def docx_to_pdf(input_path: str) -> str:
    output_dir = os.path.dirname(input_path)
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "pdf",
        "--outdir", output_dir, input_path
    ], check=True, capture_output=True)
    output_path = input_path.replace(".docx", ".pdf").replace(".doc", ".pdf")
    return output_path

def image_to_pdf(input_path: str) -> str:
    output_path = input_path.rsplit(".", 1)[0] + "_converted.pdf"
    img = Image.open(input_path).convert("RGB")
    img.save(output_path, "PDF")
    return output_path

def pdf_to_image(input_path: str) -> str:
    import fitz  # PyMuPDF
    output_path = input_path.replace(".pdf", "_page1.jpg")
    doc = fitz.open(input_path)
    page = doc[0]
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)
    pix.save(output_path)
    doc.close()
    return output_path

def excel_to_pdf(input_path: str) -> str:
    output_dir = os.path.dirname(input_path)
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "pdf",
        "--outdir", output_dir, input_path
    ], check=True, capture_output=True)
    output_path = input_path.replace(".xlsx", ".pdf").replace(".xls", ".pdf")
    return output_path

def detect_conversion(filename: str, mime_type: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return "pdf_to_docx"
    elif name.endswith(".docx") or name.endswith(".doc"):
        return "docx_to_pdf"
    elif name.endswith((".jpg", ".jpeg", ".png", ".webp")):
        return "image_to_pdf"
    elif name.endswith((".xlsx", ".xls")):
        return "excel_to_pdf"
    elif mime_type and "image" in mime_type:
        return "image_to_pdf"
    return None

def run_conversion(conv_type: str, input_path: str) -> str:
    if conv_type == "pdf_to_docx":
        return pdf_to_docx(input_path)
    elif conv_type == "docx_to_pdf":
        return docx_to_pdf(input_path)
    elif conv_type == "image_to_pdf":
        return image_to_pdf(input_path)
    elif conv_type == "pdf_to_image":
        return pdf_to_image(input_path)
    elif conv_type == "excel_to_pdf":
        return excel_to_pdf(input_path)
    raise ValueError(f"Noma'lum konversiya: {conv_type}")
