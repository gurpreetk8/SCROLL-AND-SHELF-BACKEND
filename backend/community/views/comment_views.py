from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import json

from community.models import Comment, Post, CustomUser

from users.utils import jwt_decode, auth_user
from django.forms.models import model_to_dict

@csrf_exempt
@require_http_methods(["GET"])
def retrieve_comment_view(request, comment_id):
    try:
        comment = Comment.objects.select_related('user', 'post').get(id=comment_id)
        return JsonResponse({
            "success": True,
            "comment": {
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "user": {
                    "id": comment.user.id,
                    "email": comment.user.email,
                    "first_name": comment.user.first_name,
                    "last_name": comment.user.last_name
                },
                "post": {
                    "id": comment.post.id,
                    "title": comment.post.title,
                    "user_email": comment.post.user.email
                }
            }
        })
    except Comment.DoesNotExist:
        return JsonResponse({"success": False, "message": "Comment not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_comment_view(request, post_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    content = data.get('content')

    if not content:
        return JsonResponse({'success': False, 'message': 'Content is required.'}, status=400)

    try:
        comment = Comment.objects.create(
            user=user,
            post=post,
            content=content
        )
        
        response_data = {
            "success": True,
            "message": "Comment created successfully.",
            "comment": {
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                },
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "username": post.user.username
                }
            }
        }
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error creating comment: {e}"}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def update_comment_view(request, comment_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Comment not found.'}, status=404)

    if comment.user != user:
        return JsonResponse({"success": False, "message": "You are not authorized to update this comment."}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    content = data.get('content')

    if not content:
        return JsonResponse({'success': False, 'message': 'Content is required.'}, status=400)

    comment.content = content
    comment.save()

    return JsonResponse({
        "success": True,
        "message": "Comment updated successfully.",
        "comment": {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            },
            "post": {
                "id": comment.post.id,
                "title": comment.post.title,
                "user_email": comment.post.user.email
            }
        }
    }, status=200)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_comment_view(request, comment_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Comment not found.'}, status=404)

    if comment.user != user:
        return JsonResponse({"success": False, "message": "You are not authorized to delete this comment."}, status=403)

    comment.delete()

    return JsonResponse({"success": True, "message": "Comment deleted successfully."}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def list_comments_for_post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)

    comments = post.comments.select_related('user').all()
    comments_data = []
    
    for comment in comments:
        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "user": {
                "id": comment.user.id,
                "email": comment.user.email,
                "first_name": comment.user.first_name,
                "last_name": comment.user.last_name
            },
            "post": {
                "id": post.id,
                "title": post.title,
                "user_email": post.user.email
            }
        })
    
    return JsonResponse({
        "success": True,
        "comments": comments_data,
        "post_owner": post.user.email
    }, safe=False)