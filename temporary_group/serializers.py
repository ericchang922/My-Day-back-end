from datetime import datetime

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Schedule, Group, Account


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class GroupMemberForCreateGroupSerializer(serializers.Serializer):
    friendId = serializers.CharField(default=None)


class CreateTmpGroupRequestSerializer(serializers.Serializer):
    founder = serializers.CharField(required=True)
    group_name = serializers.CharField(required=True)
    scheduleStartTime = serializers.DateTimeField(required=True)
    scheduleEndTime = serializers.DateTimeField(required=True)
    type = serializers.IntegerField(required=True, min_value=1, max_value=8)
    place = serializers.CharField(required=True)
    friend = GroupMemberForCreateGroupSerializer(many=True)

