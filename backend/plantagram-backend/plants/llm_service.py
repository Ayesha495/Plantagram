import json
import time
from django.conf import settings
from openai import OpenAI

class PlantCareLLM:
    """
    Optimized Hugging Face LLM service - ONE call per plant
    Gets care data AND Urdu translations in a single request
    """
    
    def __init__(self):
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=settings.HF_TOKEN,
        )
    
    def get_complete_plant_data(self, plant_name, scientific_name='', family=''):
        """
        Get ALL plant data (care info + Urdu translations) in ONE LLM call
        
        Args:
            plant_name: Common plant name in English
            scientific_name: Scientific/Latin name
            family: Plant family
        
        Returns:
            dict: Complete plant data with care info and Urdu translations
        """
        
        # Combined prompt - asks for everything at once
        prompt = f"""You are a professional botanist. Provide care information AND Urdu translations for this plant.

Plant: {plant_name}
Scientific Name: {scientific_name}
Family: {family}

Respond with ONLY a JSON object (no markdown, no explanations):

{{
  "watering_days": <number: days between watering>,
  "sunlight": "<Full Sun|Partial Sun|Indirect Light|Low Light|Shade>",
  "care_level": "<Easy|Medium|Hard>",
  "temperature_min": <celsius number>,
  "temperature_max": <celsius number>,
  "humidity": "<High|Medium|Low>",
  "category": "<Flowering|Foliage|Succulent|Cactus|Herb|Vegetable|Fruit|Tree|Vine|Fern>",
  "is_beginner_friendly": <true|false>,
  "care_tips": "<brief English care tips>",
  "name_urdu": "<plant name in Urdu script>",
  "scientific_name_urdu": "<scientific name in Urdu script>",
  "description_urdu": "<brief description in Urdu: 1-2 sentences about the plant>",
  "care_tips_urdu": "<care tips translated to Urdu>"
}}

Provide accurate botanical data and proper Urdu translations."""

        try:
            print(f"  🤖 Getting complete data for {plant_name}...")
            
            chat_completion = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,  # Increased for complete response
                temperature=0.3,
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # Clean markdown
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON
            complete_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['watering_days', 'sunlight', 'care_level', 'name_urdu']
            if not all(field in complete_data for field in required_fields):
                print(f"  ⚠️ Missing required fields in response")
                return None
            
            print(f"  ✅ Got complete data")
            print(f"     English: {plant_name}")
            print(f"     Urdu: {complete_data['name_urdu']}")
            print(f"     Watering: every {complete_data['watering_days']} days")
            print(f"     Care Level: {complete_data['care_level']}")
            
            # Rate limiting
            time.sleep(2)  # 2 seconds between requests
            
            return complete_data
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️ Failed to parse response: {e}")
            print(f"  Response: {response_text[:300]}")
            return None
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def test_connection(self):
        """
        Test if the optimized service works
        """
        try:
            print("\n=== Testing Optimized LLM Service ===\n")
            print("Making ONE call to get care data + translations...\n")
            
            test_data = self.get_complete_plant_data("Rose", "Rosa", "Rosaceae")
            
            if test_data and all(key in test_data for key in ['watering_days', 'name_urdu']):
                print("\n✅ Service working! Got everything in one call:")
                print(json.dumps(test_data, indent=2, ensure_ascii=False))
                print(f"\n💰 API calls used: 1 (optimized!)")
                return True
            else:
                print("\n❌ Service failed")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False