from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Schedule


class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'
