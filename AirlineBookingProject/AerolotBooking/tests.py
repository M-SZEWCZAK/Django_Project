from zoneinfo import ZoneInfo

from django.test import TestCase
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import make_aware

from .models import Flight,CustomUser,Ad,Booking
#Model tests
class FlightModelTests(TestCase):

    def test_create_flight(self):
        flight = Flight.objects.create(
            flight_id=1,
            flight_code="FL123",
            origin="WAW",
            destination="BUD",
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
            price=Decimal("100.50"),
            duration="2h"
        )
        self.assertEqual(flight.flight_code, "FL123")
        self.assertEqual(flight.origin, "WAW")
        self.assertEqual(flight.destination, "BUD")
        self.assertEqual(flight.price, Decimal("100.50"))
        self.assertEqual(flight.duration, "2h")
class BookingModelTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="testuser@example.com", password="password123")
        self.flight = Flight.objects.create(
            flight_id=1,
            flight_code="AL123",
            origin="WAW",
            destination="BUD",
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
            price=Decimal("150.00"),
            duration="3h"
        )

    def test_create_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            flight_id=self.flight,
            passanger_number=2,
            passengers=[{"name": "Passenger 1"}, {"name": "Passenger 2"}],
            booking_date=timezone.now()
        )

        self.assertEqual(booking.user.email, "testuser@example.com")
        self.assertEqual(booking.flight_id.flight_code, "AL123")
        self.assertEqual(booking.passanger_number, 2)
        self.assertEqual(len(booking.passengers), 2)
        self.assertEqual(booking.passengers[0]["name"], "Passenger 1")
        self.assertEqual(booking.passengers[1]["name"], "Passenger 2")
class AdModelTests(TestCase):

    def test_create_ad(self):
        ad = Ad.objects.create(
            ad_title="Special Offer",
            ad_content="Get 50% off on your next flight!",
            ad_img="special_offer.jpg"
        )

        self.assertEqual(ad.ad_title, "Special Offer")
        self.assertEqual(ad.ad_content, "Get 50% off on your next flight!")
        self.assertEqual(ad.ad_img, "special_offer.jpg")

    def test_ad_content_length(self):
        long_content = "A" * 500
        ad = Ad.objects.create(
            ad_title="Long Ad",
            ad_content=long_content,
            ad_img="long_ad.jpg"
        )

        self.assertEqual(ad.ad_content, long_content)

#Views tests
class HomeViewTests(TestCase):
    def setUp(self):
        self.ad1 = Ad.objects.create(ad_title="Ad1", ad_content="Content1",ad_img="static/img/ad1.jpg")
        self.ad2 = Ad.objects.create(ad_title="Ad2", ad_content="Content2",ad_img="static/img/ad2.jpg")

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        ads = response.context['ads']
        ad1=ads[0]
        ad2=ads[1]
        self.assertEqual(ad1.ad_title, "Ad1")
        self.assertEqual(ad1.ad_content, "Content1")
        self.assertEqual(ad1.ad_img, "static/img/ad1.jpg")
        self.assertEqual(ad2.ad_title, "Ad2")
        self.assertEqual(ad2.ad_content, "Content2")
        self.assertEqual(ad2.ad_img, "static/img/ad2.jpg")





class FlightListViewTests(TestCase):
    warsaw_tz = ZoneInfo("Europe/Warsaw")

    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(email='admin@example.com', password='admin123')


        self.flight = Flight.objects.create(
            flight_id=1,
            flight_code="AL123",
            origin="WAW",
            destination="BUD",
            departure_time= make_aware(datetime(2025, 1, 16, 15, 0),timezone=self.warsaw_tz),
            arrival_time= make_aware(datetime(2025, 1, 16, 17, 0),timezone=self.warsaw_tz),
            price="150.00",
            duration="2h"
        )

    def test_flights_list_view_for_admin(self):
        # Log in as admin
        self.client.login(email='admin@example.com', password='admin123')

        # Get the flight list page
        response = self.client.get(reverse('flights_list'))
        flight=response.context['flights'][0]
        # Check if the flight is displayed on the page
        self.assertEqual(flight.flight_code, "AL123")
        self.assertEqual(flight.origin, "WAW")
        self.assertEqual(flight.destination, "BUD")
        self.assertEqual(flight.departure_time,  make_aware(datetime(2025, 1, 16, 15, 0),timezone=self.warsaw_tz))
        self.assertEqual(flight.arrival_time, make_aware(datetime(2025, 1, 16, 17, 0),timezone=self.warsaw_tz ))
        self.assertEqual(flight.price, Decimal("150.00"))
        self.assertEqual(flight.duration, "2h")



    def test_flights_list_view_for_non_admin(self):
        # Create a regular user
        self.client.login(email='user@example.com', password='password123')

        # Try to access the flight list page
        response = self.client.get(reverse('flights_list'))

        # Check if the response is a redirect (as the user is not an admin)
        self.assertEqual(response.status_code, 302)
class DeleteUserViewTests(TestCase):
    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(
            password="adminpass",
            email="admin@example.com"
        )
        self.client.login(email="admin@example.com", password="adminpass")

        self.user = CustomUser.objects.create_user(
            password="userpass",
            email="user1@example.com"
        )

    def test_delete_user_post(self):
        response = self.client.post(reverse('delete_user', args=[self.user.id]))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(id=self.user.id)
class EditFlightViewTests(TestCase):
    warsaw_tz = ZoneInfo("Europe/Warsaw")
    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(
            password="adminpass",
            email="admin@example.com"
        )
        self.client.login(username="admin@example.com", password="adminpass")

        self.flight = Flight.objects.create(
            flight_id=1,
            flight_code="AL123",
            origin="WAW",
            destination="BUD",
            departure_time=make_aware(datetime(2025, 2, 18, 15, 0), timezone=self.warsaw_tz),
            arrival_time=make_aware(datetime(2025, 2, 18, 17, 0), timezone=self.warsaw_tz),
            price="150.00",
            duration="2h"
        )

    def test_edit_flight_get(self):
        response = self.client.get(reverse('edit_flight', args=[self.flight.flight_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create/edit_flight.html')

    def test_edit_flight_post(self):
        response = self.client.post(reverse('edit_flight', args=[self.flight.flight_id]), {
            'flight_code': "AL456",
            'origin': "WAW",
            'destination': "BUD",
            'departure_time':make_aware(datetime(2025, 2, 18, 16, 0), timezone=self.warsaw_tz),
            'arrival_time': make_aware(datetime(2025, 2, 18, 18, 0), timezone=self.warsaw_tz),
            'price': "200.00",
            'duration': "2h"
        })

        self.assertEqual(response.status_code, 302)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.flight_code, "AL456")
        self.assertEqual(self.flight.price, Decimal("200.00"))
class BookingViewTests(TestCase):
    warsaw_tz = ZoneInfo("Europe/Warsaw")

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            password='password123',
            email="user@example.com"
        )
        self.client.login(username='user@example.com', password='password123')

        self.flight = Flight.objects.create(
            flight_id=1,
            flight_code="AL123",
            origin="WAW",
            destination="BUD",
            departure_time=make_aware(datetime(2025, 1, 18, 16, 0), timezone=self.warsaw_tz),
            arrival_time=make_aware(datetime(2025, 1, 18, 18, 0), timezone=self.warsaw_tz),
            price=Decimal("150.00"),
            duration="2h"
        )

    def test_booking_view_get(self):
        response = self.client.get(reverse('booking', args=[self.flight.flight_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking.html')
        self.assertIn('form', response.context)
        self.assertIn('passenger_forms', response.context)
        self.assertEqual(response.context['flight'], self.flight)

    def test_booking_view_post_valid_data(self):
        post_data = {
            'num_passengers': '2',
            'Passenger_1-name': 'Vladimir',
            'Passenger_1-surname':'Lenin',
            'Passenger_1-nationality': 'rosyjskie',
            'Passenger_1-age': 54,
            'Passenger_1-luggage': '1',
            'Passenger_2-name': 'Ernesto',
            'Passenger_2-surname': 'Guevara',
            'Passenger_2-nationality': 'argentyńskie',
            'Passenger_2-age': 39,
            'Passenger_2-luggage': '1',

        }
        response = self.client.post(reverse('booking', args=[self.flight.flight_id]), post_data)
        self.assertEqual(response.status_code, 200)  # Ensure booking finishes

        bookings = Booking.objects.filter(flight_id=self.flight, user=self.user)
        self.assertEqual(bookings.count(), 1)
        booking = bookings.first()

        self.assertEqual(booking.passanger_number, 2)
        self.assertEqual(len(booking.passengers), 2)
        self.assertEqual(booking.passengers[0]['name'], 'Vladimir')
        self.assertEqual(booking.passengers[1]['name'], 'Ernesto')

        # Verify total price calculation
        luggage_coeffs = {'0': 1.0, '1': 1.1, '2': 1.15, '3': 1.2}
        expected_price = (
            self.flight.price * Decimal(luggage_coeffs['1']) +
            self.flight.price * Decimal(luggage_coeffs['1'])
        ).quantize(Decimal('.01'))
        self.assertEqual(response.context['total_price'], expected_price)

    def test_booking_view_post_invalid_data(self):
        # Test POST request with invalid data
        post_data = {
            'num_passengers': '2',
            'Passenger_1-name': 'Vladimir',
            'Passenger_1-surname': 'lenin',
            'Passenger_1-nationality': 'rosyjskie',
            'Passenger_1-age': 54,
            'Passenger_1-luggage': '1',
            'Passenger_2-name': 'Ernesto',
            'Passenger_2-surname': 'Guevara lynch',
            'Passenger_2-nationality': 'Argentyńskie',
            'Passenger_2-age': 39,
            'Passenger_2-luggage': '1',
        }
        response = self.client.post(reverse('booking', args=[self.flight.flight_id]), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking.html')
        self.assertIn('form', response.context)
        self.assertIn('passenger_forms', response.context)

        bookings = Booking.objects.filter(flight_id=self.flight, user=self.user)
        self.assertEqual(bookings.count(), 0)
