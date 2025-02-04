from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from profiles.models import Notification
from .models import Post, Like, Comment, Bookmark
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

User = get_user_model()

class PostView(APIView):
    def get(self, request, id=None):
        """Handle GET request to retrieve a post by ID, and its associated comments and likes."""
        try:
            if id:
                try:
                    post = Post.objects.get(id=id)
                    comments = Comment.objects.filter(post=post)
                    likes = Like.objects.filter(post=post,type='like')
                    post_data = PostSerializer(post).data
                    comments_data = CommentSerializer(comments, many=True).data
                    likes_data = LikeSerializer(likes, many=True).data
                    post_data['image'] = request.build_absolute_uri(post_data['image']) if post_data['image'] else None
                    return Response({
                        "post": post_data,
                        "comments": comments_data,
                        "likes": likes_data
                    }, status=status.HTTP_200_OK)
                except Post.DoesNotExist:
                    return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                posts = Post.objects.all()
                response_data = []
                for post in posts:
                    serializer = PostSerializer(post)
                    comments = Comment.objects.filter(post=post)
                    likes = Like.objects.filter(post=post,type='like')
                    
                    comments_data = CommentSerializer(comments, many=True).data
                    likes_data = LikeSerializer(likes, many=True).data
                    data = serializer.data
                    data['image'] = request.build_absolute_uri(data['image']) if data['image'] else None
                    response_data.append({
                        "post": data, 
                        "comments": comments_data,
                        "likes": likes_data
                    })
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Create a new post with blob image support"""
        try:
            image = request.FILES.get('image')
            if image:
                try:
                    # Attempt to open the image file
                    img = Image.open(io.BytesIO(image.read()))
                    img.verify()  # Verify if it's a valid image
                except (IOError, SyntaxError) as e:
                    return Response({"message": "Invalid image file."}, status=status.HTTP_400_BAD_REQUEST)
        
            content = request.data.get('text')  # Ensure text data is retrieved safely
            post = Post.objects.create(
                user=request.user,
                content=content,
                image=image
            )
            post.save()
            post = self.get(request,post.id).data
            return Response({"detail": "Post Created successfully.",'post':post}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": f"Error creating post: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def delete(self, request, id):
        """Handle DELETE request to delete a post."""
        try:
            post = Post.objects.get(id=id)
            if post.user != request.user:
                return Response({"detail": "You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)

            post.delete()
            return Response({"detail": "Post deleted successfully."}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        """Handle PUT request to partially update a post."""
        try:
            post = Post.objects.get(id=id)
            if post.user != request.user:
                return Response(
                    {"detail": "You do not have permission to edit this post."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Handle image update if provided
            image = request.FILES.get('image')
            if image:
                try:
                    # Attempt to open the image file
                    img = Image.open(io.BytesIO(image.read()))
                    img.verify()  # Verify if it's a valid image
                except (IOError, SyntaxError) as e:
                    return Response({"message": "Invalid image file."}, status=status.HTTP_400_BAD_REQUEST)
    
                if post.image:
                    post.image.delete()
                
                # Set new image
                post.image = image         
            content = request.data.get('content')  # Ensure text data is retrieved safely
            post.content = content
            post.save()
            post = self.get(request,post.id).data
            return Response({'message':'Post edited successfully.','post':post}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"detail": f"Error updating post: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
"""View to handle liking and commenting on posts."""
class PostLikeView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """Handle POST request to like or comment on a post."""
        try:
            post = Post.objects.filter(id=id).first()
            if not post:
                return Response({"message": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
            # Like the post
            like = Like.objects.filter(post=post, user=request.user).first()
            if like:
                if like.type == 'dislike':
                    like.type = 'like'
                    like.save()
                else:
                    return Response({"message": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                Like.objects.create(post=post, user=request.user)
            Notification.objects.create(
                recipient=post.user,
                actor=request.user,
                verb='liked',
                target=f'post: {post}'
            )
            post_view = PostView()
            post = post_view.get(request,id=post.id).data
            return Response({"message": "Post liked successfully.", "post":post}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

class PostDislikeView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """Handle POST request to dislike a post."""
        try:
            post = Post.objects.filter(id=id).first()
            if not post:
                return Response({"message": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

            # Dislike the post
            if Like.objects.filter(post=post, user=request.user, type='dislike').exists():
                return Response({"message": "You have already disliked this post."}, status=status.HTTP_400_BAD_REQUEST)

            # If the user has liked the post before disliking, remove the like
            like = Like.objects.filter(post=post, user=request.user, type='like').first()

            if like:
                like.delete()
            
            Like.objects.create(post=post, user=request.user, type='dislike')
            post_view = PostView()
            post = post_view.get(request,id=post.id).data
            return Response({"message": "Post disliked successfully.","post":post}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

class PostCommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, id):
        """Handle POST request to like or comment on a post."""
        try:
            post = Post.objects.filter(id=id).first()
            if not post:
                return Response({"message": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Comment on the post
            comment_text = request.data.get('commentData')
            if not comment_text:
                return Response({"message": "Comment text is required."}, status=status.HTTP_400_BAD_REQUEST)
            Comment.objects.create(post=post, user=request.user, text=comment_text)
            Notification.objects.create(
                recipient=post.user,
                actor=request.user,
                verb='commented on',
                target=f'post: {post}'
            )
            post_view = PostView()
            post = post_view.get(request,id=post.id).data
            return Response({"message": "Comment added successfully.",'post':post}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        """Handle PUT request to edit a comment."""
        try:
            comment = Comment.objects.filter(id=id, user=request.user).first()
            if not comment:
                return Response({"message": "Comment not found or you're not authorized to edit it."}, status=status.HTTP_404_NOT_FOUND)

            comment_text = request.data.get('commentData')
            if not comment_text:
                return Response({"message": "Comment text is required."}, status=status.HTTP_400_BAD_REQUEST)

            comment.text = comment_text
            comment.save()
            
            post_view = PostView()
            post = post_view.get(request,id=comment.post.id).data
            return Response({"message": "Comment updated successfully.","post":post}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """Handle DELETE request to delete a comment."""
        try:
            comment = Comment.objects.filter(id=id, user=request.user).first()
            if not comment:
                return Response({"message": "Comment not found or you're not authorized to delete it."}, status=status.HTTP_404_NOT_FOUND)

            comment.delete()
            
            post_view = PostView()
            post = post_view.get(request,id=comment.post.id).data
            return Response({"message": "Comment deleted successfully.",'post':post}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        """Handle GET request to retrieve comments on a post."""
        try:
            post = Post.objects.filter(id=id).first()
            if not post:
                return Response({"message": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)
