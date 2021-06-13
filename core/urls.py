"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# friend
import friend.views as friend_views
# from api.views import group as group_views
# from api.views import studyplan as studyplan_views
# from api.views import temporary_group as temporary_group_views

#account
import account.views as account_views
# schedule
from schedule import views as schedule_views

router = DefaultRouter()
router.register('friend', friend_views.FriendViewSet)
router.register('group', group_views.GroupViewSet)
router.register('studyplan', studyplan_views.StudyPlanViewSet)
router.register('temporary_group', temporary_group_views.TemporaryGroupViewSet)

#account
router.register('account', account_views.AccountViewSet)
# schedule
router.register('schedule', schedule_views.ScheduleViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
