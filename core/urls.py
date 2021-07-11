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

router = DefaultRouter()
router.register('friend', friend_views.FriendViewSet)
router.register('group', group_views.GroupViewSet)
router.register('studyplan', studyplan_views.StudyPlanViewSet)
router.register('temporary_group', temporary_group_views.TemporaryGroupViewSet)

# account
router.register('account', account_views.AccountViewSet)
# schedule
router.register('schedule', schedule_views.ScheduleViewSet)
# note
router.register('note', note_views.NoteViewSet)
# vote
router.register('vote', vote_views.VoteViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
