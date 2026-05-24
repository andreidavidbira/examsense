from rest_framework import serializers


class WeakConceptSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()
    document_id = serializers.IntegerField(required=False, allow_null=True)
    document_file = serializers.CharField(required=False, allow_null=True)


class DashboardRecentAttemptSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    document_id = serializers.IntegerField()
    document_file = serializers.CharField(allow_null=True)
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    completed_at = serializers.DateTimeField()


class LearningDashboardSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    average_score = serializers.FloatField()
    best_score = serializers.IntegerField()
    worst_score = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    weak_concepts = WeakConceptSerializer(many=True)
    recent_attempts = DashboardRecentAttemptSerializer(many=True)


class RecommendationSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()
    recommendation = serializers.CharField()
    document_id = serializers.IntegerField(required=False, allow_null=True)
    document_file = serializers.CharField(required=False, allow_null=True)


class RetryQuizQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question_type = serializers.CharField()
    language = serializers.CharField()
    question_text = serializers.CharField()
    options = serializers.JSONField(required=False, allow_null=True)
    correct_answer = serializers.CharField()


class RetryQuizResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    questions = RetryQuizQuestionSerializer(many=True)