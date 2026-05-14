import requests

BASE_URL = "yoururlhere"


def safe_get(url):
    try:
        r = requests.get(url, timeout=10)
        print("GET:", url, "->", r.status_code)
        return r
    except Exception as e:
        print("REQUEST ERROR:", url, e)
        return None


def get_categories():
    r = safe_get(f"{BASE_URL}/categories/")
    if r and r.status_code == 200:
        try:
            return r.json()
        except Exception as e:
            print("JSON ERROR:", e)
    return []


def get_subcategories(category_id):
    r = safe_get(f"{BASE_URL}/categories/{category_id}/subcategories/")
    return r.json() if r and r.status_code == 200 else []


def get_brands(subcategory_id):
    r = safe_get(f"{BASE_URL}/subcategories/{subcategory_id}/brands/")
    return r.json() if r and r.status_code == 200 else []


def get_models(brand_id):
    r = safe_get(f"{BASE_URL}/brands/{brand_id}/models/")
    return r.json() if r and r.status_code == 200 else []


def get_products(model_id):
    r = safe_get(f"{BASE_URL}/models/{model_id}/items/")
    return r.json() if r and r.status_code == 200 else []


def get_product_details(product_id):
    r = safe_get(f"{BASE_URL}/items/{product_id}/")
    return r.json() if r and r.status_code == 200 else None


def check_stock_availability(item_id):
    r = safe_get(f"{BASE_URL}/items/{item_id}/stocks/")
    return r.json() if r and r.status_code == 200 else None


def search_items(query):
    r = safe_get(f"{BASE_URL}/items/search?q={query}")
    return r.json() if r and r.status_code == 200 else []


def fetch_item_details(item_id):
    return get_product_details(item_id)


def create_request(user_id, username, name, phone, address, additional_text):
    r = requests.post(
        f"{BASE_URL}/requests/",
        json={
            "user_id": user_id,
            "username": username,
            "name": name,
            "phone": phone,
            "address": address,
            "additional_text": additional_text
        },
        timeout=10
    )
    return r.json() if r.status_code == 201 else None


def create_message(request_id, sender_id, user_id, content):
    r = requests.post(
        f"{BASE_URL}/messages/",
        json={
            "request": request_id,
            "sender_id": sender_id,
            "user_id": user_id,
            "content": content
        },
        timeout=10
    )
    return r.json() if r.status_code == 201 else None


def get_all_requests():
    r = safe_get(f"{BASE_URL}/requests/")
    return r.json() if r and r.status_code == 200 else []


def get_request_details(request_id):
    r = safe_get(f"{BASE_URL}/requests/{request_id}/")
    return r.json() if r and r.status_code == 200 else None


def get_all_messages():
    r = safe_get(f"{BASE_URL}/messages/")
    return r.json() if r and r.status_code == 200 else []
