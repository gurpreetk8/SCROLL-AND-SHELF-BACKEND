import json
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods

from users.models import CustomUser
from ebooks.models import Ebook, Category, SampleImage

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
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images]
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
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images]
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
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images]
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
        ebooks = Ebook.objects.filter(best_seller=True).order_by('-created_at')[:10]
        ebook_list = []
        for ebook in ebooks:
            sample_images = ebook.sample_images.all()
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images]
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
        ebooks = Ebook.objects.filter(trending=True).order_by('-created_at')[:10]
        ebook_list = []
        for ebook in ebooks:
            sample_images = ebook.sample_images.all()
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'cover_image': str(ebook.cover_image.url),
                'created_at': ebook.created_at,
                'sample_images': [str(sample_image.image.url) for sample_image in sample_images]
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
        ebook_dict = {
            'id': ebook.id,
            'title': ebook.title,
            'author': ebook.author,
            'description': ebook.description,
            'cover_image': str(ebook.cover_image.url),
            'created_at': ebook.created_at,
            'sample_images': [str(sample_image.image.url) for sample_image in sample_images]
        }
        return JsonResponse({'success': True, 'message': 'Best book of the month fetched successfully.', 'ebook': ebook_dict}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)

@csrf_exempt
def get_ebook_detail(request):
    # 1. Validate request method
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Only POST requests are allowed',
            'status': 405
        }, status=405)

    try:
        # 2. Validate Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                'success': False,
                'message': 'Authorization header with Bearer token is required',
                'status': 401
            }, status=401)

        # 3. Extract and validate token
        try:
            token = auth_header.split(' ')[1]
            if not token:
                return JsonResponse({
                    'success': False,
                    'message': 'Token is missing',
                    'status': 401
                }, status=401)
            
            # Verify token is valid
            if not auth_user(token):
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid or expired token',
                    'status': 401
                }, status=401)
        except IndexError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid Authorization header format',
                'status': 401
            }, status=401)

        # 4. Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data in request body',
                'status': 400
            }, status=400)

        # 5. Validate ebook ID exists in request
        ebook_id = data.get('id')
        if not ebook_id:
            return JsonResponse({
                'success': False,
                'message': 'Ebook ID is required',
                'status': 400
            }, status=400)

        # 6. Get user from token
        try:
            decoded_token = jwt_decode(token)
            user_email = decoded_token.get('email')
            if not user_email:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid token payload',
                    'status': 401
                }, status=401)
                
            user = CustomUser.objects.get(email=user_email)
        except ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found',
                'status': 404
            }, status=404)

        # 7. Get ebook details
        try:
            ebook = Ebook.objects.get(id=ebook_id)
            sample_images = ebook.sample_images.all()
            
            # Build response data with null checks
            ebook_dict = {
                'id': ebook.id,
                'title': ebook.title,
                'author': ebook.author,
                'description': ebook.description,
                'cover_image': str(ebook.cover_image.url) if ebook.cover_image else None,
                'created_at': ebook.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(ebook, 'created_at') else None,
                'sample_images': [str(img.image.url) for img in sample_images if img.image],
            }

            # Add file URL if user is subscribed and file exists
            if user.is_subscribed and hasattr(ebook, 'file') and ebook.file:
                ebook_dict['file_url'] = str(ebook.file.url)

            return JsonResponse({
                'success': True,
                'message': 'Ebook details fetched successfully',
                'ebook': ebook_dict,
                'status': 200
            })

        except ObjectDoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Ebook not found',
                'status': 404
            }, status=404)

    except Exception as e:
        # Log the actual error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_ebook_detail: {str(e)}", exc_info=True)
        
        return JsonResponse({
            'success': False,
            'message': 'An internal server error occurred',
            'status': 500
        }, status=500)