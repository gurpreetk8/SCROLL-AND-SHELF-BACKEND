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
            
        data = request.POST
        ebook_id = data.get('id')
        ebook = Ebook.objects.get(id=ebook_id)
        sample_images = ebook.sample_images.all()
        ebook_dict = {
            'id': ebook.id,
            'title': ebook.title,
            'author': ebook.author,
            'description': ebook.description,
            'cover_image': str(ebook.cover_image.url),
            'created_at': ebook.created_at,
            'sample_images': [str(sample_image.image.url) for sample_image in sample_images],
        }
        if user.is_subscribed:
            ebook_dict['file_url'] = ebook.file.url
        return JsonResponse({'success': True, 'message': 'Ebook detail fetched successfully.', 'ebook': ebook_dict}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=400)
