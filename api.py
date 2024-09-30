import requests

BASE_URL = 'https://store.4gmobiles.com'

# Fetch all categories
def get_categories():
    response = requests.get(f'{BASE_URL}/categories/')
    return response.json() if response.status_code == 200 else []

# Fetch subcategories for a specific category
def get_subcategories(category_id):
    response = requests.get(f'{BASE_URL}/categories/{category_id}/subcategories/')
    return response.json() if response.status_code == 200 else []

# Fetch brands for a specific subcategory
def get_brands(subcategory_id):
    response = requests.get(f'{BASE_URL}/subcategories/{subcategory_id}/brands/')
    return response.json() if response.status_code == 200 else []

# Fetch models for a specific brand
def get_models(brand_id):
    response = requests.get(f'{BASE_URL}/brands/{brand_id}/models/')
    return response.json() if response.status_code == 200 else []

# Fetch items for a specific model
def get_products(model_id):
    response = requests.get(f'{BASE_URL}/models/{model_id}/items/')
    return response.json() if response.status_code == 200 else []

# Fetch details of a specific item/product
def get_product_details(product_id):
    response = requests.get(f'{BASE_URL}/items/{product_id}/')
    return response.json() if response.status_code == 200 else None

# Check stock availability for a specific item
def check_stock_availability(item_id):
    response = requests.get(f'{BASE_URL}/items/{item_id}/stocks/')
    return response.json() if response.status_code == 200 else None

# Search for items by query
def search_items(query):
    response = requests.get(f'{BASE_URL}/items/search?q={query}') 
    return response.json() if response.status_code == 200 else []

# Fetch all details of a specific brand by ID
def get_brand_details(brand_id):
    response = requests.get(f'{BASE_URL}/brands/{brand_id}/')
    return response.json() if response.status_code == 200 else None

# Fetch all details of a specific model by ID
def get_model_details(model_id):
    response = requests.get(f'{BASE_URL}/models/{model_id}/')
    return response.json() if response.status_code == 200 else None

# Fetch all details of a specific subcategory by ID
def get_subcategory_details(subcategory_id):
    response = requests.get(f'{BASE_URL}/subcategories/{subcategory_id}/')
    return response.json() if response.status_code == 200 else None

# Fetch details of a specific item/product directly from the new endpoint
def fetch_item_details(item_id):
    response = requests.get(f'{BASE_URL}/items/{item_id}/')
    return response.json() if response.status_code == 200 else None

# Add a new request
def create_request(user_id, username, name, phone, address, additional_text):
    data = {
        "user_id": user_id,
        "username": username,
        "name": name,
        "phone": phone,
        "address": address,
        "additional_text": additional_text
    }
    response = requests.post(f'{BASE_URL}/requests/', json=data)
    return response.json() if response.status_code == 201 else None

# Add a new message
def create_message(request_id, sender_id, content):
    data = {
        "request": request_id,
        "sender_id": sender_id,
        "content": content
    }
    response = requests.post(f'{BASE_URL}/messages/', json=data)
    return response.json() if response.status_code == 201 else None
