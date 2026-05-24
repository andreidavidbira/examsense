from rest_framework import serializers

from .models import (
    Document,
    ExtractedDefinition,
    GeneratedQuestion,
    QuizAttempt,
    QuizAnswer
)


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
            "created_at"
        ]


class GeneratedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedQuestion
        fields = [
            "id",
            "question_type",
            "language",
            "question_text",
            "options",
            "correct_answer",
            "created_at"
        ]


class QuizAnswerSerializer(serializers.ModelSerializer):
    question = GeneratedQuestionSerializer(read_only=True)

    class Meta:
        model = QuizAnswer
        fields = [
            "id",
            "question",
            "selected_answer",
            "is_correct"
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    document_file = serializers.SerializerMethodField()
    user_document_number = serializers.SerializerMethodField()
    user_attempt_number = serializers.SerializerMethodField()
    answers = QuizAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "user_attempt_number",
            "document",
            "document_file",
            "user_document_number",
            "score",
            "total_questions",
            "completed_at",
            "answers"
        ]

    def get_document_file(self, obj):
        if obj.document and obj.document.file:
            return obj.document.file.url
        return None

    def get_user_document_number(self, obj):
        if not obj.document:
            return None

        return (
            Document.objects
            .filter(user=obj.document.user, id__lte=obj.document.id)
            .count()
        )

    def get_user_attempt_number(self, obj):
        return (
            QuizAttempt.objects
            .filter(user=obj.user, id__lte=obj.id)
            .count()
        )


class DocumentListSerializer(serializers.ModelSerializer):
    user_document_number = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "user_document_number",
            "file",
            "uploaded_at"
        ]

    def get_user_document_number(self, obj):
        return (
            Document.objects
            .filter(user=obj.user, id__lte=obj.id)
            .count()
        )


class DocumentDetailSerializer(serializers.ModelSerializer):
    definitions = ExtractedDefinitionSerializer(many=True, read_only=True)
    generated_questions = GeneratedQuestionSerializer(many=True, read_only=True)
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
            "generated_questions"
        ]

    def get_user_document_number(self, obj):
        return (
            Document.objects
            .filter(user=obj.user, id__lte=obj.id)
            .count()
        )


class SubmitQuizAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_answer = serializers.JSONField()


class SubmitQuizInputSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    answers = SubmitQuizAnswerInputSerializer(many=True)


class SubmitQuizResultItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question = serializers.CharField()
    selected_answer = serializers.JSONField()
    correct_answer = serializers.CharField()
    is_correct = serializers.BooleanField()


class SubmitQuizResponseSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    user_attempt_number = serializers.IntegerField()
    document_id = serializers.IntegerField()
    user_document_number = serializers.IntegerField()
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    results = SubmitQuizResultItemSerializer(many=True)


class QuizStatsConceptSerializer(serializers.Serializer):
    concept = serializers.CharField()
    wrong_count = serializers.IntegerField()


class QuizStatsResponseSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    total_answers = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    wrong_answers = serializers.IntegerField()
    average_score = serializers.FloatField()
    best_score = serializers.IntegerField()
    worst_score = serializers.IntegerField()
    most_wrong_concepts = QuizStatsConceptSerializer(many=True)