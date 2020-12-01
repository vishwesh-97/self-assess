import datetime

from rest_framework import serializers

from apps.assess.models import UserAssessment, AssessmentQuestion, UserAnswer


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAssessment
        fields = '__all__'


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = '__all__'


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = '__all__'


class TodayQuestionSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)
    assessment = serializers.IntegerField(required=True)
    datetime = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        today = datetime.datetime.today()
        user_id = attrs.get('user')
        assessment_id = attrs.get('assessment')
        assessment_obj = UserAssessment.objects.filter(id=assessment_id).first()
        if assessment_obj.end_datetime:
            raise serializers.ValidationError({"completed_msg": "Assessment already completed!"})
        today_ans_count = UserAnswer.objects.filter(user_id=user_id, assessment_id=assessment_id,
                                                    answer_datetime__date=today.date()).count()
        que_count = AssessmentQuestion.objects.all().count()

        if que_count == 0:
            raise serializers.ValidationError({"no_question": "No questions available for the assessment!"})

        if today_ans_count == que_count:
            raise serializers.ValidationError({"submitted_msg": "You have already submitted Answers for today!"})
        return attrs


class GenerateReportSerializer(serializers.Serializer):
    # user = serializers.IntegerField(required=True)
    assessment = serializers.IntegerField(required=True)
