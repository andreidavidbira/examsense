import PyPDF2
from docx import Document as DocxDocument


# extragem textul din toate paginile unui fisier pdf
def extract_text_from_pdf(file):
    try:
        file.seek(0)
        reader = PyPDF2.PdfReader(file)

        pages_text = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            page_text = page_text.strip()

            if page_text:
                pages_text.append(page_text)

        return "\n".join(pages_text)

    except Exception as e:
        raise Exception(f"Eroare la citirea PDF-ului: {str(e)}")


# extragem textul din toate paragrafele unui fisier docx
def extract_text_from_docx(file):
    try:
        file.seek(0)
        doc = DocxDocument(file)

        paragraphs = []

        for para in doc.paragraphs:
            para_text = para.text.strip()

            if para_text:
                paragraphs.append(para_text)

        return "\n".join(paragraphs)

    except Exception as e:
        raise Exception(f"Eroare la citirea DOCX-ului: {str(e)}")