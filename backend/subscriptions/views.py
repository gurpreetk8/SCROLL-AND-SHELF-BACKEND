import json
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods

from users.models import CustomUser
from subscriptions.models import Subscription

from users.utils import jwt_encode, jwt_decode, auth_user

@csrf_exempt
def pre_book_subscription(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

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

    subscription = Subscription.objects.filter(user=user).first()
    if subscription:
        return JsonResponse({
            'success': True,
            'message': 'Subscription already created.',
            'subscription_id': subscription.id
        }, status=200)

    subscription = Subscription.objects.create(user=user)

    return JsonResponse({
        'success': True,
        'message': 'Subscription pre-booked successfully.',
        'subscription_id': subscription.id
    }, status=200)
