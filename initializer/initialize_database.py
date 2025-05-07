import mysql.connector
from mysql.connector import Error
from google.cloud import storage
import requests
import random
import uuid
import json
from typing import List, Dict
import logging
import time
import os
import sys
from tenacity import retry, stop_after_attempt, wait_exponential

def requireenv(name: str) -> str:
    """Require an environment variable to be set, panic if not found"""
    value = os.getenv(name)
    if value is None:
        logger.error(f"Error: Required environment variable {name} is not set")
        sys.exit(1)
    return value

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
GCS_CONFIG = {
    'project': requireenv('GOOGLE_CLOUD_PROJECT'),
    'bucket_name': requireenv('GCS_BUCKET_NAME')
}

MAIN_SERVER_URL = requireenv('BACKEND_URL')
IMAGE_KEY = requireenv('GCS_IMAGE_KEY')
IMAGE_PATH = requireenv('IMAGE_PATH')

# Database configuration from environment variables
DB_CONFIG = {
    'host': requireenv('DB_HOST'),
    'port': int(requireenv('DB_PORT')),
    'user': requireenv('DB_USER'),
    'password': requireenv('DB_PASSWORD'),
    'database': requireenv('DB_NAME')
}

# Initialize GCS client
storage_client = storage.Client()

@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_db_connection():
    """Get a database connection with retry mechanism"""
    try:
        logger.info(f"Attempting to connect to MySQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.info("Successfully connected to MySQL")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise

def initialize_database():
    connection = None
    cursor = None
    try:
        # Connect to MySQL server using environment variables
        connection = get_db_connection()
        cursor = connection.cursor()

        if connection.is_connected():
            # Create user table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Create product table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product (
                    product_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    image_key VARCHAR(255),
                    price DECIMAL(10,2) NOT NULL
                )
            """)

            # Create view table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS view (
                    view_id INT AUTO_INCREMENT PRIMARY KEY,
                    product_id INT,
                    view_count INT DEFAULT 0,
                    FOREIGN KEY (product_id) REFERENCES product(product_id)
                )
            """)

            connection.commit()
            logger.info("Database tables created successfully!")

    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection is closed")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def upload_to_gcs():
    """Upload sample.png to Google Cloud Storage"""
    try:
        bucket = storage_client.bucket(GCS_CONFIG['bucket_name'])
        
        # Upload the file
        logger.info(f"Uploading {IMAGE_PATH} to bucket {GCS_CONFIG['bucket_name']} with key {IMAGE_KEY}")
        blob = bucket.blob(IMAGE_KEY)
        blob.upload_from_filename(IMAGE_PATH)
        
        # Make the blob publicly accessible
        blob.make_public()
        
        logger.info(f"Successfully uploaded {IMAGE_PATH} to GCS with key {IMAGE_KEY}")
    except Exception as e:
        logger.error(f"Failed to upload to GCS: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def add_products():
    """Add 10 products with similar names and random prices"""
    products = [
        {
            "name": "beer",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "A refreshing craft beer with a perfect balance of hops and malt. Brewed locally with traditional methods."
        },
        {
            "name": "beers",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "A variety pack of our most popular craft beers. Perfect for sharing with friends."
        },
        {
            "name": "be",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "A unique herbal tea blend inspired by traditional brewing methods. Caffeine-free and soothing."
        },
        {
            "name": "beer4",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "Our signature IPA with a bold citrus flavor and smooth finish. Limited edition batch."
        },
        {
            "name": "apple",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "Fresh, crisp apples picked at peak ripeness. Perfect for snacking or baking."
        },
        {
            "name": "beer5",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "A rich stout with notes of coffee and chocolate. Perfect for cold winter nights."
        },
        {
            "name": "beer6",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "Light and refreshing wheat beer with a hint of citrus. Great for summer days."
        },
        {
            "name": "beer7",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "Amber ale with caramel notes and a smooth finish. A customer favorite."
        },
        {
            "name": "beer8",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "Pilsner with a crisp, clean taste and golden color. Perfect for any occasion."
        },
        {
            "name": "beer9",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "Sour beer with tropical fruit notes. A unique and refreshing experience."
        },
        {
            "name": "beer10",
            "price": round(random.uniform(1.00, 10.00), 2),
            "description": "Barrel-aged porter with complex flavors of vanilla and oak. Limited release."
        }
    ]
    
    added_ids = []
    for product in products:
        product_id = random.randint(1000, 9999)
        payload = {
            "product_id": product_id,
            "name": product["name"],
            "description": product["description"],
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
            raise
    
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
        # Wait for backend to be ready
        logger.info("Waiting for backend service to be ready...")
        
        # Step 1: Upload image to S3
        upload_to_gcs()
        
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
    logger.info("Starting Initialize Database")
    initialize_database()
    main()
    logger.info("Initialize Database Done")
