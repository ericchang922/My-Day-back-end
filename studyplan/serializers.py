from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import StudyPlan, Schedule


class StudyPlanSerializer(ModelSerializer):
    class Meta:
        model = StudyPlan
        fields = '__all__'


class StudyPlanContentSerializer(serializers.Serializer):
    subject = serializers.CharField()
    plan_start = serializers.DateTimeField()
    plan_end = serializers.DateTimeField()
    remark = serializers.CharField(allow_null=True)
    note_no = serializers.IntegerField(default=None, allow_null=True)
    is_rest = serializers.BooleanField()


class CreateStudyPlanSerializer(ModelSerializer):
    subjects = StudyPlanContentSerializer(many=True)

    class Meta:
        model = Schedule
        fields = '__all__'


class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


