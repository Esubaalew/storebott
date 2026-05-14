import requests

BASE_URL = "yoururlhere"

SESSION = requests.Session()
TIMEOUT = 10  # seconds


def safe_get(url, params=None):
    try:
        res = SESSION.get(url, params=params, timeout=TIMEOUT)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        print("GET ERROR:", url, e)
        return []


def safe_post(url, data=None):
    try:
        res = SESSION.post(url, json=data, timeout=TIMEOUT)
        if res.status_code in (200, 201):
            return res.json()
        return None
    except Exception as e:
        print("POST ERROR:", url, e)
        return None


# ── Categories ─────────────────────────────
def get_categories():
    return safe_get(f"{BASE_URL}/categories/")


def get_subcategories(category_id):
    return safe_get(f"{BASE_URL}/categories/{category_id}/subcategories/")


def get_brands(subcategory_id):
    return safe_get(f"{BASE_URL}/subcategories/{subcategory_id}/brands/")


def get_models(brand_id):
    return safe_get(f"{BASE_URL}/brands/{brand_id}/models/")


def get_products(model_id):
    return safe_get(f"{BASE_URL}/models/{model_id}/items/")


def get_product_details(item_id):
    return safe_get(f"{BASE_URL}/items/{item_id}/")


def check_stock_availability(item_id):
    return safe_get(f"{BASE_URL}/items/{item_id}/stocks/")


def search_items(query):
    return safe_get(f"{BASE_URL}/items/search", params={"q": query})


def fetch_item_details(item_id):
    return get_product_details(item_id)


# ── Requests system ────────────────────────
def create_request(user_id, username, name, phone, address, additional_text):
    return safe_post(f"{BASE_URL}/requests/", {
        "user_id": user_id,
        "username": username,
        "name": name,
        "phone": phone,
        "address": address,
        "additional_text": additional_text
    })


def create_message(request_id, sender_id, user_id, content):
    return safe_post(f"{BASE_URL}/messages/", {
        "request": request_id,
        "sender_id": sender_id,
        "user_id": user_id,
        "content": content
    })


def get_all_requests():
    return safe_get(f"{BASE_URL}/requests/")


def get_request_details(request_id):
    return safe_get(f"{BASE_URL}/requests/{request_id}/")


def get_all_messages():
    return safe_get(f"{BASE_URL}/messages/")
