from rest_framework import serializers


# statistici simple reutilizabile pentru o categorie de quiz-uri
class AdminStatsBlockSerializer(serializers.Serializer):
    attempts_count = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    average_score = serializers.FloatField()
    best_score = serializers.IntegerField()
    worst_score = serializers.IntegerField()


# comparatie user vs ai pentru un set de quiz-uri
class AdminUserVsAiBlockSerializer(serializers.Serializer):
    compared_attempts = serializers.IntegerField()
    user_wins = serializers.IntegerField()
    ai_wins = serializers.IntegerField()
    draws = serializers.IntegerField()


# concept la care s-a gresit frecvent
class AdminWrongConceptSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()


# statistici generale pentru dashboardul de admin
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


# statistici globale pentru solverul AI
class AdminAiOverviewSerializer(serializers.Serializer):
    overall = AdminStatsBlockSerializer()
    nlp = AdminStatsBlockSerializer()
    ai = AdminStatsBlockSerializer()


# lista de utilizatori din panoul de admin
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


# date simple despre utilizator, folosite in dashboardul detaliat
class AdminUserIdentitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    date_joined = serializers.DateTimeField()


# attempt recent din dashboardul unui user
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


# dashboard complet pentru un utilizator
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


# lista de documente din panoul de admin
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


# lista de seturi de intrebari generate
class AdminQuestionSetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    document_id = serializers.IntegerField()
    username = serializers.CharField()
    generation_mode = serializers.CharField()
    difficulty = serializers.CharField()
    max_questions = serializers.IntegerField()
    questions_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


# istoricul global al attempturilor
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


# validarea starii active / inactive pentru user
class ToggleUserActiveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()