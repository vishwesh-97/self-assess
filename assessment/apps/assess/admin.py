from django.contrib import admin

from apps.assess.models import UserAnswer, AssessmentQuestion, UserAssessment

admin.site.register(UserAssessment)
admin.site.register(AssessmentQuestion)
admin.site.register(UserAnswer)
