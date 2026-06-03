"""
ExamSense+ - Admin Panel Serializers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste serializer-ele folosite de panoul de administrare
- structureaza statisticile globale si individuale afisate in admin panel
- serializeaza listele de utilizatori, documente, seturi de intrebari si attempturi
- defineste structura comparatiilor dintre utilizatori si solverul AI
- valideaza schimbarea starii active / inactive pentru utilizatori
"""

from rest_framework import serializers


# grup de statistici reutilizabil pentru un anumit tip de quiz-uri sau pentru un anumit bloc
class AdminStatsBlockSerializer(serializers.Serializer):
    attempts_count = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    average_score = serializers.FloatField()
    best_score = serializers.IntegerField()
    worst_score = serializers.IntegerField()


# bloc folosit pentru comparatia dintre utilizator si AI pe un set de attempturi
class AdminUserVsAiBlockSerializer(serializers.Serializer):
    compared_attempts = serializers.IntegerField()
    user_wins = serializers.IntegerField()
    ai_wins = serializers.IntegerField()
    draws = serializers.IntegerField()


# concept la care s-a gresit frecvent, folosit in dashboardurile de analiza
class AdminWrongConceptSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()


# statistici generale afisate in partea de overview din admin panel
class AdminOverviewSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    staff_users = serializers.IntegerField()
    total_documents = serializers.IntegerField()
    total_question_sets = serializers.IntegerField()
    total_definitions = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    total_attempts = serializers.IntegerField()
    total_answers = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    average_score = serializers.FloatField()
    nlp_attempts = serializers.IntegerField()
    ai_attempts = serializers.IntegerField()
    nlp_average_score = serializers.FloatField()
    ai_average_score = serializers.FloatField()


# statistici globale pentru solverul AI, separate pe overall / nlp / ai
class AdminAiOverviewSerializer(serializers.Serializer):
    overall = AdminStatsBlockSerializer()
    nlp = AdminStatsBlockSerializer()
    ai = AdminStatsBlockSerializer()


# serializer pentru lista de utilizatori afisata in admin panel
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
    question_sets_count = serializers.IntegerField()
    attempts_count = serializers.IntegerField()
    average_score = serializers.FloatField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()


# date de identificare pentru un utilizator, folosite in dashboardul detaliat
class AdminUserIdentitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    date_joined = serializers.DateTimeField()


# ultimele attempturi ale unui utilizator, folosite in dashboardul sau din admin
class AdminRecentAttemptSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question_set_id = serializers.IntegerField()
    generation_mode = serializers.CharField()
    difficulty = serializers.CharField()
    user_attempt_number = serializers.IntegerField()
    user_document_number = serializers.IntegerField()
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    completed_at = serializers.DateTimeField()


# dashboardul complet pentru un utilizator selectat din admin panel
class AdminUserDetailSerializer(serializers.Serializer):
    user = AdminUserIdentitySerializer()
    documents_count = serializers.IntegerField()
    question_sets_count = serializers.IntegerField()
    definitions_count = serializers.IntegerField()
    questions_count = serializers.IntegerField()

    overall = AdminStatsBlockSerializer()
    nlp = AdminStatsBlockSerializer()
    ai = AdminStatsBlockSerializer()

    ai_solver_overall = AdminStatsBlockSerializer()
    ai_solver_nlp = AdminStatsBlockSerializer()
    ai_solver_ai = AdminStatsBlockSerializer()

    user_vs_ai_overall = AdminUserVsAiBlockSerializer()
    user_vs_ai_nlp = AdminUserVsAiBlockSerializer()
    user_vs_ai_ai = AdminUserVsAiBlockSerializer()

    most_wrong_concepts = AdminWrongConceptSerializer(many=True)
    recent_attempts = AdminRecentAttemptSerializer(many=True)


# serializer pentru lista de documente din panoul de administrare
class AdminDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    user_document_number = serializers.IntegerField()
    file = serializers.CharField()
    uploaded_at = serializers.DateTimeField()
    definitions_count = serializers.IntegerField()
    nlp_definitions_count = serializers.IntegerField()
    ai_definitions_count = serializers.IntegerField()
    questions_count = serializers.IntegerField()
    question_sets_count = serializers.IntegerField()


# serializer pentru seturile de intrebari generate in platforma
class AdminQuestionSetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    document_id = serializers.IntegerField()
    username = serializers.CharField()
    generation_mode = serializers.CharField()
    difficulty = serializers.CharField()
    max_questions = serializers.IntegerField()
    questions_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


# serializer pentru istoricul global al attempturilor din admin
class AdminAttemptSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    user_attempt_number = serializers.IntegerField()
    user_document_number = serializers.IntegerField()
    question_set_id = serializers.IntegerField(allow_null=True)
    generation_mode = serializers.CharField()
    difficulty = serializers.CharField()
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    ai_score = serializers.IntegerField(allow_null=True, required=False)
    time_spent_seconds = serializers.IntegerField(required=False)
    ai_time_spent_seconds = serializers.IntegerField(required=False)
    completed_at = serializers.DateTimeField()


# valideaza schimbarea starii active / inactive pentru un utilizator
class ToggleUserActiveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()