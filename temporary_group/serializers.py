from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Group
from group.serializers import GroupMemberForCreateGroupSerializer


class TemporaryGroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class CreateTmpGroupRequestSerializer(serializers.Serializer):
    founder = serializers.CharField(required=True)
    group_name = serializers.CharField(required=True)
    schedule_start = serializers.DateTimeField(required=True)
    schedule_end = serializers.DateTimeField(required=True)
    type = serializers.IntegerField(required=True, min_value=1, max_value=8)
    place = serializers.CharField(required=True)
    friend = GroupMemberForCreateGroupSerializer(many=True)



