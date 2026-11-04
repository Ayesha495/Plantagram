import requests
from django.conf import settings

class TrefleAPI:
    """
    Service to fetch plant data from Trefle API
    Documentation: https://docs.trefle.io/
    """
    BASE_URL = "https://trefle.io/api/v1"
    
    def __init__(self):
        self.api_key = settings.TREFLE_API_KEY
        if not self.api_key:
            raise ValueError("TREFLE_API_KEY not found in settings. Check your .env file.")
    
    def get_plant_list(self, page=1, per_page=20):
        """
        Get list of plants from Trefle API
        
        Args:
            page: Page number (default 1)
            per_page: Results per page (max 20 for free tier)
        
        Returns:
            dict: API response with plant data
        """
        url = f"{self.BASE_URL}/plants"
        params = {
            'token': self.api_key,
            'page': page,
            'per_page': per_page,
        }
        
        try:
            print(f"🌱 Fetching plants from Trefle API (page {page})...")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Successfully fetched {len(data.get('data', []))} plants")
            return data
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching plants: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def get_plant_details(self, plant_id):
        """
        Get detailed information about a specific plant
        
        Args:
            plant_id: Trefle plant ID
        
        Returns:
            dict: Detailed plant data
        """
        url = f"{self.BASE_URL}/plants/{plant_id}"
        params = {'token': self.api_key}
        
        try:
            print(f"🌱 Fetching details for plant ID {plant_id}...")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching plant details: {e}")
            return None
    
    def search_plants(self, query, page=1):
        """
        Search for plants by name
        
        Args:
            query: Search term
            page: Page number
        
        Returns:
            dict: Search results
        """
        url = f"{self.BASE_URL}/plants/search"
        params = {
            'token': self.api_key,
            'q': query,
            'page': page,
        }
        
        try:
            print(f"🔍 Searching for '{query}'...")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Found {len(data.get('data', []))} results")
            return data
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching plants: {e}")
            return None
    
    def test_connection(self):
        """
        Test if API key is valid
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.get_plant_list(page=1, per_page=1)
            if result and 'data' in result:
                print("✅ Trefle API connection successful!")
                return True
            else:
                print("❌ API connection failed - invalid response")
                return False
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False