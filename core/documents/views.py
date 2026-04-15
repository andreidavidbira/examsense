from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Document
from .utils import extract_text_from_pdf, extract_text_from_docx

# NLP pipeline nou
from nlp.services import process_text

# generator intrebari
from quiz.services import generate_questions


# upload document + procesare completa
class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided"}, status=400)

        # salvare document
        document = Document.objects.create(
            user=request.user,
            file=file
        )

        # extragere text
        if file.name.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif file.name.endswith('.docx'):
            text = extract_text_from_docx(file)
        else:
            return Response({"error": "Unsupported file type"}, status=400)

        # salvare text
        document.extracted_text = text
        document.save()

        # procesare NLP (definitii)
        result = process_text(text)
        definitions = result["definitions"]

        # dificultate (optional din request)
        difficulty = request.data.get("difficulty", "easy")

        # generare intrebari
        questions = generate_questions(definitions, difficulty=difficulty)

        return Response({
            "id": document.id,
            "file": document.file.url,
            "uploaded_at": document.uploaded_at,
            "extracted_text": text,
            "definitions": definitions,
            "questions": questions
        })