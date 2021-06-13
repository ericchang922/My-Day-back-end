from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import StudyPlan, Schedule


class StudyPlanSerializer(ModelSerializer):
    class Meta:
        model = StudyPlan
        fields = '__all__'


class StudyPlanForCreateGroupSerializer(serializers.Serializer):
    subject = serializers.CharField()
    plan_start = serializers.DateTimeField()
    plan_end = serializers.DateTimeField()
    is_rest = serializers.CharField()


class CreateStudyPlanSerializer(serializers.ModelSerializer):
    subjects = StudyPlanForCreateGroupSerializer(many=True)

    class Meta:
        model = Schedule
        fields = '__all__'

class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


