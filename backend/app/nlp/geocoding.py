"""
Geocoding Pipeline for Nigerian Conflict Events
774 LGAs + Villages lookup for precise coordinate mapping
"""

import json
import csv
import re
from typing import Dict, Any, Optional, Tuple, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class NigerianGeocoder:
    """Precise geocoding for Nigerian locations using 774 LGAs and villages database"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.lga_data = {}
        self.village_data = {}
        self.state_coordinates = {}
        
        # Load geospatial data
        self._load_lga_data()
        self._load_village_data()
        self._load_state_coordinates()
        
        # State to LGA mapping
        self.state_lga_mapping = self._create_state_lga_mapping()
        
        # Common location variations
        self.location_variations = {
            'fct': 'federal capital territory',
            'abuja': 'federal capital territory',
            'lagos island': 'lagos',
            'ikeja': 'lagos',
            'mainland': 'lagos',
            'victoria island': 'lagos',
            'ikorodu': 'lagos',
            'badagry': 'lagos',
            'port harcourt': 'rivers',
            'portharcourt': 'rivers',
            'warri': 'delta',
            'effurun': 'delta',
            'aba': 'abia',
            'umua': 'abia',  # Common prefix in Abia
            'owerri': 'imo',
            'onitsha': 'anambra',
            'awka': 'anambra',
            'enugu': 'enugu',
            'aba': 'abia',
            'umuahia': 'abia',
            'calabar': 'cross river',
            'uyo': 'akwa ibom',
            'benin': 'edo',
            'benin city': 'edo',
            'ile-ife': 'osun',
            'ife': 'osun',
            'osogbo': 'osun',
            'ibadan': 'oyo',
            'ilorin': 'kwara',
            'kano': 'kano',
            'katsina': 'katsina',
            'kaduna': 'kaduna',
            'maiduguri': 'borno',
            'jos': 'plateau',
            'bauchi': 'bauchi',
            'gombe': 'gombe',
            'yola': 'adamawa',
            'damaturu': 'yobe',
            'minna': 'niger',
            'suleja': 'niger',
            'lokoja': 'kogi',
            'okene': 'kogi',
            'akure': 'ondo',
            'ado ekiti': 'ekiti',
            'asaba': 'delta',
            'ogwashi uku': 'delta',
            'sapele': 'delta',
            'warri': 'delta',
            'ugelli': 'delta',
            'aba': 'abia',
            'umuahia': 'abia',
            'afikpo': 'ebonyi',
            'abakaliki': 'ebonyi',
            'onycha': 'ebonyi',
            'makurdi': 'benue',
            'otu': 'benue',
            'gboko': 'benue',
            'katsina ala': 'benue',
            'jalingo': 'taraba',
            'wukari': 'taraba',
            'sokoto': 'sokoto',
            'birnin kebbi': 'kebbi',
            'gusau': 'zamfara',
            'kaura namoda': 'zamfara'
        }

    def geocode_location(self, location_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Geocode location data to precise coordinates
        
        Args:
            location_data: Dictionary with state, lga, community
            
        Returns:
            Dictionary with coordinates and location details
        """
        try:
            state = self._normalize_location(location_data.get('state', ''))
            lga = self._normalize_location(location_data.get('lga', ''))
            community = self._normalize_location(location_data.get('community', ''))
            
            # If no state provided, try to extract from text
            if not state:
                return None
            
            # Get state coordinates as fallback
            state_coords = self.state_coordinates.get(state.lower())
            
            # Try to find LGA coordinates
            lga_coords = self._find_lga_coordinates(state, lga)
            
            # Try to find community/village coordinates
            community_coords = self._find_community_coordinates(state, lga, community)
            
            # Determine best coordinates
            if community_coords:
                coordinates = community_coords
                precision = 'community'
            elif lga_coords:
                coordinates = lga_coords
                precision = 'lga'
            elif state_coords:
                coordinates = state_coords
                precision = 'state'
            else:
                logger.warning(f"No coordinates found for location: {location_data}")
                return None
            
            return {
                'latitude': coordinates['lat'],
                'longitude': coordinates['lng'],
                'state': state,
                'lga': lga or 'Unknown',
                'community': community or 'Unknown',
                'precision': precision,
                'coordinates': f"POINT({coordinates['lng']} {coordinates['lat']})"
            }
            
        except Exception as e:
            logger.error(f"Error geocoding location {location_data}: {str(e)}")
            return None

    def _normalize_location(self, location: str) -> str:
        """Normalize location name for matching"""
        if not location:
            return ''
        
        # Convert to lowercase and strip
        location = location.lower().strip()
        
        # Handle common variations
        for variation, standard in self.location_variations.items():
            if variation in location:
                location = location.replace(variation, standard)
        
        # Remove common prefixes/suffixes
        location = re.sub(r'^(local|government|area|lga)\s+', '', location)
        location = re.sub(r'\s+(local|government|area|lga)$', '', location)
        
        return location.title()

    def _find_lga_coordinates(self, state: str, lga: str) -> Optional[Dict[str, float]]:
        """Find coordinates for a specific LGA"""
        if not state or not lga:
            return None
        
        # Search in LGA data
        state_lgas = self.lga_data.get(state.lower(), {})
        
        for lga_name, coords in state_lgas.items():
            if self._normalize_location(lga) == self._normalize_location(lga_name):
                return coords
        
        return None

    def _find_community_coordinates(self, state: str, lga: str, community: str) -> Optional[Dict[str, float]]:
        """Find coordinates for a specific community/village"""
        if not community:
            return None
        
        # Search in village data
        for village_data in self.village_data:
            if (village_data['state'].lower() == state.lower() and
                self._normalize_location(community) == self._normalize_location(village_data['village'])):
                return {
                    'lat': float(village_data['latitude']),
                    'lng': float(village_data['longitude'])
                }
        
        return None

    def _load_lga_data(self):
        """Load LGA coordinates data"""
        try:
            lga_file = self.data_dir / "nigeria_lgas.csv"
            
            if lga_file.exists():
                with open(lga_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        state = row['state'].lower().strip()
                        lga = row['lga'].lower().strip()
                        
                        if state not in self.lga_data:
                            self.lga_data[state] = {}
                        
                        self.lga_data[state][lga] = {
                            'lat': float(row['latitude']),
                            'lng': float(row['longitude'])
                        }
                
                logger.info(f"Loaded {len(self.lga_data)} states with LGA data")
            else:
                # Create sample data for demonstration
                self._create_sample_lga_data()
                
        except Exception as e:
            logger.error(f"Error loading LGA data: {str(e)}")
            self._create_sample_lga_data()

    def _load_village_data(self):
        """Load village coordinates data"""
        try:
            village_file = self.data_dir / "nigeria_villages.csv"
            
            if village_file.exists():
                with open(village_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.village_data.append({
                            'state': row['state'].strip(),
                            'lga': row['lga'].strip(),
                            'village': row['village'].strip(),
                            'latitude': row['latitude'],
                            'longitude': row['longitude']
                        })
                
                logger.info(f"Loaded {len(self.village_data)} villages")
            else:
                # Create sample data for demonstration
                self._create_sample_village_data()
                
        except Exception as e:
            logger.error(f"Error loading village data: {str(e)}")
            self._create_sample_village_data()

    def _load_state_coordinates(self):
        """Load state capital coordinates"""
        self.state_coordinates = {
            'abia': {'lat': 5.5320, 'lng': 7.4826},
            'adamawa': {'lat': 9.3264, 'lng': 12.3956},
            'akwa ibom': {'lat': 4.9983, 'lng': 7.5114},
            'anambra': {'lat': 6.2154, 'lng': 7.0677},
            'bauchi': {'lat': 10.3157, 'lng': 9.8443},
            'bayelsa': {'lat': 4.8446, 'lng': 6.0220},
            'benue': {'lat': 7.3406, 'lng': 8.9329},
            'borno': {'lat': 11.8674, 'lng': 13.1455},
            'cross river': {'lat': 5.9613, 'lng': 8.6769},
            'delta': {'lat': 5.7883, 'lng': 6.1974},
            'ebonyi': {'lat': 6.3170, 'lng': 8.0978},
            'edo': {'lat': 6.5244, 'lng': 5.6037},
            'ekiti': {'lat': 7.6376, 'lng': 5.2262},
            'enugu': {'lat': 6.4469, 'lng': 7.5018},
            'gombe': {'lat': 10.2847, 'lng': 11.1646},
            'imo': {'lat': 5.5196, 'lng': 7.0223},
            'jigawa': {'lat': 11.7067, 'lng': 9.4193},
            'kaduna': {'lat': 10.5224, 'lng': 7.4406},
            'kano': {'lat': 11.9444, 'lng': 8.5222},
            'katsina': {'lat': 12.9896, 'lng': 7.6009},
            'kebbi': {'lat': 11.5150, 'lng': 4.1950},
            'kogi': {'lat': 7.8023, 'lng': 6.7338},
            'kwara': {'lat': 8.9667, 'lng': 4.5667},
            'lagos': {'lat': 6.5244, 'lng': 3.3792},
            'nasarawa': {'lat': 8.5000, 'lng': 7.9000},
            'niger': {'lat': 9.6136, 'lng': 5.2292},
            'ogun': {'lat': 7.1606, 'lng': 3.3483},
            'ondo': {'lat': 7.2506, 'lng': 5.1958},
            'osun': {'lat': 7.5718, 'lng': 4.5437},
            'oyo': {'lat': 7.8596, 'lng': 3.9511},
            'plateau': {'lat': 9.2006, 'lng': 8.8807},
            'rivers': {'lat': 4.8156, 'lng': 7.0498},
            'sokoto': {'lat': 13.0605, 'lng': 5.2398},
            'taraba': {'lat': 8.8893, 'lng': 10.9933},
            'yobe': {'lat': 12.8683, 'lng': 11.6344},
            'zamfara': {'lat': 12.1628, 'lng': 6.0305},
            'federal capital territory': {'lat': 9.0765, 'lng': 7.3986}
        }

    def _create_sample_lga_data(self):
        """Create sample LGA data for demonstration"""
        self.lga_data = {
            'plateau': {
                'bokkos': {'lat': 9.2833, 'lng': 8.8833},
                'jos north': {'lat': 9.9333, 'lng': 8.8833},
                'jos south': {'lat': 9.7500, 'lng': 8.9000},
                'barkin ladi': {'lat': 9.5333, 'lng': 8.9167},
                'riyom': {'lat': 9.6500, 'lng': 8.8500}
            },
            'lagos': {
                'ikeja': {'lat': 6.6018, 'lng': 3.3515},
                'badagry': {'lat': 6.4167, 'lng': 2.8833},
                'ikorodu': {'lat': 6.6333, 'lng': 3.5000},
                'epe': {'lat': 6.5833, 'lng': 3.9833}
            },
            'rivers': {
                'port harcourt': {'lat': 4.8156, 'lng': 7.0498},
                'obio-akpor': {'lat': 4.8083, 'lng': 7.0483},
                'ikwerre': {'lat': 4.9167, 'lng': 7.0833},
                'oyigbo': {'lat': 4.9000, 'lng': 7.1167}
            }
        }

    def _create_sample_village_data(self):
        """Create sample village data for demonstration"""
        self.village_data = [
            {
                'state': 'Plateau',
                'lga': 'Bokkos',
                'village': 'Mushere',
                'latitude': '9.2833',
                'longitude': '8.8833'
            },
            {
                'state': 'Plateau',
                'lga': 'Bokkos',
                'village': 'Ropp',
                'latitude': '9.3000',
                'longitude': '8.9000'
            },
            {
                'state': 'Plateau',
                'lga': 'Barkin Ladi',
                'village': 'Gashish',
                'latitude': '9.5333',
                'longitude': '8.9167'
            }
        ]

    def _create_state_lga_mapping(self):
        """Create mapping of states to their LGAs"""
        mapping = {}
        for state, lgas in self.lga_data.items():
            mapping[state] = list(lgas.keys())
        return mapping

    def validate_location(self, state: str, lga: str = None) -> bool:
        """Validate if location exists in Nigeria"""
        state = state.lower().strip()
        
        if state not in self.state_coordinates:
            return False
        
        if lga:
            lga = lga.lower().strip()
            state_lgas = self.lga_data.get(state, {})
            if lga not in state_lgas:
                return False
        
        return True

    def get_lgas_for_state(self, state: str) -> List[str]:
        """Get all LGAs for a given state"""
        state = state.lower().strip()
        return self.state_lga_mapping.get(state, [])

    def search_location(self, query: str) -> List[Dict[str, Any]]:
        """Search for locations by name"""
        query = query.lower().strip()
        results = []
        
        # Search states
        for state in self.state_coordinates:
            if query in state:
                results.append({
                    'type': 'state',
                    'name': state.title(),
                    'coordinates': self.state_coordinates[state]
                })
        
        # Search LGAs
        for state, lgas in self.lga_data.items():
            for lga, coords in lgas.items():
                if query in lga:
                    results.append({
                        'type': 'lga',
                        'name': f"{lga.title()}, {state.title()}",
                        'state': state.title(),
                        'coordinates': coords
                    })
        
        # Search villages
        for village in self.village_data:
            if query in village['village'].lower():
                results.append({
                    'type': 'community',
                    'name': f"{village['village'].title()}, {village['lga'].title()}, {village['state'].title()}",
                    'state': village['state'],
                    'lga': village['lga'],
                    'coordinates': {
                        'lat': float(village['latitude']),
                        'lng': float(village['longitude'])
                    }
                })
        
        return results

# Example usage
if __name__ == "__main__":
    geocoder = NigerianGeocoder()
    
    # Test geocoding
    location = {
        'state': 'Plateau',
        'lga': 'Bokkos',
        'community': 'Mushere'
    }
    
    result = geocoder.geocode_location(location)
    if result:
        print(json.dumps(result, indent=2))
