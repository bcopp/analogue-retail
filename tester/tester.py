import requests
import json
from typing import List, Dict
from datetime import datetime

def get_all_products() -> List[Dict]:
    """
    Fetches all products from the /getall endpoint
    Returns a list of product dictionaries
    """
    try:
        response = requests.get('http://localhost:8080/getall')
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()['products']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching products: {e}")
        return []

def print_products(products: List[Dict]) -> None:
    """
    Prints products in a formatted way
    """
    if not products:
        print("No products found")
        return

    print("\n=== Product List ===")
    print(f"Total Products: {len(products)}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    for product in products:
        print(f"Product ID: {product['product_id']}")
        print(f"Name: {product['name']}")
        print(f"Description: {product['description']}")
        print(f"Price: ${product['price']:.2f}")
        print(f"Views: {product['view_count']}")
        print(f"Image Key: {product['image_key']}")
        print("-" * 50)

def main():
    print("Testing /getall endpoint...")
    products = get_all_products()
    print_products(products)

if __name__ == "__main__":
    main() 