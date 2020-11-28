from django.urls import path

from . import views

app_name = "assess"

urlpatterns = [
    path('user-assessment', views.AssessmentView.as_view(), name="user-assessment"),
    path('user-assessment/<int:pk>', views.AssessmentView.as_view(), name="user-assessment"),
    path('all-assessments', views.AllAssessmentView.as_view(), name="user-assessments"),
    path('all-questions', views.AllQuestionsView.as_view(), name="assessment-questions"),
    path('user-answer', views.UserAnswerView.as_view(), name="user-answer"),
    path('today-questions', views.TodayQuestionsView.as_view(), name="today-question"),
    path('generate-report/<int:id>', views.GenerateReportView.as_view(), name="generate-report"),
    path('share-report/<int:id>', views.ShareReportView.as_view(), name="share-report"),
    # path('finish-assessment', views.FinishAssessmentView.as_view(), name="finish-assessment"),
    path('cbc-tweets', views.GetTweetsView.as_view(), name="cbc-tweets"),
]
