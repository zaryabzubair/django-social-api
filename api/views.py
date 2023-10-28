import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import UserProfile, Post
from .serializers import UserSerializer, PostSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as EmailValidationError
from django.shortcuts import get_object_or_404


class UserSignup(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')

        # Add email format validation
        try:
            validate_email(email)
        except EmailValidationError:
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

        if not email or not username or not password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
        except IntegrityError:
            return Response({'error': 'Username or email already taken'}, status=status.HTTP_400_BAD_REQUEST)

        user_ip = request.META.get('REMOTE_ADDR')
        ipinfo_url = f"https://ipinfo.io/{user_ip}/json"
        try:
            response = requests.get(ipinfo_url)
            response.raise_for_status()
            ipinfo_data = response.json()
            city = ipinfo_data.get('city')
            region = ipinfo_data.get('region')
            country = ipinfo_data.get('country')
        except requests.RequestException as e:
            return Response({'error': f'Error fetching IP information: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.city = city
            user_profile.region = region
            user_profile.country = country
            user_profile.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token}, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error creating user profile: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(username=username).first()

        if user is None or not user.check_password(password):
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({'access_token': access_token}, status=status.HTTP_200_OK)


class PostList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, post_id):
        return get_object_or_404(Post, id=post_id)

    def get(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = self.get_object(post_id)
        post.delete()
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)


class PostLikeUnlike(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user not in post.likes.all():
            post.likes.add(request.user)
            return Response({'message': 'Post liked'}, status=status.HTTP_200_OK)
        return Response({'message': 'You have already liked this post'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({'message': 'Like removed'}, status=status.HTTP_200_OK)
        return Response({'message': 'You have not liked this post'}, status=status.HTTP_400_BAD_REQUEST)
