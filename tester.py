import boto3
import requests
import random
import uuid
import json
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
S3_CONFIG = {
    'endpoint_url': 'http://localhost:4566',
    'aws_access_key_id': 'test',
    'aws_secret_access_key': 'test',
    'region_name': 'us-east-1'
}

MAIN_SERVER_URL = 'http://localhost:8000'
BUCKET_NAME = 'products'
IMAGE_KEY = 'brendanheadshot'
IMAGE_PATH = 'sample.jpg'

# Initialize S3 client
s3_client = boto3.client('s3', **S3_CONFIG)

def upload_to_s3():
    """Upload sample.jpg to S3"""
    try:
        # Create bucket if it doesn't exist
        try:
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        except:
            pass  # Bucket might already exist
        
        # Upload the file
        s3_client.upload_file(IMAGE_PATH, BUCKET_NAME, IMAGE_KEY)
        logger.info(f"Successfully uploaded {IMAGE_PATH} to S3 with key {IMAGE_KEY}")
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        raise

def add_products():
    """Add 10 products with similar names and random prices"""
    products = [
        {"name": "beer", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "beers", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "be", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "beer4", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "apple", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "beer5", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "beer6", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "beer7", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "beer8", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "beer9", "price": round(random.uniform(1.00, 10.00), 2)},
        {"name": "beer10", "price": round(random.uniform(1.00, 10.00), 2)}
    ]
    
    added_ids = []
    for product in products:
        product_id = random.randint(1000, 9999)
        payload = {
            "product_id": product_id,
            "name": product["name"],
            "description": f"Description for {product['name']}",
            "image_key": IMAGE_KEY,
            "price": product["price"]
        }
        
        try:
            response = requests.post(f"{MAIN_SERVER_URL}/add", json=payload)
            response.raise_for_status()
            logger.info(f"Added product: {product['name']} with ID {product_id}")
            added_ids.append(product_id)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add product {product['name']}: {e}")
    
    return added_ids

def remove_products(product_ids: List[int], count: int = 2):
    """Remove specified number of products"""
    removed_ids = random.sample(product_ids, min(count, len(product_ids)))
    for product_id in removed_ids:
        try:
            response = requests.delete(f"{MAIN_SERVER_URL}/remove/{product_id}")
            response.raise_for_status()
            logger.info(f"Removed product with ID {product_id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to remove product {product_id}: {e}")
    return removed_ids

def search_products(term: str):
    """Search for products and log results"""
    try:
        response = requests.get(f"{MAIN_SERVER_URL}/search", params={"name": term})
        response.raise_for_status()
        results = response.json()
        logger.info(f"Search results for '{term}':")
        logger.info(json.dumps(results, indent=2))
        return results
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to search products: {e}")

def view_product(product_id: int):
    """View a product to increment its view count"""
    try:
        response = requests.get(f"{MAIN_SERVER_URL}/analytics/view/{product_id}")
        response.raise_for_status()
        logger.info(f"Viewed product {product_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to view product {product_id}: {e}")

def main():
    try:
        # Step 1: Upload image to S3
        upload_to_s3()
        
        # Step 2: Add products
        added_ids = add_products()
        
        # Step 3: Remove two products
        removed_ids = remove_products(added_ids)
        
        # Step 4: Search for "beer"
        search_results = search_products("beer")
        
        # Step 5: View one of the remaining products
        remaining_ids = [id for id in added_ids if id not in removed_ids]
        if remaining_ids:
            view_product(remaining_ids[0])
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    main() 