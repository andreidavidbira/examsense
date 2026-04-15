from django.db import models
from django.conf import settings

# model pentru documente incarcate
class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True)

    def __str__(self):
        return f"Document {self.id} - {self.user.username}"