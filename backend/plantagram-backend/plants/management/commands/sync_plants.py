from django.core.management.base import BaseCommand
from plants.models import Plant
from plants.trefle_service import TrefleAPI
import time
from googletrans import Translator

class Command(BaseCommand):
    help = 'Sync plants from Trefle API to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=3,
            help='Number of pages to fetch (20 plants per page)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing plants before syncing',
        )
    
    def handle(self, *args, **options):
        api = TrefleAPI()
        translator = Translator()
        pages = options['pages']
        clear_existing = options['clear']
        
        # Clear existing plants if requested
        if clear_existing:
            Plant.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing plants'))
        
        self.stdout.write(f'Fetching {pages} pages of plants from Trefle API...')
        self.stdout.write(f'This will take approximately {pages * 2} seconds...\n')
        
        total_created = 0
        total_updated = 0
        total_skipped = 0
        
        for page in range(1, pages + 1):
            self.stdout.write(f'📄 Fetching page {page}/{pages}...')
            
            data = api.get_plant_list(page=page, per_page=20)
            
            if not data or 'data' not in data:
                self.stdout.write(self.style.ERROR(f'❌ Failed to fetch page {page}'))
                continue
            
            plants_data = data['data']
            
            for plant_data in plants_data:
                try:
                    # Extract data safely
                    trefle_id = plant_data.get('id')
                    if not trefle_id:
                        total_skipped += 1
                        continue
                    
                    # Common name
                    common_name = plant_data.get('common_name') or plant_data.get('slug', 'Unknown Plant')
                    
                    # Scientific name
                    scientific_name = plant_data.get('scientific_name', '')
                    
                    # Get image
                    image_url = ''
                    if plant_data.get('image_url'):
                        image_url = plant_data['image_url']
                    
                    # Determine category based on family or genus
                    category = 'Foliage'  # Default
                    family = plant_data.get('family', '').lower()
                    genus = plant_data.get('genus', '').lower()
                    
                    if 'cact' in family or 'cact' in genus:
                        category = 'Cactus'
                    elif 'succulent' in family or any(word in genus for word in ['aloe', 'echeveria', 'sedum']):
                        category = 'Succulent'
                    elif 'rose' in family or 'rose' in genus:
                        category = 'Flowering'
                    elif any(word in genus for word in ['fern', 'asplen', 'pterid']):
                        category = 'Fern'
                    elif 'vine' in common_name.lower() or 'climbing' in common_name.lower():
                        category = 'Vine'
                    
                    # Default care values (Trefle doesn't provide detailed care info in list view)
                    care_level = 'Medium'
                    water_frequency_days = 7
                    sunlight = 'Indirect Light'
                    
                    # Temperature defaults
                    temperature_min = 15
                    temperature_max = 25
                    
                    
                    # Simple description
                    description = f"{common_name}"
                    if scientific_name:
                        description += f" ({scientific_name})"
                    description += " is a beautiful plant. "
                    
                    if plant_data.get('family'):
                        description += f"It belongs to the {plant_data['family']} family. "
                    
                    # Determine if beginner friendly (simplified logic)
                    is_beginner_friendly = category in ['Succulent', 'Cactus'] or 'easy' in common_name.lower()
                    
                    # Translate to Urdu
                    name_urdu = ''
                    description_urdu = ''
                    
                    try:
                        self.stdout.write(f'  🔤 Translating to Urdu...')
                        
                        # Translate name
                        name_translation = translator.translate(common_name, src='en', dest='ur')
                        name_urdu = name_translation.text if name_translation else ''
                        
                        # Translate description (keep it short for speed)
                        desc_to_translate = f"{common_name} is a beautiful plant."
                        desc_translation = translator.translate(desc_to_translate, src='en', dest='ur')
                        description_urdu = desc_translation.text if desc_translation else ''
                        
                        self.stdout.write(f'  ✅ Urdu: {name_urdu}')
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.5)
                        
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ⚠️ Translation failed: {str(e)}'))
                        name_urdu = common_name  # Fallback to English
                        description_urdu = description

                    # Create or update plant
                    plant, created = Plant.objects.update_or_create(
                        trefle_id=trefle_id,  # Using trefle_id field for trefle_id
                        defaults={
                            'name': common_name[:200],  # Ensure it fits in CharField
                            'name_urdu': name_urdu[:400] if name_urdu else '', 
                            'scientific_name': scientific_name[:200] if scientific_name else '',
                            'description': description,
                            'description_urdu': description_urdu if description_urdu else '',
                            'care_level': care_level,
                            'water_frequency_days': water_frequency_days,
                            'sunlight': sunlight,
                            'temperature_min': temperature_min,
                            'temperature_max': temperature_max,
                            'humidity_level': 'Medium',
                            'category': category,
                            'image_url': image_url,
                            'is_beginner_friendly': is_beginner_friendly,
                            'is_popular': False,
                        }
                    )
                    
                    if created:
                        total_created += 1
                        self.stdout.write(self.style.SUCCESS(f'  ✅ Created: {common_name}'))
                    else:
                        total_updated += 1
                        self.stdout.write(f'  🔄 Updated: {common_name}')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Error processing plant: {e}'))
                    total_skipped += 1
                    continue
            
            # Small delay to be nice to the API
            if page < pages:
                time.sleep(1)
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✅ Sync complete!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Results:'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {total_created} plants'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {total_updated} plants'))
        if total_skipped > 0:
            self.stdout.write(self.style.WARNING(f'   Skipped: {total_skipped} plants'))
        self.stdout.write(self.style.SUCCESS(f'   Total in database: {Plant.objects.count()} plants'))
        self.stdout.write('='*50)