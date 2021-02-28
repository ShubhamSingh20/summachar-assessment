from uuid import uuid4
from django.db import models
from datetime import datetime
from helper.models import ModelStamps
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

User  = get_user_model()

# Create your models here.

class Quiz(ModelStamps):
    name = models.CharField(_('name'), max_length=250)
    slug = models.SlugField(_('slug'), default=uuid4, editable=False)
    schedule_date = models.DateTimeField(_('schedule_date'))
    end_date = models.DateTimeField(_('end_date'))
    description = models.TextField(_('description'), null=True, default=None)
    time_per_question = models.PositiveSmallIntegerField(
        _('time_per_question'), default=60, 
        help_text=_('Time in seconds to be given per question for a quiz')
    )

    def __str__(self) -> str:
        return '<Quiz {}>'.format(self.name)

    @property
    def question_count(self) -> int:
        return self.questions.count()

    @property
    def is_live(self) -> bool:
        today = datetime.now()
        return  today >= self.schedule_date or today <= self.end_date 

    @property
    def questions(self) -> QuerySet:
        return Question.objects.filter(quiz=self)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    slug = models.SlugField(_('slug'), default=uuid4, editable=False)
    question_text = models.TextField(_('question_text'), null=False)
    question_img = models.FileField(
        _('question_img'), 
        null=True, default=None
    )

    QUESTION_TYPE_ENUM = (
        ('mcq', 'MCQ'),
        ('open_text', 'Open Text'),
    )

    question_type = models.CharField(
        _('question_type'), max_length=50, 
        choices=QUESTION_TYPE_ENUM
    )

    answer = models.CharField(_('answer'), max_length=15)

    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated_at'), auto_now=True)

    def __str__(self) -> str:
        return '<Question {} of Quiz {}>'.format(self.id, self.quiz.name)

    @property
    def quiz_slug(self) -> str:
        return self.quiz.slug

    @property
    def solution(self) -> QuerySet:
        return QuestionSolution.objects.get(question=self)

class TakenQuiz(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    taken_on = models.DateTimeField(_('taken_on'), auto_now_add=True)
    score = models.FloatField(_('score'), default=0)

    def save_total_score(self) -> None:
        self.score = QuestionSolution.objects.filter(
            taken_quiz=self, is_correct=True
        ).count()

        self.save()

    @property
    def answers(self) -> QuerySet:
        return QuestionSolution.objects.filter(taken_quiz=self)

    def __str__(self) -> str:
        return '< %s by %s>' % (self.quiz.name, self.user.username)

class QuestionSolution(models.Model):
    taken_quiz = models.ForeignKey(TakenQuiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(_('is_correct'), default=False)
    answer = models.CharField(
        _('answer'), max_length=250, 
        null=True, default=None
    )
