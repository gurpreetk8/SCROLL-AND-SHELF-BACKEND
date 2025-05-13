import json
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods

from users.models import CustomUser
from subscriptions.models import Subscription
from datetime import timedelta
from django.utils import timezone

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
            'subscription_id': subscription.id,
            'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None
        }, status=200)

    # Get subscription duration from request (default to 30 days if not provided)
    try:
        data = json.loads(request.body)
        duration_days = int(data.get('duration_days', 30))
    except (json.JSONDecodeError, ValueError):
        duration_days = 30

    now = timezone.now()
    end_date = now + timedelta(days=duration_days)

    subscription = Subscription.objects.create(
        user=user,
        start_date=now,
        end_date=end_date,
        is_active=True
    )

    return JsonResponse({
        'success': True,
        'message': 'Subscription created successfully.',
        'subscription_id': subscription.id,
        'start_date': subscription.start_date.isoformat(),
        'end_date': subscription.end_date.isoformat()
    }, status=200)

@csrf_exempt
def check_subscription(request):
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
        subscription = Subscription.objects.filter(user=user).first()
        
        if subscription and subscription.is_active and subscription.end_date > timezone.now():
            return JsonResponse({
                'success': True,
                'has_subscription': True,
                'end_date': subscription.end_date.isoformat()
            })
        return JsonResponse({
            'success': True,
            'has_subscription': False
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)