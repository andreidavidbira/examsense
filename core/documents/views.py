from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Document, ExtractedDefinition, GeneratedQuestion
from .utils import extract_text_from_pdf, extract_text_from_docx

from nlp.services import process_text
from quiz.services import generate_questions


class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=400)

        filename = file.name.lower()

        if not (filename.endswith(".pdf") or filename.endswith(".docx")):
            return Response({"error": "Unsupported file type"}, status=400)

        # salvare document
        document = Document.objects.create(
            user=request.user,
            file=file
        )

        # extragere text
        try:
            if filename.endswith(".pdf"):
                text = extract_text_from_pdf(file)
            else:
                text = extract_text_from_docx(file)
        except Exception as e:
            return Response({
                "error": "Eroare la extragerea textului",
                "details": str(e)
            }, status=500)

        # limitare text
        max_length = 100000
        if len(text) > max_length:
            text = text[:max_length]

        # salvare text extras
        document.extracted_text = text
        document.save()

        # procesare NLP
        try:
            result = process_text(text)
            definitions = result.get("definitions", [])
            definitions_ro = result.get("definitions_ro", [])
            definitions_en = result.get("definitions_en", [])
        except Exception as e:
            return Response({
                "error": "Eroare la procesarea textului",
                "details": str(e)
            }, status=500)

        # stergere eventuale definitii vechi pentru document
        ExtractedDefinition.objects.filter(document=document).delete()

        saved_definitions = []

        # salvare definitii
        for d in definitions:
            db_definition = ExtractedDefinition.objects.create(
                document=document,
                concept=d.get("concept", ""),
                definition=d.get("definition", ""),
                pattern=d.get("pattern", ""),
                language=d.get("language", ""),
                sentence=d.get("sentence", "")
            )
            saved_definitions.append(db_definition)

        # generare intrebari
        try:
            difficulty = request.data.get("difficulty", "medium")
            max_q = int(request.data.get("max_questions", 10))

            questions = generate_questions(
                definitions,
                difficulty=difficulty,
                max_questions=max_q
            )
        except Exception as e:
            return Response({
                "error": "Eroare la generarea intrebarilor",
                "details": str(e)
            }, status=500)

        # stergere eventuale intrebari vechi pentru document
        GeneratedQuestion.objects.filter(document=document).delete()

        # mapare definitii salvate pentru legatura cu intrebarile
        definition_map = {}

        for db_def in saved_definitions:
            key = (db_def.concept, db_def.definition, db_def.language)
            definition_map[key] = db_def

        # salvare intrebari
        for q in questions:
            source_definition_obj = None

            if q.get("type") == "mcq":
                for d in definitions:
                    if (
                        d.get("definition") == q.get("correct_answer") and
                        d.get("language") == q.get("language")
                    ):
                        key = (
                            d.get("concept"),
                            d.get("definition"),
                            d.get("language")
                        )
                        source_definition_obj = definition_map.get(key)
                        break

            elif q.get("type") == "mcq_reverse":
                for d in definitions:
                    if (
                        d.get("concept", "").lower() == str(q.get("correct_answer", "")).lower() and
                        d.get("language") == q.get("language")
                    ):
                        key = (
                            d.get("concept"),
                            d.get("definition"),
                            d.get("language")
                        )
                        source_definition_obj = definition_map.get(key)
                        break

            GeneratedQuestion.objects.create(
                document=document,
                source_definition=source_definition_obj,
                question_type=q.get("type"),
                language=q.get("language"),
                question_text=q.get("question"),
                options=q.get("options", None),
                correct_answer=str(q.get("correct_answer"))
            )

        response_data = {
            "id": document.id,
            "file": document.file.url,
            "uploaded_at": document.uploaded_at,
            "definitions": definitions,
            "definitions_ro": definitions_ro,
            "definitions_en": definitions_en,
            "questions": questions
        }

        if not definitions:
            response_data["warning"] = "Nu s-au putut extrage suficiente definitii relevante din document"

        return Response(response_data)