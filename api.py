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

def check_stock_availability(item_id):
    response = requests.get(f'{BASE_URL}/items/{item_id}/stocks/')
    return response.json() if response.status_code == 200 else None