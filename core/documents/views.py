from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Document
from .serializers import DocumentSerializer
from .utils import extract_text_from_pdf, extract_text_from_docx


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

        document.extracted_text = text
        document.save()

        return Response(DocumentSerializer(document).data)
