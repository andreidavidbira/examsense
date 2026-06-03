"""
ExamSense+ - Learning Serializers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste serializer-ele pentru modulul de learning
- structureaza conceptele slabe si recomandarile de invatare
- serializeaza statisticile din dashboardul de progres
- defineste formatul quiz-ului de recapitulare si al intrebarilor trimise catre frontend
"""

from rest_framework import serializers


# serializer pentru un concept la care utilizatorul a gresit frecvent
class WeakConceptSerializer(serializers.Serializer):
    concept = serializers.CharField()
    definition = serializers.CharField(allow_blank=True, required=False)
    wrong_count = serializers.IntegerField()
    document_id = serializers.IntegerField(allow_null=True, required=False)
    document_file = serializers.CharField(allow_null=True, required=False)
    user_document_number = serializers.IntegerField(allow_null=True, required=False)


# serializer pentru o recomandare de invatare asociata unui concept slab
class RecommendationSerializer(serializers.Serializer):
    concept = serializers.CharField()
    definition = serializers.CharField(allow_blank=True, required=False)
    wrong_count = serializers.IntegerField()
    recommendation = serializers.CharField()
    document_id = serializers.IntegerField(allow_null=True, required=False)
    document_file = serializers.CharField(allow_null=True, required=False)
    user_document_number = serializers.IntegerField(allow_null=True, required=False)


# serializer pentru un attempt recent afisat in dashboardul de learning
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


# bloc de statistici pentru overall, nlp sau ai
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


# serializer complet pentru dashboardul de invatare
class LearningDashboardSerializer(serializers.Serializer):
    overall = ModeStatsSerializer()
    nlp = ModeStatsSerializer()
    ai = ModeStatsSerializer()
    weak_concepts = WeakConceptSerializer(many=True)
    recent_attempts = RecentAttemptSerializer(many=True)


# serializer pentru o intrebare din quiz-ul de recapitulare
class RetryQuizQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question_set_id = serializers.IntegerField()
    generation_mode = serializers.CharField()
    question_type = serializers.CharField()
    language = serializers.CharField()
    question_text = serializers.CharField()
    options = serializers.JSONField(allow_null=True, required=False)
    correct_answer = serializers.CharField()


# serializer pentru raspunsul complet al quiz-ului de recapitulare
class RetryQuizResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    questions = RetryQuizQuestionSerializer(many=True)
    message = serializers.CharField(required=False, allow_blank=True)