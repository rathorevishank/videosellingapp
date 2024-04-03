from django.urls import path, include
from .views import *

urlpatterns = [
    path("", index),
    path('login/', login_view, name='login'),
    path("sign-up", signup),
   path('home/<int:user_id>/', login_required(home), name='home'),
    path('category/<slug>/', category_page, name='category_page'),
    path('latest_videos/', latest_videos, name='latest_videos'),
    path('add_to_cart/<uuid:product_uid>/', add_to_cart, name='add_to_cart'),
    path('view_cart/', view_cart, name='view_cart'),
    path('remove_from_cart/<uuid:product_uid>/', remove_from_cart, name='remove_from_cart'),
    path('logout/', logout_view, name='logout'),
    path('contact/', contact_view, name='contact_view'),
    path('check/', checkout, name='checkout'),
    path('payment_success/', payment_success, name='payment_success'),
    path('verify-otp/<int:user_id>/', verify_otp, name='verify_otp'),
    path('change-password/<str:token>/', ChangePasswords, name='change_password'),
    path('forget-password/', ForgetPassword, name='forget_password'),
    path('handlerequest/', handlerequest, name='handlerequest'),
    path('client-signup/', client_signup, name='client_signup'),
    path('verify-client-otp/<int:user_id>/', verify_client_otp, name='verify_client_otp'),
    path('client-dashboard/', clientdashboard, name='client-dashboard'),
    path('client-dashboard/addcategory/', addcategory, name='addcategory'),
    path('client-dashboard/categorylist/', category_list, name='category_list'),
    path('client-dashboard/edit-category/<slug:slug>/', edit_category, name='edit_category'),
    path('client-dashboard/delete-category/<slug:slug>/', delete_category, name='delete_category'),
    path('client-dashboard/add-video/', add_video, name='add_video'),
    path('client-dashboard/edit_video/<slug:slug>/', edit_video, name='edit_video'),
    path('client-dashboard/delete_video/<slug:slug>/', delete_video, name='delete_video'),
    path('client-dashboard/page/<int:page>/', clientdashboard, name='clientdashboard_paginated'),
  
]
