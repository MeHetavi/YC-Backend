from django.urls import path
from .views import PostView, PostCommentView,PostLikeView, PostDislikeView

urlpatterns = [
    path('', PostView.as_view(), name='post-list'),
    path('<str:id>', PostView.as_view(), name='post_detail'),
    path('like/<str:id>', PostLikeView.as_view(), name='post_like'),
    path('dislike/<str:id>', PostDislikeView.as_view(), name='post_dislike'),
    path('comment/<str:id>', PostCommentView.as_view(), name='post_comment'),
]
