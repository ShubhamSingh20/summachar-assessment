from typing import Dict, List, OrderedDict

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.forms.models import model_to_dict
from helper.validators import ExistValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from quiz.models import Question, QuestionSolution, Quiz

CollectedDict = List[OrderedDict]

get_user = lambda u : model_to_dict(u, ['username', 'emaill', 'created_at', 'updated_at'])

# create serializers here.

class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.SlugField(source='slug', required=False)
    quiz = serializers.SlugField(required=False, source='quiz_slug', validators=[
        ExistValidator(Quiz, field='slug')
    ])

    def __init__(self, hide_quiz=False, *args, **kwargs) -> None:
        """
            While working using `QuestionSerializer` in `QuizSerializer`
            `quiz` field will be populated by `QuizSerilaizer` after the 
            creation of quiz, therefore this fields need to be removed 
            from here. Otherwise, keep the `quiz` field
        """

        if hide_quiz:
            del self.fields['quiz'] 

        super().__init__(*args, **kwargs)

    class Meta:
        model = Question
        lookup_field = 'slug'
        fields = [
            'id', 'quiz', 'question_text',
            'question_img', 'question_type',
            'answer', 'created_at', 'updated_at'
        ]
        read_only_fields = ['stats', 'created_at', 'updated_at']
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
        }

    def validate(self, attrs : OrderedDict) -> OrderedDict:
        attrs['answer'] = attrs['answer'].lower()
        if quiz_slug := attrs.pop('quiz_slug', False):
            attrs['quiz'] = Quiz.objects.get(slug=quiz_slug)
        return attrs

    def to_representation(self, instance : Question):
        data : OrderedDict = super().to_representation(instance)
        data['stats'] = instance.stats
        return data

class QuizWithoutQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        lookup_field = 'slug'
        fields = [
            'id', 'name', 'schedule_date',
            'end_date', 'description',
            'time_per_question', 'created_at', 'updated_at',
            'is_live', 'question_count',
        ]
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def to_representation(self, instance : Quiz):
        data : OrderedDict = super().to_representation(instance)
        data['id'] = instance.slug
        data['questions'] = instance.questions.values_list('slug', flat=True)
        data['total_questions'] = instance.question_count
        return data

class QuizSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='slug')
    name = serializers.CharField(validators=[
        MaxLengthValidator(250),
        MinLengthValidator(3),
        UniqueValidator(queryset=Quiz.objects.all())
    ])
    questions = QuestionSerializer(many=True, hide_quiz=True)

    class Meta:
        model = Quiz
        lookup_field = 'slug'
        read_only_fields = ['id', 'created_at', 'updated_at']
        fields = [
            'id', 'name', 'schedule_date', 
            'end_date', 'description', 
            'time_per_question', 'is_live',
            'questions', 'created_at', 'updated_at',
        ]

        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def to_representation(self, instance : Quiz) -> OrderedDict:
        data : OrderedDict = super().to_representation(instance)
        data['created_by'] = get_user(instance.created_by)
        data['updated_by'] = get_user(instance.updated_by)
        return data

    def create(self, validated_data) -> Quiz:
        questions : CollectedDict = validated_data.pop('questions', [])
        quiz : Quiz = super().create(validated_data)

        question_instances = list(map(lambda x: Question(quiz=quiz, **x), questions))
        Question.objects.bulk_create(question_instances)

        return quiz

    def update(self, instance, validated_data) -> Quiz:
        questions : CollectedDict = validated_data.pop('questions', [])
        quiz : Quiz = super().update(instance, validated_data)

        # get list of all the questions that needs to be created & questions that just needs to be updated
        # check for the slugs, if they have slug then update question else create question with that data
        create_question_data : CollectedDict = list(filter(lambda x: 'slug' not in dict(x).keys(), questions))
        update_question_data : CollectedDict = list(filter(lambda x: 'slug' in dict(x).keys(), questions))

        create_question_instance = list(map(lambda x: Question(quiz=quiz, **x), create_question_data))

        # bulk create questions
        Question.objects.bulk_create(create_question_instance)

        # update all the questions with slug
        map(lambda q: Question.objects.filter(slug=q.pop('slug')).update(**q), update_question_data)

        return quiz

class UserTakenQuizSolutionSerializer(serializers.ModelSerializer):
    question = serializers.SlugField(
        required=True, source='question_slug', 
        validators=[ExistValidator(Question, field='slug')]
    )

    class Meta:
        model = QuestionSolution
        read_only_fields = ['id', 'is_correct']
        fields = ['id', 'question', 'answer', 'is_correct']

    def validate(self, attrs : OrderedDict) -> OrderedDict:
        attrs['answer'] = attrs.get('answer').lower()
        question = Question.objects.get(slug=attrs.pop('question_slug'))
        attrs['is_correct'] = question.answer == attrs.get('answer')
        attrs['question'] = question
        return attrs
