import json
from venv import logger
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Q, Count
from django.core.cache import cache
from backend.backend import settings
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

# views.py
from django.db.models import Q

@csrf_exempt
def recommend_books(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Use POST.'}, status=405)

    try:
        # Authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'success': False, 'message': 'Authorization required.'}, status=401)
            
        token = auth_header.split()[1]
        try:
            decoded = jwt_decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = CustomUser.objects.get(email=decoded.get('email'))
        except (jwt_decode.InvalidTokenError, CustomUser.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Invalid token.'}, status=401)

        # User-specific cache key with versioning
        cache_key = f'user_{user.id}_v2_recommendations'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return JsonResponse({
                'success': True,
                'recommendations': cached_data,
                'cached': True,
                'generated_at': cache.ttl(cache_key)  # Time remaining in cache
            })

        # Fetch user's data in optimized queries
        wishlist_ids = Wishlist.objects.filter(user=user).values_list('ebook_id', flat=True)
        reading_data = UserBook.objects.filter(
            user=user,
            status__in=['reading', 'completed']
        ).values_list('book_id', 'status')

        reading_book_ids = [book_id for book_id, _ in reading_data]
        completed_book_ids = [book_id for book_id, status in reading_data if status == 'completed']

        # Get base book data in single queries
        wishlist_books = Ebook.objects.filter(id__in=wishlist_ids).only(
            'id', 'title', 'author', 'series_id', 'series_order', 'cover_url'
        )
        reading_books = Ebook.objects.filter(id__in=reading_book_ids).only(
            'id', 'title', 'author', 'series_id', 'series_order', 'cover_url'
        )

        recommendations = []
        seen_book_ids = set(wishlist_ids).union(reading_book_ids)

        # Rule 1: Series continuation (prioritize reading over completed)
        series_priority = []
        for book in reading_books:
            if book.series_id:
                series_priority.append((book.series_id, book.series_order or 0))
        
        for series_id, current_order in series_priority:
            next_in_series = Ebook.objects.filter(
                series_id=series_id,
                series_order=current_order + 1
            ).exclude(id__in=seen_book_ids).first()
            
            if next_in_series:
                recommendations.append({
                    'id': next_in_series.id,
                    'title': next_in_series.title,
                    'author': next_in_series.author,
                    'cover': next_in_series.cover_url,
                    'reason': 'Next in series',
                    'priority': 1  # Highest priority
                })
                seen_book_ids.add(next_in_series.id)

        # Rule 2: Same author (weighted by user's interaction)
        author_weights = {}
        for book in wishlist_books:
            author_weights[book.author] = author_weights.get(book.author, 0) + 1
        
        for book in reading_books:
            author_weights[book.author] = author_weights.get(book.author, 0) + 2
        
        # Get top 5 authors by weight
        sorted_authors = sorted(author_weights.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for author, weight in sorted_authors:
            author_books = Ebook.objects.filter(
                author=author
            ).exclude(
                id__in=seen_book_ids
            ).order_by('-rating')[:2]  # Get 2 highest rated per author
            
            for book in author_books:
                recommendations.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'cover': book.cover_url,
                    'reason': f'More from {author}',
                    'priority': 2
                })
                seen_book_ids.add(book.id)

        # Rule 3: Similar genre (based on user's reading history)
        if len(recommendations) < 10:
            favorite_genres = Ebook.objects.filter(
                id__in=reading_book_ids
            ).values_list('genres__name', flat=True).distinct()
            
            if favorite_genres:
                similar_books = Ebook.objects.filter(
                    genres__name__in=favorite_genres
                ).exclude(
                    id__in=seen_book_ids
                ).annotate(
                    rating_count=Count('reviews')
                ).order_by('-rating', '-rating_count')[:5]
                
                for book in similar_books:
                    recommendations.append({
                        'id': book.id,
                        'title': book.title,
                        'author': book.author,
                        'cover': book.cover_url,
                        'reason': f'Similar to your {favorite_genres[0]} reads',
                        'priority': 3
                    })
                    seen_book_ids.add(book.id)

        # Rule 4: Popular fallback (weighted by rating and review count)
        if len(recommendations) < 10:
            needed = 10 - len(recommendations)
            popular_books = Ebook.objects.annotate(
                rating_count=Count('reviews'),
                weighted_score=Avg('reviews__rating') * Q(Count('reviews'))
            ).exclude(
                id__in=seen_book_ids
            ).order_by('-weighted_score')[:needed]
            
            for book in popular_books:
                recommendations.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'cover': book.cover_url,
                    'reason': 'Popular in the community',
                    'priority': 4
                })

        # Sort recommendations by priority and freshness
        final_recommendations = sorted(
            recommendations,
            key=lambda x: (x['priority'], x.get('rating', 0)),
        )[:10]

        # Prepare response data
        response_data = []
        for rec in final_recommendations:
            response_data.append({
                'id': rec['id'],
                'title': rec['title'],
                'author': rec['author'],
                'cover': rec.get('cover'),
                'reason': rec['reason']
            })

        # Cache the results for 1 hour
        cache.set(cache_key, response_data, timeout=3600)

        return JsonResponse({
            'success': True,
            'recommendations': response_data,
            'cached': False,
            'generated_at': 'fresh'
        })

    except Exception as e:
        # Log the full error for debugging
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': 'Failed to generate recommendations',
            'error': str(e)
        }, status=500)