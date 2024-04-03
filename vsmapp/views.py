
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model
from django.shortcuts import *
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import login, authenticate,logout
import json
from uuid import *
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.core.mail import send_mail
import json
from django_recaptcha.fields import ReCaptchaField
from django.urls import reverse
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login
from .models import Transaction
from .paytm import *
from django.conf import settings
from .checksum import *
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django import template
import hashlib
import requests
from .helpers import send_forget_password_mail
register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

def generate_random_otp():
    # Implement your logic to generate a random OTP (e.g., a 6-digit number)
    return get_random_string(length=6, allowed_chars='0123456789')

def send_otp_to_email(email, otp):
    # Implement your logic to send the OTP to the user's email
    pass

def index(request):
    # Retrieve all categories
    categories = Category.objects.all()

    # Retrieve all videos
    videos = Product.objects.all()

    context = {
        'categories': categories,
        'videos': videos,
    }
    print(videos)

    return render(request, 'index.html', context)
    
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the user is a regular user
        user_obj = authenticate(username=email, password=password)
        customuser_obj = CustomUser.objects.filter(email=email).first()

        if not user_obj and not customuser_obj:
            messages.warning(request, 'Account does not exist')
            return HttpResponseRedirect(request.path_info)

        if customuser_obj and customuser_obj.is_admin:
            captcha_response = request.POST.get('g-recaptcha-response')
            recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY

            # Verify reCAPTCHA with Google
            verification_url = 'https://www.google.com/recaptcha/api/siteverify'
            payload = {
                'secret': recaptcha_secret_key,
                'response': captcha_response,
                'remoteip': request.META['REMOTE_ADDR'],
            }

            response = requests.post(verification_url, data=payload)
            result = response.json()

            if not result['success']:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return render(request, 'login.html', {})
            
            
            return redirect('/client-dashboard')
        else:
            if user_obj is not None:
                if user_obj.is_active:
                    # Validate reCAPTCHA
                    captcha_response = request.POST.get('g-recaptcha-response')
                    recaptcha_secret_key = settings.RECAPTCHA_PRIVATE_KEY

                    # Verify reCAPTCHA with Google
                    verification_url = 'https://www.google.com/recaptcha/api/siteverify'
                    payload = {
                        'secret': recaptcha_secret_key,
                        'response': captcha_response,
                        'remoteip': request.META['REMOTE_ADDR'],
                    }

                    response = requests.post(verification_url, data=payload)
                    result = response.json()

                    if not result['success']:
                        messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                        return render(request, 'registration/login.html', {})
                    
                    auth_login(request, user_obj)

                # Redirect to /home with the user's unique identifier
                    return redirect(reverse('home', args=[user_obj.id]))# Redirect to /home after successful login

                else:
                    messages.warning(request, 'Your account is not yet activated. Please create an account first')
                    return HttpResponseRedirect(request.path_info)

            messages.warning(request, 'Invalid credentials')
            return HttpResponseRedirect(request.path_info)

    return render(request, 'registration/login.html', {})

def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')  # Display an info message
    return redirect('/login')  # Redirect to the desired page after logout
@transaction.atomic
def client_signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the email is already taken
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        # Generate and store hashed OTP
        otp = generate_random_otp()
        hashed_otp = make_password(otp)

        # Create the CustomUser instance and save it
        user_obj = CustomUser(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),
            is_admin=True  # Set is_client to True for client users
        )
        user_obj.save()

        # Create CustomUserEmailVerification object with the created CustomUser instance
        email_verification_obj = CustomUserEmailVerification.objects.create(user=user_obj, otp=hashed_otp)
        email_verification_obj.save()

        # Send OTP to the user's email
        send_otp_to_email(email, otp)

        # Redirect to the OTP verification page
        return HttpResponseRedirect(reverse('verify_client_otp', args=[user_obj.id]))


    return render(request, 'client_signup.html')

def clientdashboard(request):
   
        categories = Category.objects.all()

        # Assuming 'upload_date' is a field in your Product model
        videos = Product.objects.all().order_by('-upload_date')

        # Paginate the videos
        paginator = Paginator(videos, 2)  # Show 2 videos per page (adjust as needed)
        page = request.GET.get('page')

        try:
            videos = paginator.page(page)
        except PageNotAnInteger:
            videos = paginator.page(1)
        except EmptyPage:
            videos = paginator.page(paginator.num_pages)

        context = {
            'categories': categories,
            'videos': videos,
        }

        return render(request, 'client/clientdashboard.html', context)
    


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the email is already taken
        if User.objects.filter(username=email).exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        # Generate and store hashed OTP
        otp = generate_random_otp()
        hashed_otp = make_password(otp)

        # Create the User instance but don't save it yet
        # Use the email as a unique username
        user_obj = User(username=email, email=email, first_name=first_name, last_name=last_name, is_active=False)
        user_obj.set_password(password)  # Set the password
        user_obj.save()

        # Create EmailVerification object with the created User instance
        email_verification_obj = EmailVerification.objects.create(user=user_obj, otp=hashed_otp)
        email_verification_obj.save()

        # Send OTP to the user's email
        send_otp_to_email(email, otp)

        # Redirect to the OTP verification page
        return HttpResponseRedirect(reverse('verify_otp', args=[user_obj.id]))

    return render(request, 'signup.html')

@login_required
def home(request, user_id):
    if request.user.is_authenticated:
        categories = Category.objects.all()
        videos = Product.objects.all()

        # Paginate the videos
        paginator = Paginator(videos, 2)  # Show 2 videos per page (adjust as needed)
        page = request.GET.get('page')

        try:
            videos = paginator.page(page)
        except PageNotAnInteger:
            videos = paginator.page(1)
        except EmptyPage:
            videos = paginator.page(paginator.num_pages)

        context = {
            'categories': categories,
            'videos': videos,
            'user_id': user_id,  # Pass user_id to the template
        }

        return render(request, 'home.html', context)
    else:
        return redirect('/login')

def verify_client_otp(request, user_id):
    # Retrieve the user based on the provided user_id
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        user_email = request.POST.get('user_email')

        # Retrieve the stored OTP hash for the user
        email_verification_obj = CustomUserEmailVerification.objects.filter(user__email=user_email).first()

        if email_verification_obj and check_password(entered_otp, email_verification_obj.otp):
            # OTP is valid, now update the user activation status
            user_obj = email_verification_obj.user
            user_obj.is_active = True  # Activate the user
            user_obj.save()

            # ... (additional user creation steps, if any)

            # Remove the CustomUserEmailVerification object after successful registration
            email_verification_obj.delete()

            messages.success(request, 'User created successfully.')
            return HttpResponseRedirect('/client-signup')  # Redirect to the desired page after successful signup

        messages.warning(request, 'Invalid OTP. Please try again.')
        return HttpResponseRedirect(request.path_info)

    # Handle the GET request here if needed
    return render(request, 'verify_client_otp.html', {'user': user})
   
def verify_otp(request, user_id):
    # Retrieve the user based on the provided user_id
    user = get_object_or_404(User, id=user_id)
    print(user)

    if request.method == 'POST':
        print("Inside POST method")  # Add this line for debugging
        entered_otp = request.POST.get('otp')
        user_email = request.POST.get('user_email')
        print(entered_otp)
        print(user_email)

        # Retrieve the stored OTP hash for the user
        email_verification_obj = EmailVerification.objects.filter(user__email=user_email).first()
        print(email_verification_obj)
        if email_verification_obj and check_password(entered_otp, email_verification_obj.otp):
            # OTP is valid, now update the user activation status
            user_obj = email_verification_obj.user
            user_obj.is_active = True  # Activate the user
            user_obj.save()

            # Log in the user
            login(request, user_obj)

            # ... (additional user creation steps, if any)

            # Remove the EmailVerification object after successful registration
            email_verification_obj.delete()

            messages.success(request, 'User created successfully.')
            return HttpResponseRedirect('/sign-up')  # Redirect to the desired page after successful signup

        messages.warning(request, 'Invalid OTP. Please try again.')
        return HttpResponseRedirect(request.path_info)

    # Handle the GET request here if needed
    return render(request, 'verify_otp.html', {'user': user})




def send_otp_to_email(email, otp):
    subject = 'Verify Your Email'
    message = f'Your OTP for email verification is: {otp}'
    print(f'OTP for email {email}: {otp}')
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)

def ForgetPassword(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('email')
            print("User name for forget password : ", username)

            # Check if the user with the specified email exists
            if not User.objects.filter(username=username).exists():
                messages.success(request, "No User Found with this username")
                return redirect('/forget-password')

            user_obj = User.objects.get(username=username)
            print(user_obj)

            # Check if the Profile object exists
            profile_obj, created = Profile.objects.get_or_create(user=user_obj)

            # Generate and save a new token
            token = str(uuid.uuid4())
            profile_obj.forget_password_token = token
            profile_obj.save()

            # Send the forget password email
            send_forget_password_mail(user_obj, token)

            messages.success(request, "An email is sent")
            return redirect('/forget-password')

    except Exception as e:
        print(e)

    return render(request, 'forget-password.html')         
    
def ChangePasswords(request, token):
    context = {}
    
    try:
        # Use get_object_or_404 to raise a 404 error if the profile is not found
        profile_obj = get_object_or_404(Profile, forget_password_token=token)

        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')

            if user_id is None:
                messages.success(request, 'No user id found')
                return redirect(f'/change-password/{token}/')

            if new_password != confirm_password:
                messages.success(request, 'Both passwords should be equal')
                return redirect(f'/change-password/{token}/')

            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('/login')

        context = {'user_id': profile_obj.user.id,'token': token}

    except Exception as e:
        print(e)

    return render(request, 'change-password.html', context)
       
    


def latest_videos(request):
    # Query the database to get the latest videos
    latest_videos = Product.objects.order_by('-upload_date')[:10]  # Get the latest 10 videos, change the number as needed
    categories = Category.objects.all()
    context = {
        'latest_videos': latest_videos,
        'categories': categories,
    }

    return render(request, 'latest_videos.html', context)

def add_to_cart(request, product_uid):
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(uid=product_uid)

        # Check if the product is already in the user's cart
        existing_cart_item = Cart.objects.filter(user=user, product=product).first()

        if existing_cart_item:
            messages.warning(request, 'This video is already in your cart.')
        else:
            # Assuming you have a quantity field in your form or want to set a default quantity
            quantity = 1  # You can update this based on your requirements

            # Calculate the total price based on the product's price and quantity
            total_price = product.price * quantity

            # Create a Cart instance for the added product
            cart_item = Cart(
                user=user,
                product=product,
                quantity=quantity,
                total_price=total_price,
            )

            cart_item.save()
            messages.success(request, 'Video added to your cart successfully.')

        return redirect('view_cart')  # Redirect to your cart page
    else:
        # Handle the case where the user is not logged in
        return redirect('/login')

def remove_from_cart(request, product_uid):
    if request.user.is_authenticated:
        user = request.user

        # Find the cart item to remove by the product UID
        cart_item_to_remove = Cart.objects.filter(user=user, product__uid=product_uid).first()

        if cart_item_to_remove:
            cart_item_to_remove.delete()
            messages.success(request, 'Video removed from your cart successfully.')
        else:
            messages.warning(request, 'This video is not in your cart.')

    # Redirect back to the cart page after removing the item
    return redirect('view_cart')

def view_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        # Calculate the total cart price
        total_cart_price = sum(cart_item.total_price for cart_item in cart_items)
      
        context = {
            'cart_items': cart_items,
            'total_cart_price': total_cart_price,
         
        }
       
       
        return render(request, 'cart.html', context)
    
    else:
        # Handle the case where the user is not logged in
        return redirect('/login')
  

    

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('cs_name')
        mobile = request.POST.get('cs_mobile')
        email = request.POST.get('cs_email')
        message= request.POST.get('message')

        # Perform any additional validation if needed

        # Save the data to the database
        contact_submission = ContactSubmission(name=name, mobile=mobile, email=email, message=message)
        contact_submission.save()

        # Display a success message
        messages.success(request, 'Your message has been sent successfully!')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'index1.html')

@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        user = request.user
        MERCHANT_KEY = settings.PAYTM_SECRET_KEY
        form = request.POST
        response_dict = {}
        response_dict = dict(request.POST.items())
        print('Form Data:', form)

        # Check if 'CHECKSUMHASH' key is present in the response_dict
        checksum_hash = response_dict.get('CHECKSUMHASH', None)
        if checksum_hash is not None:
            # Continue with your code
            verify = verifySignature(response_dict, MERCHANT_KEY, checksum_hash)
            if verify:
                for key in request.POST:
                    if key == "BANKTXNID" or key == "RESPCODE":
                        if request.POST[key]:
                            response_dict[key] = int(request.POST[key])
                        else:
                            response_dict[key] = 0
                    elif key == "TXNAMOUNT":
                        response_dict[key] = float(request.POST[key])

                Paytm_history.objects.create(user_id=response_dict['MERC_UNQ_REF'], **response_dict)
                return render(request, "paytm/response.html", {"paytm": response_dict, 'user': user})
            else:
                return HttpResponse("Checksum verification failed")
        else:
            return HttpResponse("CHECKSUMHASH not found in the response")

    return render(request, 'payment/pay.html', {'response': response_dict})


def checkout(request):
    if request.user.is_authenticated:
        user = request.user

        # Retrieve cart items
        cart_items = Cart.objects.filter(user=user)

        # Calculate total cart price
        total_cart_price = sum(item.product.price for item in cart_items)

        # Create a new transaction
        transaction = Transaction.objects.create(made_by=user, amount=total_cart_price)
        transaction.save()

        # Generate Paytm checksum
        merchant_key = settings.PAYTM_SECRET_KEY
        paytm_params = {
            'MID': settings.PAYTM_MERCHANT_ID,
            'ORDER_ID': str(transaction.order_id),
            'CUST_ID': str(transaction.made_by.email),
            'TXN_AMOUNT': str(transaction.amount),
            'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
            'WEBSITE': settings.PAYTM_WEBSITE,
            'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',  # Update with your local development server URL
        }

        # Generate checksum
        #checksum = generateSignature(paytm_params, merchant_key)
        paytm_params['CHECKSUMHASH']= generateSignature(paytm_params, merchant_key)
        

        # Update the transaction with the checksum
        #transaction.checksum = checksum
        transaction.save()

        # Pass relevant data to the template
        context = {
            'cart_items': cart_items,
            'total_cart_price': total_cart_price,
            'paytm_params': paytm_params,
           
        }
       
        print("context",context)
        return render(request, 'checkout.html', context)
    else:
        # Handle the case where the user is not logged in
        return redirect('/login')


def payment_success(request):
    if request.user.is_authenticated:
        user = request.user
        Cart.objects.filter(user=user).delete()
        return render(request, 'success.html')
    return render(request, 'error.html', {'error_message': 'Authentication failed.'})

def send_otp_to_email(email, otp):
    subject = 'Verify Your Email'
    message = f'Your OTP for email verification is: {otp}'
    print(f'OTP for email {email}: {otp}')
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)
    



def category_page(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    print(slug)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'category.html', context)

def addcategory(request):
    if request.method == 'POST':
        # Get category data from the request
        category_name = request.POST.get('category_name')
        category_description = request.POST.get('category_description')

        # Save the category to the database
        Category.objects.create(
            category_name=category_name,
            category_description=category_description
        )
        messages.success(request, 'Category added successfully.')

        # Redirect to a success page or the category list page
        return redirect('/client-dashboard/categorylist')  # Adjust the URL pattern name as needed

    # Handle the GET request here, render a form or any necessary content
    return render(request, 'client/category.html')


def category_list(request):
  
        categories = Category.objects.all()
        return render(request, 'client/category_list.html', {'categories': categories})

def edit_category(request, slug):
  
        category = get_object_or_404(Category, slug=slug)

        if request.method == 'POST':
            # Check if the fields are present in POST data before accessing them
            if 'category_name' in request.POST and 'category_description' in request.POST:
                category.category_name = request.POST['category_name']
                category.category_description = request.POST['category_description']
                category.save()
                messages.success(request, 'Category updated successfully.')
                return redirect('/client-dashboard/categorylist')  # Redirect to the category list page after successful update
           

        return render(request, 'client/edit_category.html', {'category': category})

def delete_category(request, slug):
   

   
        category = Category.objects.get(slug=slug)
        # Add your logic for deleting the category
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('/client-dashboard/categorylist')

def add_video(request):
    

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        availability = request.POST.get('availability') == 'on'
        video_file = request.FILES.get('video_file')

        # Get the category based on the selected ID
        category = Category.objects.get(slug=category_id)

        # Create a new Product instance and save it
        product = Product.objects.create(
            product_name=product_name,
            product_description=product_description,
            price=price,
            category=category,
            availability=availability,
            video_file=video_file,
        )
        messages.success(request, 'Video added successfully.')
        # Redirect to a success page or any other page as needed
        return redirect('/client-dashboard/')  # Adjust the URL pattern name as needed

    # Retrieve all categories for the form
    categories = Category.objects.all()

    return render(request, 'client/add_video.html', {'categories': categories})

def edit_video(request, slug):
    # Retrieve the product based on the provided slug
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        # Update the product fields with the new values from the form
        product.product_name = request.POST.get('product_name')
        product.product_description = request.POST.get('product_description')
        product.price = request.POST.get('price')
        category_id = request.POST.get('category')
        product.availability = request.POST.get('availability') == 'on'

        # Generate a new slug based on the updated product name
        product.slug = slugify(product.product_name)

        # Retrieve the category based on the selected ID
        product.category = Category.objects.get(slug=category_id)

        # Save the changes
        product.save()
        messages.success(request, 'Video updated successfully.')

        # Redirect to the video list page
        return redirect('/client-dashboard')

    # Retrieve all categories for the form
    categories = Category.objects.all()

    # Pass the product and categories to the template for rendering the form
    return render(request, 'client/edit_video.html', {'product': product, 'categories': categories})

def delete_video(request, slug):
    product = Product.objects.get(slug=slug)
    product.delete()
    messages.success(request, 'Video deleted successfully.')
    return redirect('/client-dashboard')
