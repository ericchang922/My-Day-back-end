from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Group, GroupList


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


class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupList
        fields = ('group_no', 'group_name', 'type_id', 'cnt')


class GroupInviteListSerializer(ModelSerializer):
    class Meta:
        model = GroupList
        fields = ('group_no', 'group_name', 'type_id', 'founder')


class GroupMemberListNestedSerializer(ModelSerializer):
    class Meta:
        model = GroupList
        fields = ('name', 'status_id')


class GroupMemberListSerializer(ModelSerializer):
    member = GroupMemberListNestedSerializer(many=True)

    class Meta:
        model = GroupList
        fields = ('founder', 'member')
