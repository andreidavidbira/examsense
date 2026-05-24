from rest_framework import serializers


# definim forma unui concept la care utilizatorul greseste frecvent
class WeakConceptSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()
    document_id = serializers.IntegerField(allow_null=True, required=False)
    document_file = serializers.CharField(allow_null=True, required=False)
    user_document_number = serializers.IntegerField(allow_null=True, required=False)


# definim forma unei recomandari generate pe baza conceptelor slabe
class RecommendationSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()
    recommendation = serializers.CharField()
    document_id = serializers.IntegerField(allow_null=True, required=False)
    document_file = serializers.CharField(allow_null=True, required=False)
    user_document_number = serializers.IntegerField(allow_null=True, required=False)


# serializam attempturile recente care apar in dashboard
class RecentAttemptSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    user_attempt_number = serializers.IntegerField()
    document_id = serializers.IntegerField()
    user_document_number = serializers.IntegerField()
    document_file = serializers.CharField(allow_null=True, required=False)
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    completed_at = serializers.DateTimeField()


# definim structura completa pentru dashboardul de learning
class LearningDashboardSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    average_score = serializers.FloatField()
    best_score = serializers.IntegerField()
    worst_score = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    weak_concepts = WeakConceptSerializer(many=True)
    recent_attempts = RecentAttemptSerializer(many=True)


# definim forma unei intrebari din quiz-ul de recapitulare
class RetryQuizQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question_type = serializers.CharField()
    language = serializers.CharField()
    question_text = serializers.CharField()
    options = serializers.JSONField(allow_null=True, required=False)
    correct_answer = serializers.CharField()


# definim raspunsul complet pentru quiz-ul de recapitulare
class RetryQuizResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    questions = RetryQuizQuestionSerializer(many=True)
    message = serializers.CharField(required=False, allow_blank=True)