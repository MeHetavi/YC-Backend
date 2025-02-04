from django.urls import path
from .views import  ProfileView, FollowView, FollowerListView, FollowingListView,DashboardView, AllUsersView

urlpatterns = [
    path('follow/<str:username>', FollowView.as_view(), name='follow'),
    path('followers/<str:username>', FollowerListView.as_view(), name='followers'),
    path('following/<str:username>', FollowingListView.as_view(), name='following'),
    path('dashboard', DashboardView.as_view(), name='following'),
    path('', AllUsersView.as_view(), name='allUsers'),
    path('<str:username>', ProfileView.as_view(), name='allUsers'),
]