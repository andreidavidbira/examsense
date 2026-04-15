from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Document
from .utils import extract_text_from_pdf, extract_text_from_docx

from nlp.services import process_text
from quiz.services import generate_questions


class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided"}, status=400)

        filename = file.name.lower()

        # salvare document
        document = Document.objects.create(
            user=request.user,
            file=file
        )

        # extragere text
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        else:
            return Response({"error": "Unsupported file type"}, status=400)

        # limitare text (protectie)
        MAX_LENGTH = 100000
        if len(text) > MAX_LENGTH:
            text = text[:MAX_LENGTH]

        # salvare text
        document.extracted_text = text
        document.save()

        # procesare NLP
        try:
            result = process_text(text)
            definitions = result["definitions"]
        except Exception as e:
            return Response({
                "error": "Eroare la procesarea textului",
                "details": str(e)
            }, status=500)

        if not definitions:
            return Response({
                "error": "Nu s-au putut extrage definitii din document"
            }, status=400)

        # dificultate
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