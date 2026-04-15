from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Document
from .serializers import DocumentSerializer
from .utils import extract_text_from_pdf, extract_text_from_docx

from nlp.services import extract_concepts


# upload document + extragere text
class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided"}, status=400)

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
            text = "Unsupported file type"

        # extragere concepte
        result = extract_concepts(text)
        
        document.extracted_text = text
        document.save()

        
        return Response({
            "id": document.id,
            "file": document.file.url,
            "uploaded_at": document.uploaded_at,
            "extracted_text": text,
            "language": result["language"],
            "concepts": result["concepts"]
})
        
        
