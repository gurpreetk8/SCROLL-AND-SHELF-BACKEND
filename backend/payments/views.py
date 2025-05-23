from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json
import razorpay
from decimal import Decimal
from datetime import datetime, timedelta

from payments.models import Payment, Transaction
from subscriptions.models import Subscription

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def create_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    data = json.loads(request.body)
    currency = data.get('currency', 'INR')
    subscription_id = data.get('subscription_id')
    amount = data.get('amount')

    if not subscription_id or not amount:
        return JsonResponse({'success': False, 'message': 'Amount and Subscription ID are required.'}, status=400)
    
    subscription = get_object_or_404(Subscription, id=subscription_id)

    gst_amount = Decimal(0.18) * Decimal(amount)
    other_amount = Decimal(50)
    total_amount = Decimal(amount) + gst_amount + other_amount
    
    try:
        order_data = {
            'amount': int(Decimal(total_amount) * 100),
            'currency': currency,
            'receipt': str(subscription_id),
            'payment_capture': 1
        }
        razorpay_order = client.order.create(data=order_data)

        payment = Payment.objects.create(
            subscription=subscription,
            amount=total_amount,
            status='Pending',
            transaction_id=razorpay_order['id']
        )

        return JsonResponse({
            'success': True,
            'message': 'Order created successfully.',
            'order_id': razorpay_order['id'],
            'amount': order_data['amount'],
            'currency': currency,
            'payment_id': payment.id
        }, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating order: {str(e)}'}, status=400)


@csrf_exempt
def verify_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    data = json.loads(request.body)
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return JsonResponse({'success': False, 'message': 'All payment details are required.'}, status=400)

    try:
        client.utility.verify_payment_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature,
        })

        payment = get_object_or_404(Payment, transaction_id=razorpay_order_id)
        payment.status = 'Completed'
        payment.save()

        subscription = payment.subscription
        subscription.is_active = True
        subscription.amount_paid = payment.amount
        subscription.start_date = datetime.now()
        subscription.end_date = datetime.now() + timedelta(days=30)
        subscription.save()

        transaction = Transaction.objects.create(
            payment=payment,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            razorpay_signature=razorpay_signature
        )

        return JsonResponse({
            'success': True,
            'message': 'Payment verified successfully.',
            'transaction_id': transaction.id
        }, status=200)

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'success': False, 'message': 'Payment verification failed.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error verifying payment: {str(e)}'}, status=400)