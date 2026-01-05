from django.core.management.base import BaseCommand
from plants.models import Plant
from plants.trefle_service import TrefleAPI
from plants.llm_service import PlantCareLLM
import time

class Command(BaseCommand):
    help = 'Sync plants from Trefle API to database with LLM-powered care data and Urdu translations'
    
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
        llm = PlantCareLLM()  # Initialize LLM service (replaces Google Translate)
        pages = options['pages']
        clear_existing = options['clear']
        
        # Clear existing plants if requested
        if clear_existing:
            Plant.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing plants'))
        
        self.stdout.write(f'Fetching {pages} pages of plants from Trefle API...')
        self.stdout.write(f'Using Hugging Face LLM for care data and Urdu translations...\n')
        
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
                    
                    self.stdout.write(f'  🌱 Processing: {common_name}')
                    
                    # ===== NEW: Get care data AND translations from LLM =====
                    llm_data = llm.get_care_data_with_translations(
                        plant_name=common_name,
                        scientific_name=scientific_name,
                        family=family
                    )
                    
                    if llm_data:
                        # Extract care data from LLM
                        category = llm_data.get('category', 'Foliage')
                        care_level = llm_data.get('care_level', 'Medium')
                        water_frequency_days = llm_data.get('watering_days', 7)
                        sunlight = llm_data.get('sunlight', 'Indirect Light')
                        temperature_min = llm_data.get('temperature_min', 15)
                        temperature_max = llm_data.get('temperature_max', 25)
                        humidity_level = llm_data.get('humidity', 'Medium')
                        is_beginner_friendly = llm_data.get('is_beginner_friendly', False)
                        care_tips = llm_data.get('care_tips', '')
                        
                        # Extract Urdu translations from LLM
                        name_urdu = llm_data.get('name_urdu', common_name)
                        scientific_name_urdu = llm_data.get('scientific_name_urdu', scientific_name)
                        care_tips_urdu = llm_data.get('care_tips_urdu', care_tips)
                        
                        self.stdout.write(self.style.SUCCESS(f'  ✅ LLM provided care data and translations'))
                        self.stdout.write(f'     English: {common_name}')
                        self.stdout.write(f'     Urdu: {name_urdu}')
                        self.stdout.write(f'     Category: {category}')
                        self.stdout.write(f'     Care Level: {care_level}')
                        self.stdout.write(f'     Watering: Every {water_frequency_days} days')
                    else:
                        # Fallback if LLM fails
                        self.stdout.write(self.style.WARNING(f'  ⚠️ LLM failed, using default values'))
                        
                        # Default care values
                        category = 'Foliage'
                        care_level = 'Medium'
                        water_frequency_days = 7
                        sunlight = 'Indirect Light'
                        temperature_min = 15
                        temperature_max = 25
                        humidity_level = 'Medium'
                        is_beginner_friendly = False
                        care_tips = f"{common_name} requires regular care and attention."
                        
                        # Fallback: Keep English as Urdu too
                        name_urdu = common_name
                        scientific_name_urdu = scientific_name
                        care_tips_urdu = care_tips
                    
                    # Build description
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
                    if scientific_name_urdu:
                        description_urdu += f" ({scientific_name_urdu})"
                    if care_tips_urdu:
                        description_urdu += " " + care_tips_urdu

                    # Create or update plant
                    plant, created = Plant.objects.update_or_create(
                        trefle_id=trefle_id,
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
                    
                    # Rate limiting - give LLM API time to breathe
                    time.sleep(2)
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Error processing plant: {e}'))
                    total_skipped += 1
                    continue
            
            # Small delay between pages
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