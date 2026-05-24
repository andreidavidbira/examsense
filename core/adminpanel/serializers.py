from rest_framework import serializers


# aici definim statisticile generale pe care le afisam in dashboardul de admin
class AdminOverviewSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    staff_users = serializers.IntegerField()
    total_documents = serializers.IntegerField()
    total_definitions = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    total_attempts = serializers.IntegerField()
    average_score = serializers.FloatField()


# aici pregatim datele pentru lista de utilizatori din panoul de admin
class AdminUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    date_joined = serializers.DateTimeField()
    documents_count = serializers.IntegerField()
    attempts_count = serializers.IntegerField()


# aici pregatim datele pentru lista de documente din panoul de admin
class AdminDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    user_document_number = serializers.IntegerField()
    file = serializers.CharField()
    uploaded_at = serializers.DateTimeField()
    definitions_count = serializers.IntegerField()
    questions_count = serializers.IntegerField()


# aici pregatim datele pentru istoricul global al attempturilor
class AdminAttemptSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    user_attempt_number = serializers.IntegerField()
    user_document_number = serializers.IntegerField()
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    completed_at = serializers.DateTimeField()


# aici validam noua stare activa/inactiva a unui utilizator
class ToggleUserActiveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()