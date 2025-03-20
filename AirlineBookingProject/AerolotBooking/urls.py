from django.shortcuts import redirect
from django.urls import path
from . import views
from .views import CustomPasswordResetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.flight_view, name='flight_form'),
    path('booking/<int:flight_id>/', views.booking_view, name='booking'),
    path('register/', views.registration_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('myaccount', views.myaccount_view, name='myaccount'),
    path('reservation/<int:booking_id>/', views.reservation_view, name='reservation'),

    path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('reset/', lambda request: redirect('password_reset')),
    path('create_flight/', views.create_flight_view, name='create_flight'),
    path('home_managment/',views.home_managment, name='home_management'),
    path('flights_list', views.flights_list_view, name='flights_list'),
    path('ads_list', views.ads_list_view, name='ads_list'),
    path('create_ad/', views.create_ad_view, name='create_ad'),
    path('edit_flight/<int:flight_id>/', views.edit_flight_view, name='edit_flight'),
    path('edit_ad/<int:ad_id>/', views.edit_ad_view, name='edit_ad'),
    path('verify_email/<int:id>/<str:token>/', views.verify_email, name='verify_email'),
    path('pastr_list', views.past_reservations_view, name='pastr_list'),
    path('futr_list', views.future_reservations_view, name='futr_list'),
    path('user_list', views.users_view, name='user_list'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete_ad/<int:ad_id>/', views.delete_ad, name='delete_ad'),
    path('ad_details/<int:ad_id>/', views.ad_details_view, name='ad_details'),
    path('flights_list_fut',views.fut_flights_list_view, name='flights_list_fut'),
    path('reservation_det/<int:booking_id>/<int:flag>', views.reservation_adm_view, name='reservation_det'),
    path('privacy',views.PrivacyView, name='privacy'),
    path('create_mult_flights', views.create_multiple_flight_view, name='create_mult_flights'),
]