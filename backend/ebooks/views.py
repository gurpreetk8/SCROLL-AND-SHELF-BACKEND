import json
from venv import logger
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Q, Count
from django.core.cache import cache
from django.conf import settings
from users.models import CustomUser
from ebooks.models import Series, UserBook,Ebook, Category, ReviewRating,Wishlist 
from django.utils import timezone
from users.utils import jwt_encode, jwt_decode, auth_user

from django.forms.models import model_to_dict

# ================================= #
# ========== Ebook API's ========== #
# ================================= #



@csrf_exempt
def get_latest_ebooks(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        ebooks = Ebook.objects.all().order_by('-created_at')[:10]
        ebook_list = []
        for ebook in ebooks:
            sample_images = ebook.sample_images.all()
            tags_list = [tag.strip() for tag in ebook.tags.split(",")] if ebook.tags else []
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'tags': tags_list,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images],
                   'book_type': ebook.book_type,  # Add this
                'series_info': {               # Add this
                    'id': ebook.series.id if ebook.series else None,
                    'name': ebook.series.name if ebook.series else None,
                    'order': ebook.series_order
                } if ebook.book_type == 'series' else None
            
            }
            ebook_list.append(ebook_dict)
        return JsonResponse({'success': True, 'message': 'Latest ebooks fetched successfully.', 'ebooks': ebook_list}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)


@csrf_exempt
def get_all_ebooks(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        ebooks = Ebook.objects.all().order_by('-created_at')
        ebook_list = []
        for ebook in ebooks:
            sample_images = ebook.sample_images.all()
            tags_list = [tag.strip() for tag in ebook.tags.split(",")] if ebook.tags else []
            # In all ebook endpoints (get_all_ebooks, get_latest_ebooks, etc.)
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'tags': tags_list,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images],
                'book_type': ebook.book_type,  # Add this line
                'series_info': {               # Add this block
                    'id': ebook.series.id if ebook.series else None,
                    'name': ebook.series.name if ebook.series else None,
                    'order': ebook.series_order
                } if ebook.book_type == 'series' else None
            }
            ebook_list.append(ebook_dict)
        return JsonResponse({'success': True, 'message': 'All ebooks fetched successfully.', 'ebooks': ebook_list}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def get_all_categories(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        categories = Category.objects.all()
        category_list = []
        for category in categories:
            category_dict = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'image': str(category.image.url),
                'type': category.type,
                'created_at': category.created_at
            }
            category_list.append(category_dict)
        return JsonResponse({'success': True, 'message': 'Categories fetched successfully.', 'categories': category_list}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def get_ebooks_by_category(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        data = request.POST
        category_id = data.get('id')
        category = Category.objects.get(id=category_id)
        ebooks = Ebook.objects.filter(category=category).order_by('-created_at')[:10]
        ebook_list = []
        for ebook in ebooks:
            sample_images = ebook.sample_images.all()
            tags_list = [tag.strip() for tag in ebook.tags.split(",")] if ebook.tags else []
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'tags': tags_list,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images],
                   'book_type': ebook.book_type,  # Add this
                'series_info': {               # Add this
                    'id': ebook.series.id if ebook.series else None,
                    'name': ebook.series.name if ebook.series else None,
                    'order': ebook.series_order
                } if ebook.book_type == 'series' else None
            
            }
            ebook_list.append(ebook_dict)
        return JsonResponse({'success': True, 'message': 'Ebooks by category fetched successfully.', 'ebooks': ebook_list, 'category_name': category.name}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)


@csrf_exempt
def get_best_sellers(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        ebooks = Ebook.objects.filter(best_seller=True).order_by('-created_at')[:6]
        ebook_list = []
        for ebook in ebooks:
            sample_images = ebook.sample_images.all()
            tags_list = [tag.strip() for tag in ebook.tags.split(",")] if ebook.tags else []
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'tags': tags_list,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images],
                   'book_type': ebook.book_type,  # Add this
                'series_info': {               # Add this
                    'id': ebook.series.id if ebook.series else None,
                    'name': ebook.series.name if ebook.series else None,
                    'order': ebook.series_order
                } if ebook.book_type == 'series' else None
            
            }
            ebook_list.append(ebook_dict)
        return JsonResponse({'success': True, 'message': 'Best sellers fetched successfully.', 'ebooks': ebook_list}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def get_trending_books(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        ebooks = Ebook.objects.filter(trending=True).order_by('-created_at')[:8]
        ebook_list = []
        for ebook in ebooks:
            sample_images = ebook.sample_images.all()
            tags_list = [tag.strip() for tag in ebook.tags.split(",")] if ebook.tags else []
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'tags': tags_list,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images],
                   'book_type': ebook.book_type,  # Add this
                'series_info': {               # Add this
                    'id': ebook.series.id if ebook.series else None,
                    'name': ebook.series.name if ebook.series else None,
                    'order': ebook.series_order
                } if ebook.book_type == 'series' else None
            
            }
            ebook_list.append(ebook_dict)
        return JsonResponse({'success': True, 'message': 'Trending books fetched successfully.', 'ebooks': ebook_list}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def get_best_of_the_month_book(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        ebook = Ebook.objects.filter(best_of_month=True).order_by('-created_at').first()
        if not ebook:
            return JsonResponse({'success': False, 'message': 'No best book of the month.'}, status=404)
        sample_images = ebook.sample_images.all()
        tags_list = [tag.strip() for tag in ebook.tags.split(",")] if ebook.tags else []
        ebook_dict = {
            'id': ebook.id,
            'title': ebook.title,
            'author': ebook.author,
            'description': ebook.description,
            'tags': tags_list,
            'cover_image': str(ebook.cover_image.url),
            'created_at': ebook.created_at,
            'sample_images': [str(sample_image.image.url) for sample_image in sample_images],
               'book_type': ebook.book_type,  # Add this
                'series_info': {               # Add this
                    'id': ebook.series.id if ebook.series else None,
                    'name': ebook.series.name if ebook.series else None,
                    'order': ebook.series_order
                } if ebook.book_type == 'series' else None
            
        }
        return JsonResponse({'success': True, 'message': 'Best book of the month fetched successfully.', 'ebook': ebook_dict}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)


# views.py (ebooks)

@csrf_exempt
def get_ebook_detail(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
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
            
        data = json.loads(request.body)
        ebook_id = data.get('id')
        ebook = Ebook.objects.get(id=ebook_id)
        sample_images = ebook.sample_images.all()
        
        # Get tags as a list from the comma-separated string
        tags_list = [tag.strip() for tag in ebook.tags.split(",")] if ebook.tags else []
        
        ebook_dict = {
            'id': ebook.id,
            'title': ebook.title,
            'author': ebook.author,
            'description': ebook.description,
            'tags': tags_list,  # Updated to use the CharField tags
            'cover_image': str(ebook.cover_image.url),
            'created_at': ebook.created_at,
            'sample_images': [str(sample_image.image.url) for sample_image in sample_images],
            'book_type': ebook.book_type,
            'series_info': {
                'id': ebook.series.id if ebook.series else None,
                'name': ebook.series.name if ebook.series else None,
                'order': ebook.series_order
            } if ebook.book_type == 'series' else None,
            'review_stats': {
                'average_rating': ReviewRating.objects.filter(ebook=ebook).aggregate(Avg('rating'))['rating__avg'] or 0,
                'total_reviews': ReviewRating.objects.filter(ebook=ebook).count()
            }
        }
        
        if user.is_subscribed:
            ebook_dict['file_url'] = ebook.file.url
            
        return JsonResponse({
            'success': True, 
            'message': 'Ebook detail fetched successfully.', 
            'ebook': ebook_dict
        }, status=200)
        
    except Ebook.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Ebook not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_series_books(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Use POST.'}, status=405)

    try:
        data = json.loads(request.body)
        series_id = data.get('series_id')
        
        series = Series.objects.get(id=series_id)
        books = series.books.all().order_by('series_order')
        
        book_list = []
        for book in books:
            book_list.append({
                'id': book.id,
                'title': book.title,
                'cover_image': str(book.cover_image.url),
                'series_order': book.series_order
            })
            
        return JsonResponse({
            'success': True,
            'series': {
                'name': series.name,
                'cover_image': str(series.cover_image.url) if series.cover_image else None,
                'description': series.description
            },
            'books': book_list
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
def get_all_series(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Use POST.'}, status=405)

    try:
        series = Series.objects.all().order_by('name')
        series_list = []
        
        for s in series:
            series_list.append({
                'id': s.id,
                'name': s.name,
                'cover_image': str(s.cover_image.url) if s.cover_image else None,
                'book_count': s.books.count()
            })
            
        return JsonResponse({
            'success': True,
            'series': series_list
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
def get_book_reviews(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        data = json.loads(request.body)
        ebook_id = data.get('ebook_id')
        reviews = ReviewRating.objects.filter(ebook_id=ebook_id).select_related('user').order_by('-created_at')
        
        review_list = []
        for review in reviews:
            review_list.append({
                'id': review.id,
                'user': {
                    'email': review.user.email,
                    'name': f"{review.user.first_name} {review.user.last_name}"
                },
                'rating': review.rating,
                'review_text': review.review_text,
                'created_at': review.created_at
            })
        
        # Calculate average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0 
        
        return JsonResponse({
            'success': True,
            'reviews': review_list,
            'average_rating': round(avg_rating, 1),
            'total_reviews': len(review_list)
        }, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def submit_review(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token.'}, status=401)
    
    try:
        decoded = jwt_decode(token)
        user = CustomUser.objects.get(email=decoded.get('email'))
        data = json.loads(request.body)
        
        ebook_id = data.get('ebook_id')
        rating = data.get('rating')
        review_text = data.get('review_text', '').strip()

        # Validate at least rating exists
        if not rating:
            return JsonResponse({'success': False, 'message': 'Rating is required.'}, status=400)

        # Create or update review
        review, created = ReviewRating.objects.update_or_create(
            user=user,
            ebook_id=ebook_id,
            defaults={
                'rating': rating,
                'review_text': review_text if review_text else None
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully!',
            'action': 'created' if created else 'updated'
        }, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def delete_review(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token.'}, status=401)
    
    try:
        decoded = jwt_decode(token)
        user = CustomUser.objects.get(email=decoded.get('email'))
        data = json.loads(request.body)
        review_id = data.get('review_id')
        
        ReviewRating.objects.filter(id=review_id, user=user).delete()
        return JsonResponse({'success': True, 'message': 'Review deleted.'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def get_user_review(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token.'}, status=401)
    
    try:
        decoded = jwt_decode(token)
        user = CustomUser.objects.get(email=decoded.get('email'))
        data = json.loads(request.body)
        ebook_id = data.get('ebook_id')
        
        review = ReviewRating.objects.filter(user=user, ebook_id=ebook_id).first()
        
        if not review:
            return JsonResponse({'success': True, 'has_review': False}, status=200)
        
        return JsonResponse({
            'success': True,
            'has_review': True,
            'review': {
                'id': review.id,
                'rating': review.rating,
                'review_text': review.review_text,
                'created_at': review.created_at
            }
        }, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def add_to_wishlist(request):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'message': 'Use POST method.'}, 
            status=405
        )

    # Authentication
    bearer = request.headers.get('Authorization', '')
    if not bearer.startswith('Bearer '):
        return JsonResponse(
            {'success': False, 'message': 'Authorization token missing or invalid.'}, 
            status=401
        )

    try:
        token = bearer.split(' ')[1]
        if not auth_user(token):
            return JsonResponse(
                {'success': False, 'message': 'Invalid or expired token.'}, 
                status=401
            )

        # Get user
        decoded = jwt_decode(token)
        try:
            user = CustomUser.objects.get(email=decoded.get('email'))
        except CustomUser.DoesNotExist:
            return JsonResponse(
                {'success': False, 'message': 'User not found.'}, 
                status=404
            )

        # Validate request data
        try:
            data = json.loads(request.body)
            ebook_id = data.get('ebook_id')
            if not ebook_id:
                return JsonResponse(
                    {'success': False, 'message': 'ebook_id is required.'},
                    status=400
                )
        except json.JSONDecodeError:
            return JsonResponse(
                {'success': False, 'message': 'Invalid JSON data.'},
                status=400
            )

        # Get ebook and add to wishlist
        try:
            ebook = Ebook.objects.get(id=ebook_id)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=user,
                ebook=ebook
            )
            
            if created:
                return JsonResponse(
                    {
                        'success': True, 
                        'message': 'Added to wishlist.',
                        'wishlist_id': wishlist_item.id
                    }, 
                    status=201
                )
            return JsonResponse(
                {
                    'success': True, 
                    'message': 'Already in wishlist.',
                    'wishlist_id': wishlist_item.id
                }, 
                status=200
            )

        except Ebook.DoesNotExist:
            return JsonResponse(
                {'success': False, 'message': 'Ebook not found.'}, 
                status=404
            )

    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': 'Internal server error.'},
            status=500
        )
@csrf_exempt
def get_wishlist(request):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'message': 'Use POST method.'}, 
            status=405
        )

    # Authentication
    bearer = request.headers.get('Authorization', '')
    if not bearer.startswith('Bearer '):
        return JsonResponse(
            {'success': False, 'message': 'Authorization token missing or invalid.'}, 
            status=401
        )

    try:
        token = bearer.split(' ')[1]
        if not auth_user(token):
            return JsonResponse(
                {'success': False, 'message': 'Invalid or expired token.'}, 
                status=401
            )

        # Get user
        decoded = jwt_decode(token)
        try:
            user = CustomUser.objects.get(email=decoded.get('email'))
        except CustomUser.DoesNotExist:
            return JsonResponse(
                {'success': False, 'message': 'User not found.'}, 
                status=404
            )

        # Get wishlist with optimized query
        wishlist_items = Wishlist.objects.filter(user=user)\
                          .select_related('ebook')\
                          .only('ebook__id', 'ebook__title', 'ebook__author', 
                                'ebook__cover_image', 'ebook__created_at')

        ebooks = [{
            'id': item.ebook.id,
            'title': item.ebook.title,
            'author': item.ebook.author,
            'cover_image': request.build_absolute_uri(item.ebook.cover_image.url),
            'created_at': item.ebook.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'added_to_wishlist': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for item in wishlist_items]

        return JsonResponse(
            {
                'success': True, 
                'count': len(ebooks),
                'wishlist': ebooks
            }, 
            status=200
        )

    except Exception as e:
        logger.error(f"Error fetching wishlist: {str(e)}")  # Add logging
        return JsonResponse(
            {'success': False, 'message': 'Could not fetch wishlist.'},
            status=500
        )
    
@csrf_exempt
def remove_from_wishlist(request):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'message': 'Use POST method.'}, 
            status=405
        )

    # Authentication
    bearer = request.headers.get('Authorization', '')
    if not bearer.startswith('Bearer '):
        return JsonResponse(
            {'success': False, 'message': 'Authorization token missing or invalid.'}, 
            status=401
        )

    try:
        token = bearer.split(' ')[1]
        if not auth_user(token):
            return JsonResponse(
                {'success': False, 'message': 'Invalid or expired token.'}, 
                status=401
            )

        # Get user
        decoded = jwt_decode(token)
        try:
            user = CustomUser.objects.get(email=decoded.get('email'))
        except CustomUser.DoesNotExist:
            return JsonResponse(
                {'success': False, 'message': 'User not found.'}, 
                status=404
            )

        # Validate request data
        try:
            data = json.loads(request.body)
            ebook_id = data.get('ebook_id')
            if not ebook_id:
                return JsonResponse(
                    {'success': False, 'message': 'ebook_id is required.'},
                    status=400
                )
        except json.JSONDecodeError:
            return JsonResponse(
                {'success': False, 'message': 'Invalid JSON data.'},
                status=400
            )

        # Verify ebook exists
        if not Ebook.objects.filter(id=ebook_id).exists():
            return JsonResponse(
                {'success': False, 'message': 'Ebook not found.'},
                status=404
            )

        # Remove from wishlist
        deleted_count, _ = Wishlist.objects.filter(
            user=user, 
            ebook_id=ebook_id
        ).delete()

        if deleted_count > 0:
            return JsonResponse(
                {'success': True, 'message': 'Removed from wishlist.'},
                status=200
            )
        return JsonResponse(
            {'success': False, 'message': 'Item not found in wishlist.'},
            status=404
        )

    except Exception as e:
        logger.error(f"Error removing from wishlist: {str(e)}")  # Add logging
        return JsonResponse(
            {'success': False, 'message': 'Could not remove from wishlist.'},
            status=500
        )
    
@csrf_exempt
def check_wishlist_status(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        # Authentication
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_user(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        data = json.loads(request.body)
        ebook_id = data.get('ebook_id')
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        try:
            user = CustomUser.objects.get(email=user_email)
            wishlist_item = Wishlist.objects.filter(user=user, ebook_id=ebook_id).first()
            
            return JsonResponse({
                'success': True,
                'is_in_wishlist': wishlist_item is not None,
                'wishlist_id': str(wishlist_item.id) if wishlist_item else None
            })
            
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)
    
@csrf_exempt
def add_reading_book(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        # Authentication
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
        
        # Parse body and get ebook
        data = json.loads(request.body)
        ebook_id = data.get('id')

        if not ebook_id:
            return JsonResponse({'success': False, 'message': 'id (ebook_id) is required'}, status=400)

        try:
            ebook = Ebook.objects.get(id=ebook_id)
        except Ebook.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Book not found'}, status=404)

        # Create or update reading status
        user_book, created = UserBook.objects.get_or_create(
            user=user,
            book=ebook,
            defaults={
                'status': 'reading',
                'started_reading': timezone.now()
            }
        )

        if not created:
            user_book.status = 'reading'
            user_book.save()

        return JsonResponse({
            'success': True,
            'message': 'Book added to reading list successfully',
            'data': {
                'book_id': ebook.id,
                'title': ebook.title,
                'status': user_book.status,
                'last_read': user_book.last_read.isoformat() if user_book.last_read else None,
                'started_reading': user_book.started_reading.isoformat() if user_book.started_reading else None
            }
        }, status=201 if created else 200)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@csrf_exempt
def get_reading_books(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        # Authentication
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
            
        # Get reading books
        reading_books = UserBook.objects.filter(
            user=user,
            status='reading'
        ).select_related('book').order_by('-last_read')
        
        books_data = []
        for user_book in reading_books:
            book = user_book.book
            books_data.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'cover_image': request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
                'started_reading': user_book.started_reading.isoformat(),
                'last_read': user_book.last_read.isoformat(),
                'status': user_book.status
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Reading books fetched successfully',
            'count': len(books_data),
            'books': books_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)



@csrf_exempt
def recommend_books(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Use POST.'}, status=405)

    try:
        # Authentication
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_user(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        decoded = jwt_decode(token)
        user = CustomUser.objects.get(email=decoded.get('email'))

        # Check cache
        cache_key = f'recs_{user.id}'
        if cached_recs := cache.get(cache_key):
            return JsonResponse({'success': True, 'recommendations': cached_recs})

        # Get recommendations with actual ratings
        wishlist_ids = Wishlist.objects.filter(user=user).values_list('ebook_id', flat=True)
        reading_ids = UserBook.objects.filter(user=user, status='reading').values_list('book_id', flat=True)

        recommendations = []
        ebooks = Ebook.objects.annotate(
            avg_rating=Avg('reviews_ratings__rating'),
            rating_count=Count('reviews_ratings')
        ).exclude(Q(id__in=wishlist_ids) | Q(id__in=reading_ids)) \
         .order_by('-avg_rating', '-rating_count')[:10]
        
        for ebook in ebooks:
            recommendations.append({
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'cover_url': request.build_absolute_uri(ebook.cover_image.url) if ebook.cover_image else None,
                'avg_rating': ebook.avg_rating or 0,
                'rating_count': ebook.rating_count or 0
            })

        # Fallback if empty
        if not recommendations:
            recommendations = [{
                'id': -1,
                'title': 'Explore New Books',
                'author': 'Add more to your wishlist',
                'cover_url': request.build_absolute_uri('/static/default-book.png'),
                'avg_rating': 0,
                'rating_count': 0
            }]

        cache.set(cache_key, recommendations, timeout=3600)
        return JsonResponse({
            'success': True,
            'message': 'Recommendations fetched successfully',
            'recommendations': recommendations
        })

    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Failed to load recommendations',
            'error': str(e)
        }, status=500)

@csrf_exempt
def book_search(request):
    # Get query parameters
    title = request.GET.get('title', '').strip()
    author = request.GET.get('author', '').strip()
    category_name = request.GET.get('category', '').strip()

    # Start with all ebooks
    queryset = Ebook.objects.all()

    # Apply filters based on provided parameters
    if title:
        queryset = queryset.filter(title__icontains=title)
    if author:
        queryset = queryset.filter(author__icontains=author)
    if category_name:
        queryset = queryset.filter(category__name__icontains=category_name)

    # Prepare the results in a dictionary format
    results = []
    for book in queryset:
        results.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'cover_image': request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
            'file': request.build_absolute_uri(book.file.url) if book.file else None,
            'category': {
                'id': book.category.id,
                'name': book.category.name,
                'type': book.category.type,
                'slug': book.category.slug,
            },
            'series': {
                'id': book.series.id if book.series else None,
                'name': book.series.name if book.series else None,
            } if book.book_type == 'series' else None,
            'series_order': book.series_order,
            'book_type': book.book_type,
            'tags': book.get_tags_list(),
            'best_seller': book.best_seller,
            'best_of_month': book.best_of_month,
            'trending': book.trending,
            'created_at': book.created_at.isoformat(),
        })

    return JsonResponse({
        'status': 'success',
        'count': len(results),
        'results': results
    })