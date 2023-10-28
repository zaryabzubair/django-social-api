from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserSignup.as_view(), name='user-signup'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('posts/', PostList.as_view(), name='post-list-create'),
    path('posts/<int:post_id>/', PostDetail.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', PostLikeUnlike.as_view(), name='like-unlike-post'),

]
