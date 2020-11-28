from django.db import models

from apps.users.models import User
from utils.models import BaseModel


class UserAssessment(BaseModel):
    user = models.ForeignKey(User, related_name="user_assessment", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    total_days = models.IntegerField(default=7, help_text="total number of days in the assessment")
    completed_days = models.IntegerField(default=0, help_text="total number of days completed in the assessment")

    def __str__(self):
        return self.name if self.name else None


class AssessmentQuestion(BaseModel):
    que_text = models.CharField(max_length=255, help_text="text of the question")
    parent_que = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    level = models.IntegerField(help_text="Level of question", null=True, blank=True)
    ideal_answer = models.IntegerField(help_text="ideal answer of the question", null=True, blank=True)

    def __str__(self):
        return self.que_text


class UserAnswer(BaseModel):
    user = models.ForeignKey(User, related_name="user_answer", on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, related_name="assessment_user_answer", on_delete=models.CASCADE)
    assessment = models.ForeignKey(UserAssessment, related_name="assessment_answer", on_delete=models.CASCADE)
    answer = models.IntegerField(help_text="Answer of the assessment question")
    answer_datetime = models.DateTimeField(blank=True, null=True)
