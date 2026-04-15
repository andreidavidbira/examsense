import PyPDF2
from docx import Document as DocxDocument

# extragere text din pdf
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


# extragere text din docx
def extract_text_from_docx(file):
    doc = DocxDocument(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text