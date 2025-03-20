from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.timezone import make_aware

from .forms import FlightForm, BookingForm, CustomUserCreationForm, EmailLoginForm, PassangerForm, FlightModelForm, \
    AdModelForm, MultFlightModelForm
from .models import Flight, Ad, Booking, CustomUser

luggage_dict={
    '0':"Tylko mały bagaż 20x25x40cm",
    '1':"Mały bagaż 20x25x40cm i walizka kabinowa",
    '2':"Mały bagaż 20x25x40cm i bagaż rejestrowy 10kg",
    '3':"Mały bagaż 20x25x40cm i bagaż rejestrowy 20kg"
}
city_airport_dict={
    'WAW': 'Warszawa',
    'BUD': 'Budapeszt',
    'DXB': 'Dubaj',
    'ORD': "Chicago",
    'NAP': 'Neapol',
    'BGO': 'Bergen',
    'OSL': 'Oslo',
    'CDG': 'Paryż',
    'LHR': 'Londyn',
    'FRA': 'Frankfurt nad Menem',
    'MAD': 'Madryt',
    'KRK': 'Kraków',
    'GRU': 'Sao Paulo',
    'EVN': 'Erewań',
    'NQZ': 'Astana',
    'NRT': 'Tokio',
    'LIM': 'Lima',
    'IST': 'Stambuł',
}
code_photo_dict={
    'EVN':'erywan.jpg',
    'NQZ':'astana.jpg',
    'WAW':'warszawa.jpg',
    'CDG':'paryz.jpg',
    'NAP':'neapol.jpg',
    'BUD':'budapeszt.jpg',
    'ORD':'chicago.jpg',
    'FRA':'frankfurt.jpg',
    'GRU':'saopaulo.jpg',
}
def is_superuser(user):
    return user.is_superuser
# Create your views here.
def home(request):
    ads=Ad.objects.all()
    return render(request,'home.html',{'ads':ads})
@user_passes_test(is_superuser)
def home_managment(request):
    return render(request,'create/home_create.html')
@user_passes_test(is_superuser)
def flights_list_view(request):
    flights = Flight.objects.all()
    flag=0
    return render(request,'create/flights_list.html',{'flights':flights,'flag':flag})
@user_passes_test(is_superuser)
def fut_flights_list_view(request):
    flights = Flight.objects.filter(departure_time__gt=timezone.now())
    flag=1
    return render(request,'create/flights_list.html',{'flights':flights,'flag':flag})
@user_passes_test(is_superuser)
def ads_list_view(request):
    ads = Ad.objects.all()
    return render(request,'create/ads_list.html',{'ads':ads})
@user_passes_test(is_superuser)
def past_reservations_view(request):
    res=Booking.objects.filter(flight_id__departure_time__lt=timezone.now())
    return render(request,'create/pastr_list.html',{'res':res})
@user_passes_test(is_superuser)
def future_reservations_view(request):
    res=Booking.objects.filter(flight_id__departure_time__gt=timezone.now())
    return render(request,'create/futr_list.html',{'res':res})
@user_passes_test(is_superuser)
def users_view(request):
    users = CustomUser.objects.all()
    for user in users:
        user.can_be_deleted = user.date_joined <= timezone.now() - timedelta(days=1)

    return render(request,'create/user_list.html',{'users':users})
@user_passes_test(is_superuser)
def create_flight_view(request):
    if request.method == 'POST':
        form = FlightModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flights_list')
    else:
        form = FlightModelForm()
    return render(request, 'create/create_flight.html', {'form': form})
@user_passes_test(is_superuser)
def create_multiple_flight_view(request):
    if request.method == 'POST':
        form = MultFlightModelForm(request.POST)
        if form.is_valid():
            flight_code = form.cleaned_data['flight_code']
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            price = form.cleaned_data['price']
            duration = form.cleaned_data['duration']
            weeks = form.cleaned_data['weeks']
            first_departure_time = form.cleaned_data['first_departure']
            first_arrival = form.cleaned_data['first_arrival']
            print(duration)
            for i in range(weeks):
                departure_time = first_departure_time+timedelta(weeks=i)
                arrival = first_arrival+timedelta(weeks=i)
                flight=Flight(flight_code=flight_code,origin=origin,destination=destination,
                                             departure_time=departure_time,arrival_time=arrival,price=price,duration=duration)
                flight.save()
            return redirect('flights_list')
    else:
        form = MultFlightModelForm()
    return render(request, 'create/create_mult_flight.html', {'form': form})
@user_passes_test(is_superuser)
def create_ad_view(request):
    if request.method == 'POST':
        form = AdModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ads_list')
    else:
        form = AdModelForm()
    return render(request, 'create/create_ad.html', {'form': form})

@user_passes_test(is_superuser)
def edit_flight_view(request, flight_id):
    flight = Flight.objects.get(flight_id=flight_id)
    if request.method == 'POST':
        form = FlightModelForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            return redirect('flights_list')
    else:
        form = FlightModelForm(instance=flight)
    return render(request, 'create/edit_flight.html', {'form': form})
@user_passes_test(is_superuser)
def delete_user(request, user_id):
    if request.method == "POST":
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return redirect('user_list')
@user_passes_test(is_superuser)
def reservation_adm_view(request, booking_id,flag):
    booking=Booking.objects.get(booking_id=booking_id)
    return render(request,'reservation_det.html',{'booking': booking,'flag':flag})
@user_passes_test(is_superuser)
def ad_details_view(request, ad_id):
    ad = Ad.objects.get(ad_id=ad_id)
    return render(request, 'create/ad_details.html',{'ad':ad})
@user_passes_test(is_superuser)
def delete_ad(request, ad_id):
    if request.method == "POST":
            ad = Ad.objects.get(ad_id=ad_id)
            ad.delete()
            return redirect('ads_list')

@user_passes_test(is_superuser)
def edit_ad_view(request, ad_id):
    ad = Ad.objects.get(ad_id=ad_id)
    if request.method == 'POST':
        form = AdModelForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ads_list')  # Replace with your desired redirect URL
    else:
        form = AdModelForm(instance=ad)
    return render(request, 'create/edit_ad.html', {'form': form})
def flight_view(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            departure = form.cleaned_data['miejsce_wylotu']
            arrival = form.cleaned_data['miejsce_przylotu']
            departure_date = form.cleaned_data['data']
            departure_date = departure_date.strftime('%Y-%m-%d')

            flights=Flight.objects.all()
            next_flights =flights.filter(origin=departure,destination=arrival,departure_time__date__gt=departure_date)
            flights=flights.filter(departure_time__date=departure_date,origin=departure,destination=arrival)
            next_flights=next_flights.order_by('departure_time')[:3]
            return render(request, 'flight_result.html', {'flights':flights,'departure': departure, 'arrival': arrival,'date': departure_date,'next_flights':next_flights})
        else:
            return render(request, 'search.html', {'form': form})
    else:
        form = FlightForm()

    return render(request, 'search.html', {'form': form})
def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    Id=user.id
    url = reverse('verify_email', kwargs={'id': Id, 'token': token})

    verification_link = f"{get_current_site(request).domain}{url}"

    subject = "Email Verification"
    message = render_to_string("verification_email.html", {
        'user': user,
        'verification_link': verification_link,
    })


    send_mail(subject, message, 'noreply@aerolot.pl', [user.email],html_message=message)
def registration_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_verification_email(request, user)
            return render(request, 'email_verification_sent.html', {'user': user})
    form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def verify_email(request, id, token):
    try:
        user = get_user_model().objects.get(pk=id)
    except get_user_model().DoesNotExist:
        return redirect('home')

    if default_token_generator.check_token(user, token):
        user.email_verified = True
        user.is_active = True
        user.save()
        return render(request,'home.html')
    else:
        return redirect('home')
def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect('home')  # Redirect to home or another page
    else:
        form = EmailLoginForm()
    return render(request, 'login.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('home')
@login_required
def myaccount_view(request):
    bookings = Booking.objects.filter(user=request.user,flight_id__departure_time__gt=timezone.now())
    return render(request,'myaccount.html',{'bookings':bookings})

@login_required
def booking_view(request, flight_id):
    flight = Flight.objects.get(flight_id=flight_id)
    fp=float(flight.price)
    fp=round(fp,2)
    num_passengers = 0
    passenger_forms = []
    luggage_coeffs={'0':1.0,'1':1.1,'2':1.15,'3':1.2}

    if request.method == 'POST':
        form = BookingForm(request.POST)
        num_passengers = int(request.POST.get('num_passengers', 0))

        passenger_forms = [
            PassangerForm(request.POST,flight_price=fp, prefix=f"Passenger_{i}") for i in range(1, num_passengers + 1)
        ]

        if form.is_valid() and all(pf.is_valid() for pf in passenger_forms):
            booking_date = datetime.now()
            passengers = [pf.cleaned_data for pf in passenger_forms]
            total_price = 0
            luggages=[]
            for passanger in passengers:
                luggage_choice = passanger.get('luggage', '0')
                dec_coeff=Decimal(str(luggage_coeffs[luggage_choice]))
                total_price +=flight.price*dec_coeff
                luggages.append(luggage_dict[luggage_choice])
            total_price=total_price.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
            booking = Booking(
                flight_id=flight,
                user=request.user,
                booking_date=booking_date,
                passanger_number=num_passengers,
                passengers=passengers,
            )
            booking.save()

            return render(request, 'booking_finish.html', {
                'flight': flight,
                'booking_date': booking_date,
                'total_price': total_price,
                'num_passengers': num_passengers,
                'passengers': passengers,
                'luggages': luggages,
            })
        else:
            return render(request, 'booking.html', {
                'form': form,
                'passenger_forms': passenger_forms
            })

    else:
        form = BookingForm()

    # Ensure passenger forms are created based on persisted `num_passengers` value
    if num_passengers > 0:
        passenger_forms = [
            PassangerForm(flight_price=fp,prefix=f"Passenger_{i}") for i in range(1, num_passengers + 1)
        ]

    return render(request, 'booking.html', {
        'form': form,
        'passenger_forms': passenger_forms,
        'flight': flight,
        'num_passengers': num_passengers,
    })
@login_required
def reservation_view(request, booking_id):
    booking=Booking.objects.get(booking_id=booking_id)
    photo=static(code_photo_dict[booking.flight_id.destination])
    city=city_airport_dict[booking.flight_id.destination]
    return render(request,'reservation.html',{'booking': booking,'photo':photo,'city':city})

def get_ads(request):
    ads=Ad.objects.all()
    ads_prep=[ {"ad_id": ad.ad_id, "title": ad.ad_title, "content": ad.ad_content,"image":ad.ad_img}
        for ad in ads]
    return JsonResponse({"ads": ads_prep})
class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
def PrivacyView(request):
    return render(request, 'privacy.html')