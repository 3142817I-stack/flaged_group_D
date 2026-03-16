from django.core.management.base import BaseCommand
from django.db import connection
from flagd.models import User, Flag
import hashlib


class Command(BaseCommand):
    help = 'Populates the database with dummy users and all 192 UN member countries'

    def handle(self, *args, **options):
        self.stdout.write('Populating database...')
        
        # Clear existing data
        User.objects.all().delete()
        Flag.objects.all().delete()
        
        # Reset SQLite auto-increment counters
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='flag'")
        
        self.stdout.write('Cleared existing data and reset ID counters.')
        
        # Create dummy users
        self.create_users()
        
        # Create flags for all 192 UN countries
        self.create_flags()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
    
    def create_users(self):
        """Create dummy users with varying scores for leaderboard testing."""
        users_data = [
            # Top players
            {'username': 'FlagMaster', 'email': 'flagmaster@example.com', 'score': 9850, 'is_guest': False},
            {'username': 'GeographyKing', 'email': 'geoking@example.com', 'score': 9200, 'is_guest': False},
            {'username': 'WorldExplorer', 'email': 'explorer@example.com', 'score': 8750, 'is_guest': False},
            {'username': 'MapWhiz', 'email': 'mapwhiz@example.com', 'score': 8500, 'is_guest': False},
            {'username': 'FlagNinja', 'email': 'ninja@example.com', 'score': 8100, 'is_guest': False},
            
            # Mid-tier players
            {'username': 'TravelBug', 'email': 'travel@example.com', 'score': 6500, 'is_guest': False},
            {'username': 'AtlasFan', 'email': 'atlas@example.com', 'score': 5800, 'is_guest': False},
            {'username': 'GlobeTrotter', 'email': 'globe@example.com', 'score': 5200, 'is_guest': False},
            {'username': 'FlagLover', 'email': 'lover@example.com', 'score': 4800, 'is_guest': False},
            {'username': 'CountryQuiz', 'email': 'quiz@example.com', 'score': 4200, 'is_guest': False},
            {'username': 'MapReader', 'email': 'reader@example.com', 'score': 3800, 'is_guest': False},
            {'username': 'GeoGenius', 'email': 'genius@example.com', 'score': 3500, 'is_guest': False},
            
            # Lower-tier players
            {'username': 'BeginnerBob', 'email': 'bob@example.com', 'score': 2100, 'is_guest': False},
            {'username': 'NewPlayer123', 'email': 'newplayer@example.com', 'score': 1500, 'is_guest': False},
            {'username': 'LearningFlags', 'email': 'learning@example.com', 'score': 1200, 'is_guest': False},
            {'username': 'CasualGamer', 'email': 'casual@example.com', 'score': 800, 'is_guest': False},
            {'username': 'JustStarted', 'email': 'started@example.com', 'score': 450, 'is_guest': False},
            {'username': 'FlagNewbie', 'email': 'newbie@example.com', 'score': 200, 'is_guest': False},
            
            # Guest users
            {'username': 'Guest_7392', 'email': 'guest7392@temp.com', 'score': 3200, 'is_guest': True},
            {'username': 'Guest_4521', 'email': 'guest4521@temp.com', 'score': 1800, 'is_guest': True},
            {'username': 'Guest_8834', 'email': 'guest8834@temp.com', 'score': 950, 'is_guest': True},
            {'username': 'Guest_2156', 'email': 'guest2156@temp.com', 'score': 600, 'is_guest': True},
            {'username': 'Guest_9012', 'email': 'guest9012@temp.com', 'score': 150, 'is_guest': True},
        ]
        
        for user_data in users_data:
            # Create a simple hash for the password (SHA256 produces 64 hex chars, fits in max_length=128)
            password_hash = hashlib.sha256('password123'.encode()).hexdigest()
            
            User.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=password_hash,
                is_guest=user_data['is_guest'],
                score=user_data['score']
            )
        
        self.stdout.write(f'Created {len(users_data)} dummy users.')
    
    def create_flags(self):
        """Create flags for all 192 UN member countries with their continents."""
        
        # All 192 UN member countries organized by continent
        countries_by_continent = {
            'Africa': [
                'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi',
                'Cabo Verde', 'Cameroon', 'Central African Republic', 'Chad', 'Comoros',
                'Congo', 'Democratic Republic of the Congo', 'Djibouti', 'Egypt',
                'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon',
                'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Kenya',
                'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali',
                'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger',
                'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles',
                'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan',
                'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
            ],
            'Americas': [
                'Antigua and Barbuda', 'Argentina', 'Bahamas', 'Barbados', 'Belize',
                'Bolivia', 'Brazil', 'Canada', 'Chile', 'Colombia', 'Costa Rica',
                'Cuba', 'Dominica', 'Dominican Republic', 'Ecuador', 'El Salvador',
                'Grenada', 'Guatemala', 'Guyana', 'Haiti', 'Honduras', 'Jamaica',
                'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Saint Kitts and Nevis',
                'Saint Lucia', 'Saint Vincent and the Grenadines', 'Suriname',
                'Trinidad and Tobago', 'United States', 'Uruguay', 'Venezuela'
            ],
            'Asia': [
                'Afghanistan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei', 'Cambodia',
                'China', 'Cyprus', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel',
                'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos',
                'Lebanon', 'Malaysia', 'Maldives', 'Mongolia', 'Myanmar', 'Nepal',
                'North Korea', 'Oman', 'Pakistan', 'Palestine', 'Philippines', 'Qatar',
                'Saudi Arabia', 'Singapore', 'South Korea', 'Sri Lanka', 'Syria',
                'Tajikistan', 'Thailand', 'Timor-Leste', 'Turkmenistan', 'United Arab Emirates',
                'Uzbekistan', 'Vietnam', 'Yemen'
            ],
            'Europe': [
                'Albania', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan', 'Belarus',
                'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Czech Republic',
                'Denmark', 'Estonia', 'Finland', 'France', 'Georgia', 'Germany', 'Greece',
                'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Liechtenstein',
                'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro',
                'Netherlands', 'North Macedonia', 'Norway', 'Poland', 'Portugal', 'Romania',
                'Russia', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain',
                'Sweden', 'Switzerland', 'Turkey', 'Ukraine', 'United Kingdom', 'Vatican City'
            ],
            'Oceania': [
                'Australia', 'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia',
                'Nauru', 'New Zealand', 'Palau', 'Papua New Guinea', 'Samoa',
                'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu'
            ]
        }
        
        # Create a flat list of all countries with their continents
        all_countries = []
        for continent, countries in countries_by_continent.items():
            for country in countries:
                all_countries.append((country, continent))
        
        # Sort alphabetically by country name to ensure proper ID ordering
        all_countries.sort(key=lambda x: x[0])
        
        flag_count = 0
        for country, continent in all_countries:
            Flag.objects.create(
                country_name=country,
                continent=continent
            )
            flag_count += 1
        
        self.stdout.write(f'Created {flag_count} flags for UN member countries.')
