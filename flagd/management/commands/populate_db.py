from django.core.management.base import BaseCommand
from django.db import connection
from flagd.models import User, Flag, CountryAlias
import hashlib


class Command(BaseCommand):
    help = 'Populates the database with dummy users and all 192 UN member countries'

    def handle(self, *args, **options):
        self.stdout.write('Populating database...')
        
        # Clear existing data
        CountryAlias.objects.all().delete()
        User.objects.all().delete()
        Flag.objects.all().delete()
        
        # Reset SQLite auto-increment counters
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='flag'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='country_alias'")
        
        self.stdout.write('Cleared existing data and reset ID counters.')
        
        # Create dummy users
        self.create_users()
        
        # Create flags for all 192 UN countries
        self.create_flags()
        
        # Create country aliases
        self.create_country_aliases()
        
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
        """Create flags for all 192 UN member countries with their continents and country codes."""
        
        # Mapping of country names to ISO 3166-1 alpha-2 codes
        country_codes = {
            'Afghanistan': 'af',
            'Albania': 'al',
            'Algeria': 'dz',
            'Andorra': 'ad',
            'Angola': 'ao',
            'Antigua and Barbuda': 'ag',
            'Argentina': 'ar',
            'Armenia': 'am',
            'Australia': 'au',
            'Austria': 'at',
            'Azerbaijan': 'az',
            'Bahamas': 'bs',
            'Bahrain': 'bh',
            'Bangladesh': 'bd',
            'Barbados': 'bb',
            'Belarus': 'by',
            'Belgium': 'be',
            'Belize': 'bz',
            'Benin': 'bj',
            'Bhutan': 'bt',
            'Bolivia': 'bo',
            'Bosnia and Herzegovina': 'ba',
            'Botswana': 'bw',
            'Brazil': 'br',
            'Brunei': 'bn',
            'Bulgaria': 'bg',
            'Burkina Faso': 'bf',
            'Burundi': 'bi',
            'Cabo Verde': 'cv',
            'Cambodia': 'kh',
            'Cameroon': 'cm',
            'Canada': 'ca',
            'Central African Republic': 'cf',
            'Chad': 'td',
            'Chile': 'cl',
            'China': 'cn',
            'Colombia': 'co',
            'Comoros': 'km',
            'Congo': 'cg',
            'Costa Rica': 'cr',
            'Croatia': 'hr',
            'Cuba': 'cu',
            'Cyprus': 'cy',
            'Czech Republic': 'cz',
            'Democratic Republic of the Congo': 'cd',
            'Denmark': 'dk',
            'Djibouti': 'dj',
            'Dominica': 'dm',
            'Dominican Republic': 'do',
            'Ecuador': 'ec',
            'Egypt': 'eg',
            'El Salvador': 'sv',
            'Equatorial Guinea': 'gq',
            'Eritrea': 'er',
            'Estonia': 'ee',
            'Eswatini': 'sz',
            'Ethiopia': 'et',
            'Fiji': 'fj',
            'Finland': 'fi',
            'France': 'fr',
            'Gabon': 'ga',
            'Gambia': 'gm',
            'Georgia': 'ge',
            'Germany': 'de',
            'Ghana': 'gh',
            'Greece': 'gr',
            'Grenada': 'gd',
            'Guatemala': 'gt',
            'Guinea': 'gn',
            'Guinea-Bissau': 'gw',
            'Guyana': 'gy',
            'Haiti': 'ht',
            'Honduras': 'hn',
            'Hungary': 'hu',
            'Iceland': 'is',
            'India': 'in',
            'Indonesia': 'id',
            'Iran': 'ir',
            'Iraq': 'iq',
            'Ireland': 'ie',
            'Israel': 'il',
            'Italy': 'it',
            'Ivory Coast': 'ci',
            'Jamaica': 'jm',
            'Japan': 'jp',
            'Jordan': 'jo',
            'Kazakhstan': 'kz',
            'Kenya': 'ke',
            'Kiribati': 'ki',
            'Kuwait': 'kw',
            'Kyrgyzstan': 'kg',
            'Laos': 'la',
            'Latvia': 'lv',
            'Lebanon': 'lb',
            'Lesotho': 'ls',
            'Liberia': 'lr',
            'Libya': 'ly',
            'Liechtenstein': 'li',
            'Lithuania': 'lt',
            'Luxembourg': 'lu',
            'Madagascar': 'mg',
            'Malawi': 'mw',
            'Malaysia': 'my',
            'Maldives': 'mv',
            'Mali': 'ml',
            'Malta': 'mt',
            'Marshall Islands': 'mh',
            'Mauritania': 'mr',
            'Mauritius': 'mu',
            'Mexico': 'mx',
            'Micronesia': 'fm',
            'Moldova': 'md',
            'Monaco': 'mc',
            'Mongolia': 'mn',
            'Montenegro': 'me',
            'Morocco': 'ma',
            'Mozambique': 'mz',
            'Myanmar': 'mm',
            'Namibia': 'na',
            'Nauru': 'nr',
            'Nepal': 'np',
            'Netherlands': 'nl',
            'New Zealand': 'nz',
            'Nicaragua': 'ni',
            'Niger': 'ne',
            'Nigeria': 'ng',
            'North Korea': 'kp',
            'North Macedonia': 'mk',
            'Norway': 'no',
            'Oman': 'om',
            'Pakistan': 'pk',
            'Palau': 'pw',
            'Palestine': 'ps',
            'Panama': 'pa',
            'Papua New Guinea': 'pg',
            'Paraguay': 'py',
            'Peru': 'pe',
            'Philippines': 'ph',
            'Poland': 'pl',
            'Portugal': 'pt',
            'Qatar': 'qa',
            'Romania': 'ro',
            'Russia': 'ru',
            'Rwanda': 'rw',
            'Saint Kitts and Nevis': 'kn',
            'Saint Lucia': 'lc',
            'Saint Vincent and the Grenadines': 'vc',
            'Samoa': 'ws',
            'San Marino': 'sm',
            'Sao Tome and Principe': 'st',
            'Saudi Arabia': 'sa',
            'Senegal': 'sn',
            'Serbia': 'rs',
            'Seychelles': 'sc',
            'Sierra Leone': 'sl',
            'Singapore': 'sg',
            'Slovakia': 'sk',
            'Slovenia': 'si',
            'Solomon Islands': 'sb',
            'Somalia': 'so',
            'South Africa': 'za',
            'South Korea': 'kr',
            'South Sudan': 'ss',
            'Spain': 'es',
            'Sri Lanka': 'lk',
            'Sudan': 'sd',
            'Suriname': 'sr',
            'Sweden': 'se',
            'Switzerland': 'ch',
            'Syria': 'sy',
            'Tajikistan': 'tj',
            'Tanzania': 'tz',
            'Thailand': 'th',
            'Timor-Leste': 'tl',
            'Togo': 'tg',
            'Tonga': 'to',
            'Trinidad and Tobago': 'tt',
            'Tunisia': 'tn',
            'Turkey': 'tr',
            'Turkmenistan': 'tm',
            'Tuvalu': 'tv',
            'Uganda': 'ug',
            'Ukraine': 'ua',
            'United Arab Emirates': 'ae',
            'United Kingdom': 'gb',
            'United States': 'us',
            'Uruguay': 'uy',
            'Uzbekistan': 'uz',
            'Vanuatu': 'vu',
            'Vatican City': 'va',
            'Venezuela': 've',
            'Vietnam': 'vn',
            'Yemen': 'ye',
            'Zambia': 'zm',
            'Zimbabwe': 'zw'
        }
        
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
            code = country_codes.get(country, '')
            Flag.objects.create(
                country_name=country,
                country_code=code,
                continent=continent
            )
            flag_count += 1
        
        self.stdout.write(f'Created {flag_count} flags for UN member countries.')
    
    def create_country_aliases(self):
        """Create alternative names for countries to help with user input matching."""
        
        # Mapping of country names to their common alternative names
        # Format: 'Official Country Name': ['alias1', 'alias2', ...]
        country_aliases = {
            # Europe
            'Czech Republic': ['Czechia'],
            'United Kingdom': ['UK', 'Britain', 'Great Britain'],
            'Netherlands': ['Holland'],
            'North Macedonia': ['Macedonia'],
            
            # Africa
            'Central African Republic': ['CAR'],
            'Democratic Republic of the Congo': ['DRC', 'DR Congo'],
            'Congo': ['Republic of the Congo'],
            'Ivory Coast': ["Côte d'Ivoire", "Cote d'Ivoire"],
            'Cabo Verde': ['Cape Verde'],
            'Eswatini': ['Swaziland'],
            'Sao Tome and Principe': ['São Tomé and Príncipe', 'Sao Tome'],
            
            # Americas
            'United States': ['USA', 'US', 'America', 'United States of America'],
            'Trinidad and Tobago': ['Trinidad & Tobago'],
            'Saint Kitts and Nevis': ['St. Kitts and Nevis', 'St Kitts and Nevis'],
            'Saint Lucia': ['St. Lucia', 'St Lucia'],
            'Saint Vincent and the Grenadines': ['St. Vincent and the Grenadines', 'St Vincent and the Grenadines', 'St Vincent and Grenadines'],
            'Antigua and Barbuda': ['Antigua & Barbuda'],
            
            # Asia
            'South Korea': ['Republic of Korea', 'Korea'],
            'North Korea': ['DPRK', 'Democratic People\'s Republic of Korea'],
            'Myanmar': ['Burma'],
            'Vietnam': ['Viet Nam'],
            'Timor-Leste': ['East Timor'],
            'United Arab Emirates': ['UAE'],
            'Saudi Arabia': ['KSA'],
            
            # Oceania
            'New Zealand': ['Aotearoa'],
            'Palau': ['Republic of Palau'],
            
            # Other common variations
            'Bahamas': ['The Bahamas'],
            'Gambia': ['The Gambia'],
            'Vatican City': ['Vatican'],
        }
        
        alias_count = 0
        for country_name, aliases in country_aliases.items():
            try:
                flag = Flag.objects.get(country_name=country_name)
                for alias in aliases:
                    CountryAlias.objects.create(
                        flag=flag,
                        alias_name=alias
                    )
                    alias_count += 1
            except Flag.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Country not found: {country_name}'))
        
        self.stdout.write(f'Created {alias_count} country aliases.')
