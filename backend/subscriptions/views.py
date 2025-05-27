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
def create_subscription(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    # Get token
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authorization header missing'}, status=401)
    
    try:
        token = bearer.split()[1]
        if not auth_user(token):
            return JsonResponse({'success': False, 'message': 'Invalid token'}, status=401)
        
        decoded = jwt_decode(token)
        user = CustomUser.objects.get(email=decoded['email'])

        # Check for existing active subscription
        existing_subscription = Subscription.objects.filter(user=user).first()
        if existing_subscription and existing_subscription.is_active and existing_subscription.end_date > timezone.now():
            return JsonResponse({
                'success': False,
                'message': 'Active subscription already exists',
                'code': 'SUBSCRIPTION_EXISTS'
            }, status=200)  # Changed from 400 to 200

        # Parse request data
        try:
            data = json.loads(request.body)
            duration_days = int(data.get('duration_days', 30))
            amount_paid = float(data.get('amount_paid', 0.00))
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid input data'}, status=400)

        now = timezone.now()
        end_date = now + timedelta(days=duration_days)

        # Create or update subscription
        if existing_subscription:
            # Update existing
            existing_subscription.start_date = now
            existing_subscription.end_date = end_date
            existing_subscription.amount_paid = amount_paid
            existing_subscription.is_active = True
            existing_subscription.save()
            subscription = existing_subscription
        else:
            # Create new
            subscription = Subscription.objects.create(
                user=user,
                start_date=now,
                end_date=end_date,
                amount_paid=amount_paid,
                is_active=True
            )

        return JsonResponse({
            'success': True,
            'message': 'Subscription created successfully',
            'subscription_id': subscription.id,
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat(),
            'amount_paid': str(subscription.amount_paid)
        }, status=201)

    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

    
@csrf_exempt
def check_subscription(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    # Authentication
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)
    
    try:
        token = bearer.split()[1]
        decoded = jwt_decode(token)
        user = CustomUser.objects.get(email=decoded['email'])
        subscription = Subscription.objects.filter(user=user, is_active=True).first()
        
        if subscription and subscription.end_date > timezone.now():
            return JsonResponse({
                'success': True,
                'has_subscription': True,
                'start_date': subscription.start_date.isoformat(),
                'end_date': subscription.end_date.isoformat()
            })
        return JsonResponse({
            'success': True,
            'has_subscription': False
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)