from django.forms.models import model_to_dict
from typing import Dict, OrderedDict, List
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from quiz.models import Quiz, Question, QuestionSolution
from helper.validators import ExistValidator
from django.core.validators import MaxLengthValidator, MinLengthValidator

CollectedDict = List[OrderedDict]

get_user = lambda u : model_to_dict(u, ['username', 'created_at', 'updated_at'])

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
            'id', 'slug', 'quiz', 'question_text',
            'question_img', 'question_type',
            'answer', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
        }

    def validate(self, attrs : OrderedDict) -> OrderedDict:
        if quiz_slug := attrs.pop('quiz_slug', False):
            attrs['quiz'] = Quiz.objects.get(slug=quiz_slug)
        return attrs

    def to_representation(self, instance) -> OrderedDict:
        data : OrderedDict= super().to_representation(instance)
        data['quiz_id'] = instance.quiz.slug
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
            'id', 'slug', 'schedule_date', 'questions',
            'end_date', 'is_public', 'description',
            'time_per_question', 'created_at', 'updated_at',
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

        question_instances = map(lambda x: Question(quiz=quiz, **x), questions)
        Question.objects.bulk_create(question_instances)

        return quiz

    def update(self, instance, validated_data) -> Quiz:
        questions : CollectedDict = validated_data.pop('questions', [])
        quiz : Quiz = super().update(instance, validated_data)

        # get list of all the questions that needs to be created & questions that just needs to be updated
        # check for the slugs, if they have slug then update question else create question with that data
        create_question_data : CollectedDict = list(filter(lambda x: 'slug' not in dict(x).keys(), questions))
        update_question_data : CollectedDict = list(filter(lambda x: 'slug' in dict(x).keys(), questions))

        create_question_instance = map(lambda x: Question(quiz=quiz, **x), create_question_data)

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
        read_only_fields = ['id']
        fields = ['id', 'question', 'answer']

    def validate(self, attrs : OrderedDict) -> OrderedDict:
        if question_slug := attrs.pop('question_slug', False):
            attrs['question'] = Question.objects.get(slug=question_slug)
        return attrs
