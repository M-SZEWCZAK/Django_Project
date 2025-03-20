from datetime import datetime, date
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

from .models import CustomUser, Flight, Ad
from django.contrib.auth import authenticate, login

Airport_choices=[
    ('WAW', 'Warszawa Chopin'),
    ('BUD','Budapeszt'),
    ('DXB','Dubaj'),
    ('ORD','Chicago O\'Hare'),
    ('NAP','Neapol'),
    ('BGO','Bergen'),
    ('OSL','Oslo'),
    ('CDG','Paryż CDG'),
    ('LHR','Londyn Heathrow'),
    ('FRA','Frankfurt nad Menem'),
    ('MAD','Madryt'),
    ('KRK','Kraków'),
    ('GRU','Sao Paulo'),
    ('EVN','Erewań'),
    ('NQZ','Astana'),
    ('NRT','Tokio Narita'),
    ('LIM','Lima'),
    ('IST','Stambuł'),
]
Luggage_choices=[(0,'Only 1 free piece 20x25x40cm'),
                 (1,'Add cabin bag'),
                 (2,'Add registered 10kg bag'),
                 (3,'Add registered 20kg bag'),]
class FlightForm(forms.Form):
    miejsce_wylotu = forms.ChoiceField(choices=Airport_choices, label='Miejsce Wylotu', widget=forms.Select)
    miejsce_przylotu = forms.ChoiceField(choices=Airport_choices, label='Miejsce Przylotu', widget=forms.Select)
    data=forms.DateField(label='Data wylotu',widget=forms.DateInput(attrs={'type': 'date'}))
    def clean_miejsce_przylotu(self):
        m_w=self.cleaned_data['miejsce_wylotu']
        m_p=self.cleaned_data['miejsce_przylotu']
        if m_w==m_p:
            raise ValidationError("Miejsce przylotu musi być różne od miejsca wylotu!")
        return m_p
    def clean_data(self):
        d_w=self.cleaned_data['data']
        if d_w<date.today():
            raise ValidationError("Wybrany dzień minął!")
        return d_w
class PassangerForm(forms.Form):
    name = forms.CharField(max_length=50, label="Imię")
    surname = forms.CharField(max_length=50, label="Nazwisko")
    nationality=forms.CharField(max_length=60, label="Obywatelstwo")
    age=forms.IntegerField(label="Wiek")
    luggage=forms.ChoiceField(label='Bagaż')

    def __init__(self, *args, flight_price=None, **kwargs):
        super().__init__(*args, **kwargs)
        if flight_price:
            luggage_choices = [
                (0, 'Tylko 1 sztuka 20x25x40cm - w cenie'),
                (1, f'Dodaj bagaż podręczny  +{round(0.1*flight_price,2)} PLN'),
                (2, f'Dodaj 10kg bagaż rejestrowy  +{round(0.15*flight_price,2)} PLN'),
                (3, f'Dodaj 10kg bagaż rejestrowy  +{round(0.2*flight_price,2)} PLN'), ]
        else:
            luggage_choices = [
                (0, 'Tylko 1 sztuka 20x25x40cm'),
                (1, 'Dodaj bagaż podręczny'),
                (2, 'Dodaj 10kg bagaż rejestrowy'),
                (3, 'Dodaj 10kg bagaż rejestrowy'), ]

        # Update the luggage field choices
        self.fields['luggage'].choices = luggage_choices
    def clean_age(self):
        age=self.cleaned_data['age']
        if age<0:
            raise ValidationError("Wiek musi być nieujemny!")
        if age>125:
            raise ValidationError("Podany wiek jest wyższy niż wiek najstarszych ludzi na Ziemi!")
        return age
    def clean_name(self):
        name = self.cleaned_data.get('name')
        pattern = r'^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+( [A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?$'
        if not re.match(pattern, name):
            raise forms.ValidationError(
                "Dopuszczalne jest jedno lub dwa imiona! Każde z imion musi zaczynać się wielką literą! Imiona należy oddzielić pojedynczą spacją!"
            )
        return name

    def clean_surname(self):
        surname = self.cleaned_data.get('surname')
        pattern = r'^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+( [A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+|-[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?$'
        if not re.match(pattern, surname):
            raise forms.ValidationError(
                "Każde z nazwisk musi zaczynać się wielką literą! Nazwiska należy oddzielić pojedynczą spacją lub myślnikiem!"
            )
        return surname
    def clean_nationality(self):
        nationality = self.cleaned_data.get('nationality')
        pattern = r'^[a-ząćęłńóśźż]+$'
        if not re.match(pattern, nationality):
            raise forms.ValidationError("Podane obywatestwo musi zawierać wyłącznie małe litery")
        return nationality

class BookingForm(forms.Form):
    num_passengers = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        label="Liczba pasażerów",
        widget=forms.Select(attrs={"onchange": "updatePassengerForms()"}),
    )
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError('Nieprawidłowe login lub hasło')
            self.user = user
class FlightModelForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields=['flight_code','origin','destination','departure_time','arrival_time','price','duration']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
    def clean_flight_code(self):
        flight_code = self.cleaned_data['flight_code']
        pattern=r'^AL[0-9]{2,3}$'
        if not re.match(pattern,flight_code):
            raise ValidationError("Kod lotu musi mieć postać 'ALxxx' lub 'ALxx'!")
        return flight_code
    def clean_destination(self):
        origin = self.cleaned_data['origin']
        destination = self.cleaned_data['destination']
        if origin==destination:
            raise ValidationError("Miejsce docelowe MUSI BYĆ RÓŻNE od miejsca początkowego!")
        return destination
    def clean_departure_time(self):
        departure_time = self.cleaned_data['departure_time']
        if departure_time < timezone.now():
            raise ValidationError("Nie można ustawić daty wylotu w przeszłości!")
        return departure_time

    def clean_arrival_time(self):
        arrival_time = self.cleaned_data['arrival_time']
        if arrival_time < timezone.now():
            raise ValidationError("Nie można ustawić daty przylotu w przeszłości!")
        return arrival_time
    def clean_price(self):
        price = self.cleaned_data['price']
        if price <=0:
            raise ValidationError("Cena musi być dodatnia")
        return price
    def clean_duration(self):
        duration = self.cleaned_data['duration']
        pattern=r'^[1-9]h[1-5][0-9]min$|^[1-9]h[1-9]min$|^[1-5][0-9]min$|^[1-2][0-9]h[0-9]min$|^[1-2][0-9]h[1-5][0-9]min$|^[1-9]h$|^[1-2]$'
        if not re.match(pattern, duration):
            raise ValidationError("Pole duration ma postać czasu podanego w h i min, bez spacji! Brak lotów krótszych niż 10 min i o długości większej niż 24h!")
        return duration
class MultFlightModelForm(forms.Form):
    flight_code = forms.CharField()
    origin = forms.CharField()
    destination = forms.CharField()
    price = forms.DecimalField()
    duration = forms.CharField()
    weeks=forms.IntegerField()
    first_departure = forms.DateTimeField(label="Data i czas wylotu pierwszego lotu", widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'))
    first_arrival = forms.DateTimeField(label="Data i czas przylotu pierwszego lotu", widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'))
    def clean_weeks(self):
        weeks = self.cleaned_data['weeks']
        if weeks <= 0:
            raise ValidationError('Liczba tygodni musi być dodatnia!')
        return weeks
    def clean_flight_code(self):
        flight_code = self.cleaned_data['flight_code']
        pattern=r'^AL[0-9]{2,3}$'
        if not re.match(pattern,flight_code):
            raise ValidationError("Kod lotu musi mieć postać 'ALxxx' lub 'ALxx'!")
        return flight_code
    def clean_origin(self):
        origin = self.cleaned_data['origin']
        pattern = r'^[A-Z]{3}$'
        if not re.match(pattern, origin):
            raise ValidationError("Miejsce startu musi być zadane 3 literowym (wielkie litery) kodem IATA!")
        return origin
    def clean_destination(self):
        origin = self.cleaned_data['origin']
        destination = self.cleaned_data['destination']
        pattern=r'^[A-Z]{3}$'
        if not re.match(pattern,destination):
            raise ValidationError("Miejsce docelowe musi być zadane 3 literowym (wielkie litery) kodem IATA!")
        if origin==destination:
            raise ValidationError("Miejsce docelowe MUSI BYĆ RÓŻNE od miejsca początkowego!")
        return destination
    def clean_departure_time(self):
        departure_time = self.cleaned_data['departure_time']
        if departure_time < timezone.now():
            raise ValidationError("Nie można ustawić daty wylotu w przeszłości!")
        return departure_time

    def clean_arrival_time(self):
        arrival_time = self.cleaned_data['arrival_time']
        if arrival_time < timezone.now():
            raise ValidationError("Nie można ustawić daty przylotu w przeszłości!")
        return arrival_time
    def clean_price(self):
        price = self.cleaned_data['price']
        if price <=0:
            raise ValidationError("Cena musi być dodatnia")
        return price
    def clean_duration(self):
        duration = self.cleaned_data['duration']
        pattern=r'^[1-9]h[1-5][0-9]min$|^[1-9]h[1-9]min$|^[1-5][0-9]min$|^[1-2][0-9]h[0-9]min$|^[1-2][0-9]h[1-5][0-9]min$|^[1-9]h$|^[1-2]$'
        if not re.match(pattern, duration):
            raise ValidationError("Pole duration ma postać czasu podanego w h i min, bez spacji! Brak lotów krótszych niż 10 min i o długości większej niż 24h!")
        return duration
class AdModelForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields=['ad_title','ad_content','ad_img']

