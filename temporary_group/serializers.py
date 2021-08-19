from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Group
from group.serializers import GroupMemberForCreateGroupSerializer


class TemporaryGroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class CreateTmpGroupRequestSerializer(serializers.Serializer):
    founder = serializers.CharField()
    group_name = serializers.CharField()
    schedule_start = serializers.DateTimeField()
    schedule_end = serializers.DateTimeField()
    type = serializers.IntegerField(min_value=1, max_value=8)
    place = serializers.CharField(allow_null=True)
    friend = GroupMemberForCreateGroupSerializer(many=True)



