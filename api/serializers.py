from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Friend, Group, GroupList, StudyPlan, Schedule


class FriendSerializer(ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'

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


