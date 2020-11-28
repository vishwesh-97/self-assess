from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from weasyprint import HTML
import tweepy

from apps.assess.models import UserAssessment, UserAnswer, AssessmentQuestion
from apps.assess.serializers import AssessmentSerializer, AssessmentQuestionSerializer, UserAnswerSerializer, \
    TodayQuestionSerializer, GenerateReportSerializer

import datetime

from assessment import settings
from utils.helpers import send_email


class AssessmentView(generics.CreateAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    """
    View to add, update and retrieve Assessment
    """
    permission_classes = [IsAuthenticated]
    queryset = UserAssessment.objects.all()
    serializer_class = AssessmentSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if instance.completed_days == instance.total_days:
            instance.end_datetime = datetime.datetime.now()
            instance.save()
        return Response(serializer.data)


class AllAssessmentView(generics.ListAPIView):
    """
    view which returns assessments of logged in user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        return UserAssessment.objects.filter(user=self.request.user)


class AllQuestionsView(generics.ListAPIView):
    """
    view which returns all the question from the database
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentQuestionSerializer


class UserAnswerView(generics.CreateAPIView):
    """
    view to create user answer
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserAnswerSerializer


class TodayQuestionsView(generics.GenericAPIView):
    """
    View that returns custom prepared question text base on previous days answers for specific users
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TodayQuestionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data.get('user')
        assessment_id = serializer.validated_data.get('assessment')

        today = datetime.datetime.today()
        all_today_answers = list(UserAnswer.objects.filter(user_id=user_id, assessment_id=assessment_id,
                                                           answer_datetime__date=today.date()).values_list('question_id', flat=True))
        # today_timestamp = int(datetime.datetime.today().timestamp())
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        # if UserAnswer.objects.filter(user_id=user_id, assessment_id=assessment_id,
        #                              answer_datetime__date=yesterday.date()).exists():
        #     que_list = []
        #     all_answers = UserAnswer.objects.filter(user_id=user_id, assessment_id=assessment_id,
        #                                             answer_datetime__date=yesterday.date())
        #     for ans in all_answers:
        #         if ans.answer == 1:
        #             # question with still
        #             data_dict = {
        #                 'id': ans.question.id,
        #                 'que_text': 'Still, {}'.format(ans.question.que_text)
        #             }
        #         else:
        #             data_dict = {
        #                 'id': ans.question.id,
        #                 'que_text': '{}'.format(ans.question.que_text)
        #             }
        #         # que_list.append(data_dict)
        #         if ans.question.id not in all_today_answers:
        #             que_list.append(data_dict)
        #     return Response(que_list, status=status.HTTP_200_OK)
        # else:
        #     ques_list = []
        #     all_questions = AssessmentQuestion.objects.all()
        #     for que in all_questions:
        #         if que.id not in all_today_answers:
        #             data_dict = {
        #                 'id': que.id,
        #                 'que_text': que.que_text
        #             }
        #             ques_list.append(data_dict)
        #     return Response(ques_list, status=status.HTTP_200_OK)
        if UserAnswer.objects.filter(user_id=user_id, assessment_id=assessment_id,
                                     answer_datetime__date=yesterday.date()).exists():
            que_list = []
            all_answers = UserAnswer.objects.filter(user_id=user_id, assessment_id=assessment_id,
                                                    answer_datetime__date=yesterday.date())
            for ans in all_answers:
                if ans.answer == 1:
                    # question with still
                    if AssessmentQuestion.objects.filter(parent_que=ans.question).exists():
                        new_que = AssessmentQuestion.objects.filter(parent_que=ans.question).first()
                    else:
                        new_que = None
                    data_dict = {
                        'id': new_que.id if new_que else ans.question.id,
                        'que_text': new_que.que_text if new_que else ans.question.que_text
                    }
                else:
                    data_dict = {
                        'id': ans.question.id,
                        'que_text': '{}'.format(ans.question.que_text)
                    }
                # que_list.append(data_dict)
                if ans.question.id not in all_today_answers:
                    que_list.append(data_dict)
            return Response(que_list, status=status.HTTP_200_OK)
        else:
            ques_list = []
            all_questions = AssessmentQuestion.objects.filter(parent_que__isnull=True)
            for que in all_questions:
                if que.id not in all_today_answers:
                    data_dict = {
                        'id': que.id,
                        'que_text': que.que_text
                    }
                    ques_list.append(data_dict)
            return Response(ques_list, status=status.HTTP_200_OK)


class GenerateReportView(generics.GenericAPIView):
    """
    view to generate report of assessment
    """
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def get(self, request, *args, **kwargs):
        assessment_id = self.kwargs.get("id")
        assessment = UserAssessment.objects.filter(id=assessment_id).first()
        dates = list(set(UserAnswer.objects.filter(user=request.user, assessment_id=assessment_id)
                         .order_by("answer_datetime").values_list("answer_datetime__date", flat=True)))

        data_dict = {}
        for date in dates:
            answer_objs = UserAnswer.objects.filter(user=request.user, assessment_id=assessment_id,
                                                    answer_datetime__date=date)
            data_dict[date] = answer_objs

        """
        data_dict = {
            date: [list of answer objects],
            date: [list of answer objects]
        }
        """
        today = datetime.datetime.now()
        context = {
            "answers": data_dict,
            "user": request.user,
            "assessment": assessment,
            "today": today
        }

        # To generate pdf file
        html = render_to_string('report.html',
                                context=context)
        pdf_file = HTML(string=html).write_pdf()

        # sending the PDF back as response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        return response

        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="detail.csv"'
        # return response


class GetTweetsView(generics.GenericAPIView):
    """
    view which returns tweet of CBC health canada
    """
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        from ibm_watson import ToneAnalyzerV3
        api_key = settings.tone_api_key
        url = settings.tone_url
        authenticator = IAMAuthenticator(api_key)
        tone_analyzer = ToneAnalyzerV3(
            version='2017-09-21',
            authenticator=authenticator
        )
        tone_analyzer.set_service_url(url)

        consumer_key = settings.consumer_key
        consumer_secret = settings.consumer_secret
        access_key = settings.access_key
        access_secret = settings.access_key

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)

        # Calling api
        api = tweepy.API(auth)

        # 100 tweets to be extracted
        number_of_tweets = 10
        all_tweets = api.user_timeline(screen_name="CBCHealth", count=number_of_tweets)

        resp_list = []
        for tweet in all_tweets:
            # data = {
            #     'created_at': tweet.created_at,
            #     'text': tweet.text
            # }
            # response = natural_language_understanding.analyze(
            #     text=tweet.text,
            #     features=Features(
            #         entities=EntitiesOptions(sentiment=True, limit=2),
            #         keywords=KeywordsOptions(sentiment=True, limit=2))).get_result()

            tone_analysis = tone_analyzer.tone(
                {'text': tweet.text},
                content_type='application/json'
            ).get_result()
            tone_name = tone_analysis['document_tone']['tones'][0]['tone_name'] if tone_analysis['document_tone']['tones'] else None
            data = {
                'created_at': tweet.created_at,
                'text': tweet.text,
                'tone': tone_name
            }
            resp_list.append(data)

        response_dict = {
            'username': 'CBCHealth',
            'tweets': resp_list
        }
        return Response(response_dict, status=status.HTTP_200_OK)


class ShareReportView(generics.GenericAPIView):
    """
    view to share report via email
    """
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        assessment_id = self.kwargs.get("id")
        email_ = self.request.query_params.get("email", None)
        if not email_:
            data = {
                'success': False,
                'message': 'Email is required.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        assessment = UserAssessment.objects.filter(id=assessment_id).first()
        dates = list(set(UserAnswer.objects.filter(user=request.user, assessment_id=assessment_id)
                         .order_by("answer_datetime").values_list("answer_datetime__date", flat=True)))

        data_dict = {}
        for date in dates:
            answer_objs = UserAnswer.objects.filter(user=request.user, assessment_id=assessment_id,
                                                    answer_datetime__date=date)
            data_dict[date] = answer_objs

        """
        data_dict = {
            date: [list of answer objects],
            date: [list of answer objects]
        }
        """
        today = datetime.datetime.now()
        context = {
            "answers": data_dict,
            "user": request.user,
            "assessment": assessment,
            "today": today
        }

        # To generate pdf file
        html = render_to_string('report.html',
                                context=context)
        pdf_file = HTML(string=html).write_pdf()

        subject = 'Assessment report - {} {}'.format(request.user.first_name, request.user.last_name)
        message = 'Hello,\n\nPlease find the attachment.'
        email_list = [email_]

        send_email(subject, message, email_list, attachment=pdf_file, attachment_name="report.pdf",
                   attachment_type="application/pdf", bcc=None)

        response_data = {
            'success': True,
            'message': 'Email sent',
        }
        return Response(data=response_data, status=status.HTTP_200_OK)

