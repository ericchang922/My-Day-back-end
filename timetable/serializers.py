from rest_framework.serializers import ModelSerializer

from api.models import PersonalTimetable


class TimetableSerializer(ModelSerializer):
    class Meta:
        model = PersonalTimetable
        fields = '__all__'
