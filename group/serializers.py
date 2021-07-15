from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Group


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class GroupMemberForCreateGroupSerializer(serializers.Serializer):
    friendId = serializers.CharField(default=None)


class CreateGroupRequestSerializer(serializers.ModelSerializer):
    friend = GroupMemberForCreateGroupSerializer(many=True)

    class Meta:
        model = Group
        fields = '__all__'
