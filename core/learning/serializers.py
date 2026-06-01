from rest_framework import serializers


class WeakConceptSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()
    document_id = serializers.IntegerField(allow_null=True, required=False)
    document_file = serializers.CharField(allow_null=True, required=False)
    user_document_number = serializers.IntegerField(allow_null=True, required=False)


class RecommendationSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()
    recommendation = serializers.CharField()
    document_id = serializers.IntegerField(allow_null=True, required=False)
    document_file = serializers.CharField(allow_null=True, required=False)
    user_document_number = serializers.IntegerField(allow_null=True, required=False)


class RecentAttemptSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    question_set_id = serializers.IntegerField()
    generation_mode = serializers.CharField()
    user_attempt_number = serializers.IntegerField()
    document_id = serializers.IntegerField()
    user_document_number = serializers.IntegerField()
    document_file = serializers.CharField(allow_null=True, required=False)
    score = serializers.IntegerField()
    ai_score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    completed_at = serializers.DateTimeField()


class ModeStatsSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    average_score = serializers.FloatField()
    best_score = serializers.IntegerField()
    worst_score = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    ai_average_score = serializers.FloatField()
    ai_best_score = serializers.IntegerField()
    ai_wins = serializers.IntegerField()
    user_wins = serializers.IntegerField()
    ties = serializers.IntegerField()


class LearningDashboardSerializer(serializers.Serializer):
    overall = ModeStatsSerializer()
    nlp = ModeStatsSerializer()
    ai = ModeStatsSerializer()
    weak_concepts = WeakConceptSerializer(many=True)
    recent_attempts = RecentAttemptSerializer(many=True)


class RetryQuizQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question_set_id = serializers.IntegerField()
    generation_mode = serializers.CharField()
    question_type = serializers.CharField()
    language = serializers.CharField()
    question_text = serializers.CharField()
    options = serializers.JSONField(allow_null=True, required=False)
    correct_answer = serializers.CharField()


class RetryQuizResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    questions = RetryQuizQuestionSerializer(many=True)
    message = serializers.CharField(required=False, allow_blank=True)