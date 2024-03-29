from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# friend
import friend.views as friend_views
# group
import group.views as group_views
# studyplan
import studyplan.views as studyplan_views
# temporary_group
import temporary_group.views as temporary_group_views

# account
import account.views as account_views
# schedule
from schedule import views as schedule_views
# note
from note import views as note_views
# vote
from vote import views as vote_views
# setting
from setting import views as setting_views
# profile
from user_profile import views as profile_views
from api import views as api_views
# timetable
from timetable import views as timetable_views

router = DefaultRouter()
# friend
router.register('friend', friend_views.FriendViewSet)
# group
router.register('group', group_views.GroupViewSet)
# studyplan
router.register('studyplan', studyplan_views.StudyPlanViewSet)
# temporary_group
router.register('temporary_group', temporary_group_views.TemporaryGroupViewSet)

# account
router.register('account', account_views.AccountViewSet)
# schedule
router.register('schedule', schedule_views.ScheduleViewSet)
# note
router.register('note', note_views.NoteViewSet)
# vote
router.register('vote', vote_views.VoteViewSet)
# setting
router.register('setting', setting_views.SettingViewSet)
# profile
router.register('profile', profile_views.ProfileViewSet)
# timetable
router.register('timetable', timetable_views.TimetableViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('logs/', include('api.urls'))
]
