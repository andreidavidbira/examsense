"""
ExamSense+ - Documents Serializers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste serializer-ele pentru documente, intrebari, attempturi si statistici
- transforma modelele din baza de date in raspunsuri JSON pentru frontend
- valideaza datele primite la submit-ul quiz-urilor
- structureaza raspunsurile pentru istoric, detalii document si comparatia User vs AI
"""

from rest_framework import serializers

from .models import (
    AIQuizAnswer,
    AIQuizAttempt,
    Document,
    ExtractedDefinition,
    GeneratedQuestion,
    QuestionSet,
    QuizAnswer,
    QuizAttempt,
)


# serializer pentru definitiile extrase dintr-un document
class ExtractedDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedDefinition
        fields = [
            "id",
            "concept",
            "definition",
            "pattern",
            "language",
            "sentence",
            "generation_mode",
            "created_at",
        ]


# serializer pentru intrebarile generate, inclusiv referinta la question set
class GeneratedQuestionSerializer(serializers.ModelSerializer):
    question_set_id = serializers.IntegerField(source="question_set.id", read_only=True)

    class Meta:
        model = GeneratedQuestion
        fields = [
            "id",
            "question_set_id",
            "generation_mode",
            "question_type",
            "language",
            "question_text",
            "options",
            "correct_answer",
            "created_at",
        ]


# serializer pentru un set de intrebari generate pentru un document
class QuestionSetSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = QuestionSet
        fields = [
            "id",
            "generation_mode",
            "difficulty",
            "max_questions",
            "questions_count",
            "created_at",
        ]

    def get_questions_count(self, obj):
        annotated_value = getattr(obj, "questions_count", None)

        if annotated_value is not None:
            return annotated_value

        return obj.questions.count()


# serializer pentru raspunsurile date de utilizator intr-un quiz
class QuizAnswerSerializer(serializers.ModelSerializer):
    question = GeneratedQuestionSerializer(read_only=True)

    class Meta:
        model = QuizAnswer
        fields = [
            "id",
            "question",
            "selected_answer",
            "is_correct",
        ]


# serializer pentru raspunsurile date de solverul AI
class AIQuizAnswerSerializer(serializers.ModelSerializer):
    question = GeneratedQuestionSerializer(read_only=True)

    class Meta:
        model = AIQuizAnswer
        fields = [
            "id",
            "question",
            "selected_answer",
            "is_correct",
        ]


# serializer pentru attemptul AI asociat unui quiz rezolvat de user
class AIQuizAttemptSerializer(serializers.ModelSerializer):
    answers = AIQuizAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = AIQuizAttempt
        fields = [
            "id",
            "model_name",
            "score",
            "total_questions",
            "time_spent_seconds",
            "completed_at",
            "answers",
        ]


# serializer simplu pentru attemptul AI din lista de istoric
# nu includem raspunsurile, ca lista sa ramana rapida
class AIQuizAttemptListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIQuizAttempt
        fields = [
            "id",
            "model_name",
            "score",
            "total_questions",
            "time_spent_seconds",
            "completed_at",
        ]


# serializer complet pentru un attempt al utilizatorului, inclusiv date despre AI
class QuizAttemptSerializer(serializers.ModelSerializer):
    document_file = serializers.SerializerMethodField()
    user_document_number = serializers.SerializerMethodField()
    user_attempt_number = serializers.SerializerMethodField()
    generation_mode = serializers.CharField(source="question_set.generation_mode", read_only=True)
    question_set_id = serializers.IntegerField(source="question_set.id", read_only=True)
    answers = QuizAnswerSerializer(many=True, read_only=True)
    ai_attempt = AIQuizAttemptSerializer(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "question_set_id",
            "generation_mode",
            "user_attempt_number",
            "document",
            "document_file",
            "user_document_number",
            "score",
            "total_questions",
            "time_spent_seconds",
            "completed_at",
            "answers",
            "ai_attempt",
        ]

    def get_document_file(self, obj):
        if obj.document and obj.document.file:
            return obj.document.file.url
        return None

    def get_user_document_number(self, obj):
        annotated_value = getattr(obj, "user_document_number", None)

        if annotated_value is not None:
            return annotated_value

        if not obj.document:
            return None

        return (
            Document.objects
            .filter(user=obj.document.user, id__lte=obj.document.id)
            .count()
        )

    def get_user_attempt_number(self, obj):
        annotated_value = getattr(obj, "user_attempt_number", None)

        if annotated_value is not None:
            return annotated_value

        return (
            QuizAttempt.objects
            .filter(user=obj.user, id__lte=obj.id)
            .count()
        )


# serializer rapid pentru lista de istoric quiz
# nu include answers si nici answers AI, deoarece acestea se incarca doar in pagina de detalii
class QuizAttemptListSerializer(serializers.ModelSerializer):
    document_file = serializers.SerializerMethodField()
    user_document_number = serializers.SerializerMethodField()
    user_attempt_number = serializers.SerializerMethodField()
    generation_mode = serializers.CharField(source="question_set.generation_mode", read_only=True)
    question_set_id = serializers.IntegerField(source="question_set.id", read_only=True)
    ai_attempt = AIQuizAttemptListSerializer(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "question_set_id",
            "generation_mode",
            "user_attempt_number",
            "document",
            "document_file",
            "user_document_number",
            "score",
            "total_questions",
            "time_spent_seconds",
            "completed_at",
            "ai_attempt",
        ]

    def get_document_file(self, obj):
        if obj.document and obj.document.file:
            return obj.document.file.url
        return None

    def get_user_document_number(self, obj):
        annotated_value = getattr(obj, "user_document_number", None)

        if annotated_value is not None:
            return annotated_value

        if not obj.document:
            return None

        return (
            Document.objects
            .filter(user=obj.document.user, id__lte=obj.document.id)
            .count()
        )

    def get_user_attempt_number(self, obj):
        annotated_value = getattr(obj, "user_attempt_number", None)

        if annotated_value is not None:
            return annotated_value

        return (
            QuizAttempt.objects
            .filter(user=obj.user, id__lte=obj.id)
            .count()
        )


# serializer simplu pentru lista documentelor utilizatorului
class DocumentListSerializer(serializers.ModelSerializer):
    user_document_number = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "user_document_number",
            "file",
            "uploaded_at",
        ]

    def get_user_document_number(self, obj):
        annotated_value = getattr(obj, "user_document_number", None)

        if annotated_value is not None:
            return annotated_value

        return (
            Document.objects
            .filter(user=obj.user, id__lte=obj.id)
            .count()
        )


# serializer detaliat pentru un document, cu definitii, intrebari si question sets
class DocumentDetailSerializer(serializers.ModelSerializer):
    definitions = ExtractedDefinitionSerializer(many=True, read_only=True)
    generated_questions = GeneratedQuestionSerializer(many=True, read_only=True)
    question_sets = QuestionSetSerializer(many=True, read_only=True)
    latest_question_set_id = serializers.SerializerMethodField()
    user_document_number = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "user_document_number",
            "file",
            "extracted_text",
            "uploaded_at",
            "definitions",
            "generated_questions",
            "question_sets",
            "latest_question_set_id",
        ]

    def get_user_document_number(self, obj):
        annotated_value = getattr(obj, "user_document_number", None)

        if annotated_value is not None:
            return annotated_value

        return (
            Document.objects
            .filter(user=obj.user, id__lte=obj.id)
            .count()
        )

    def get_latest_question_set_id(self, obj):
        latest_set = obj.question_sets.order_by("-created_at").first()

        if not latest_set:
            return None

        return latest_set.id


# serializer pentru fiecare raspuns trimis de utilizator la submit-ul quiz-ului
class SubmitQuizAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_answer = serializers.JSONField()


# valideaza payload-ul trimis la submit-ul unui quiz
class SubmitQuizInputSerializer(serializers.Serializer):
    question_set_id = serializers.IntegerField()
    elapsed_seconds = serializers.IntegerField(required=False, min_value=0)
    answers = SubmitQuizAnswerInputSerializer(many=True)


# serializer pentru rezultatul unei intrebari rezolvate de utilizator
class SubmitQuizResultItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question = serializers.CharField()
    selected_answer = serializers.JSONField()
    correct_answer = serializers.CharField()
    is_correct = serializers.BooleanField()


# serializer pentru rezultatul aceleiasi intrebari rezolvate de solverul AI
class SubmitQuizAIResultItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question = serializers.CharField()
    ai_selected_answer = serializers.JSONField()
    correct_answer = serializers.CharField()
    is_correct = serializers.BooleanField()


# serializer pentru raspunsul complet returnat dupa submit-ul unui quiz
class SubmitQuizResponseSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    question_set_id = serializers.IntegerField()
    generation_mode = serializers.CharField()
    user_attempt_number = serializers.IntegerField()
    document_id = serializers.IntegerField()
    user_document_number = serializers.IntegerField()
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    user_time_spent_seconds = serializers.IntegerField()
    results = SubmitQuizResultItemSerializer(many=True)
    ai_score = serializers.IntegerField()
    ai_total_questions = serializers.IntegerField()
    ai_model_name = serializers.CharField()
    ai_time_spent_seconds = serializers.IntegerField()
    ai_results = SubmitQuizAIResultItemSerializer(many=True)


# concept la care utilizatorul a gresit frecvent
class QuizStatsConceptSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()


# bloc de statistici pentru overall, nlp sau ai
class ModeStatsSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    average_score = serializers.FloatField()
    best_score = serializers.IntegerField()
    worst_score = serializers.IntegerField()
    ai_average_score = serializers.FloatField()
    ai_best_score = serializers.IntegerField()
    ai_wins = serializers.IntegerField()
    user_wins = serializers.IntegerField()
    ties = serializers.IntegerField()


# serializer pentru raspunsul complet din pagina de statistici a quiz-urilor
class QuizStatsResponseSerializer(serializers.Serializer):
    overall = ModeStatsSerializer()
    nlp = ModeStatsSerializer()
    ai = ModeStatsSerializer()
    most_wrong_concepts = QuizStatsConceptSerializer(many=True)
