import os
import requests
import csv
import logging
import time

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='bubble_tea_errors.log')

# Load API key from environment variable
api_key = os.getenv('GOOGLE_MAPS_API_KEY')
if not api_key:
    raise ValueError("API key not found. Set the GOOGLE_MAPS_API_KEY environment variable.")

# Districts to search in Toronto
districts = ["Etobicoke, Toronto, ON", "Scarborough, Toronto, ON", "York, Toronto, ON",
             "East York, Toronto, ON", "North York, Toronto, ON", "Downtown Toronto, ON"]

# Function to fetch bubble tea shops in a district with pagination
def fetch_shops(district):
    all_shops = []
    page_count = 0
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=highly+rated+bubble+tea+shops+in+{district}&key={api_key}"
    
    while url:
        response = requests.get(url)
        response_data = response.json()
        
        if response.status_code != 200 or 'error_message' in response_data:
            raise Exception(f"HTTP Status Code: {response.status_code}, Error Message: {response_data.get('error_message', 'Unknown error')}")
        
        results = response_data.get('results', [])
        all_shops.extend(results)
        page_count += 1
        
        # Print the number of shops fetched in this page
        print(f"Page {page_count}: Fetched {len(results)} shops.")
        
        next_page_token = response_data.get('next_page_token')
        
        # If there's a next page token, we need to wait a few seconds before using it
        if next_page_token:
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={next_page_token}&key={api_key}"
            time.sleep(2)  # Google recommends a short delay before using the next page token
        else:
            url = None
    
    return all_shops

# Function to sort and select top results
def select_top_shops(shops, max_results=60):
    # Sort shops by rating in descending order
    sorted_shops = sorted(shops, key=lambda x: x.get('rating', 0), reverse=True)
    # Return the top results within the limit
    return sorted_shops[:max_results]

# CSV file setup
csv_file = 'bubble_tea_shops.csv'
csv_columns = ['region name', 'shop id', 'shop name', 'latitude', 'longitude', 'star rating']

with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_columns)
    
    # Fetch data for each district and write to CSV
    for district in districts:
        try:
            print(f"Fetching data for district: {district}")
            shops = fetch_shops(district)
            # Select top-rated shops
            top_shops = select_top_shops(shops)
            
            for shop in top_shops:
                region_name = district.split(",")[0]
                shop_id = shop.get('place_id', 'N/A')
                shop_name = shop.get('name', 'N/A')
                location = shop.get('geometry', {}).get('location', {})
                latitude = location.get('lat', 'N/A')
                longitude = location.get('lng', 'N/A')
                star_rating = shop.get('rating', 'N/A')
                row = [region_name, shop_id, shop_name, latitude, longitude, star_rating]
                writer.writerow(row)
        except Exception as e:
            logging.error(f"Error fetching data for district {district}: {e}")
            print(f"Error fetching data for district {district}: {e}")

print("CSV file created successfully.")
