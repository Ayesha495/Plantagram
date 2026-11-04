from django.core.management.base import BaseCommand
from plants.models import Plant
from plants.trefle_service import TrefleAPI
from plants.llm_service import PlantCareLLM
import time

class Command(BaseCommand):
    help = 'Sync plants from Trefle API with LLM care data and Urdu translations (optimized: 1 call per plant)'
    
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
        llm = PlantCareLLM()
        pages = options['pages']
        clear_existing = options['clear']
        
        # Clear existing plants if requested
        if clear_existing:
            Plant.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing plants'))
        
        self.stdout.write(f'Fetching {pages} pages of plants from Trefle API...')
        self.stdout.write(f'Using OPTIMIZED Hugging Face LLM (1 call per plant)...\n')
        
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
                    
                    # Get family
                    family = plant_data.get('family', '')
                    
                    self.stdout.write(f'\n  🌱 Processing: {common_name}')
                    
                    # ===== OPTIMIZED: Get EVERYTHING in ONE LLM call =====
                    complete_data = llm.get_complete_plant_data(
                        plant_name=common_name,
                        scientific_name=scientific_name,
                        family=family
                    )
                    
                    if complete_data:
                        # Extract care data from LLM
                        category = complete_data.get('category', 'Foliage')
                        care_level = complete_data.get('care_level', 'Medium')
                        water_frequency_days = complete_data.get('watering_days', 7)
                        sunlight = complete_data.get('sunlight', 'Indirect Light')
                        temperature_min = complete_data.get('temperature_min', 15)
                        temperature_max = complete_data.get('temperature_max', 25)
                        humidity_level = complete_data.get('humidity', 'Medium')
                        is_beginner_friendly = complete_data.get('is_beginner_friendly', False)
                        care_tips = complete_data.get('care_tips', '')
                        
                        # Extract Urdu translations from SAME LLM response
                        name_urdu = complete_data.get('name_urdu', common_name)
                        scientific_name_urdu = complete_data.get('scientific_name_urdu', scientific_name)
                        care_tips_urdu = complete_data.get('care_tips_urdu', care_tips)
                        
                        self.stdout.write(self.style.SUCCESS(f'  ✅ Got complete data (1 API call)'))
                    else:
                        # Fallback if LLM fails
                        self.stdout.write(self.style.WARNING(f'  ⚠️ LLM failed, using defaults'))
                        
                        category = 'Foliage'
                        care_level = 'Medium'
                        water_frequency_days = 7
                        sunlight = 'Indirect Light'
                        temperature_min = 15
                        temperature_max = 25
                        humidity_level = 'Medium'
                        is_beginner_friendly = False
                        care_tips = f"{common_name} requires regular care and attention."
                        
                        # Fallback: Use English
                        name_urdu = common_name
                        scientific_name_urdu = scientific_name
                        care_tips_urdu = care_tips
                    
                    # Build English description
                    description = f"{common_name}"
                    if scientific_name:
                        description += f" ({scientific_name})"
                    description += " is a beautiful plant. "
                    
                    if family:
                        description += f"It belongs to the {family} family. "
                    
                    if care_tips:
                        description += care_tips
                    
                    # Build Urdu description
                    description_urdu = f"{name_urdu}"
                    if scientific_name_urdu and scientific_name_urdu != name_urdu:
                        description_urdu += f" ({scientific_name_urdu})"
                    if care_tips_urdu:
                        description_urdu += " " + care_tips_urdu

                    # Create or update plant
                    plant, created = Plant.objects.update_or_create(
                        trefle_id=trefle_id,  # Using trefle_id field for trefle_id
                        defaults={
                            'name': common_name[:200],
                            'name_urdu': name_urdu[:400] if name_urdu else '',
                            'scientific_name': scientific_name[:200] if scientific_name else '',
                            'description': description,
                            'description_urdu': description_urdu if description_urdu else '',
                            'care_level': care_level,
                            'water_frequency_days': water_frequency_days,
                            'sunlight': sunlight,
                            'temperature_min': temperature_min,
                            'temperature_max': temperature_max,
                            'humidity_level': humidity_level,
                            'category': category,
                            'image_url': image_url,
                            'care_tips': care_tips,
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
            
            # Small delay between pages
            if page < pages:
                self.stdout.write('\n  ⏸️  Pausing before next page...\n')
                time.sleep(2)
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ Sync complete!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Results:'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {total_created} plants'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {total_updated} plants'))
        if total_skipped > 0:
            self.stdout.write(self.style.WARNING(f'   Skipped: {total_skipped} plants'))
        self.stdout.write(self.style.SUCCESS(f'   Total in database: {Plant.objects.count()} plants'))
        self.stdout.write(self.style.SUCCESS(f'   API calls used: ~{total_created + total_updated} (75% reduction!)'))
        self.stdout.write('='*60)