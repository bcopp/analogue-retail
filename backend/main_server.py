from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error, IntegrityError, DataError, ProgrammingError
from google.cloud import storage
from typing import List, Optional
import re
import os
import sys

def requireenv(name: str) -> str:
    """Require an environment variable to be set, panic if not found"""
    value = os.getenv(name)
    if value is None:
        print(f"Error: Required environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value

app = FastAPI()

# Database connection configuration from environment variables
DB_CONFIG = {
    'host': requireenv('MYSQL_HOST'),
    'port': int(requireenv('MYSQL_PORT')),
    'user': requireenv('MYSQL_USER'),
    'password': requireenv('MYSQL_PASSWORD'),
    'database': requireenv('MYSQL_DATABASE')
}

# GCS configuration from environment variables
GCS_CONFIG = {
    'project': requireenv('GOOGLE_CLOUD_PROJECT'),
}

# Initialize GCS client
storage_client = storage.Client()

# Print configuration for debugging
print("Database Configuration:", {k: v for k, v in DB_CONFIG.items() if k != 'password'})
print("GCS Configuration:", GCS_CONFIG)

# Pydantic models for request validation
class ProductAdd(BaseModel):
    product_id: int
    name: str
    description: str
    image_src: str
    price: float

class PurchaseRequest(BaseModel):
    user_id: int
    product_id: int

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

def validate_gcs_path(image_src: str) -> bool:
    try:
        # Parse the GCS path
        if not image_src.startswith('gs://'):
            return False
        
        # Extract bucket and blob from path
        path_parts = image_src[5:].split('/', 1)  # Remove 'gs://' and split into bucket and blob
        if len(path_parts) != 2:
            return False
        
        bucket_name, blob_name = path_parts
        
        # Check if the blob exists in the bucket
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.exists()
    except:
        return False

def validate_price(price: float) -> bool:
    """Validate that the price is within reasonable bounds and won't overflow DECIMAL(10,2)"""
    # Check if price is positive
    if price <= 0:
        return False
    
    # Check if price has more than 2 decimal places
    if abs(price * 100 - round(price * 100)) > 0.0001:  # Small epsilon for float comparison
        return False
    
    # Check if price is within DECIMAL(10,2) bounds (max 99999999.99)
    if price > 99999999.99:
        return False
    
    return True

def handle_database_error(e: Exception) -> None:
    """Handle database errors and raise appropriate HTTP exceptions"""
    if isinstance(e, IntegrityError):
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Duplicate entry found")
        elif "foreign key constraint fails" in str(e):
            raise HTTPException(status_code=400, detail="Foreign key constraint violation")
        else:
            raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e)}")
    elif isinstance(e, DataError):
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
    elif isinstance(e, ProgrammingError):
        raise HTTPException(status_code=500, detail=f"Database programming error: {str(e)}")
    else:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/analytics/view/{product_id}")
async def view_product(product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if product exists
        cursor.execute("SELECT * FROM product WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update or insert view count
        try:
            cursor.execute("""
                INSERT INTO view (product_id, view_count) 
                VALUES (%s, 1) 
                ON DUPLICATE KEY UPDATE view_count = view_count + 1
            """, (product_id,))
            
            connection.commit()
            print(f"view incremented - Product ID: {product_id}")
            return {"message": "View count updated successfully"}
        except Exception as e:
            handle_database_error(e)
    
    except Exception as e:
        handle_database_error(e)
    finally:
        cursor.close()
        connection.close()

@app.post("/add")
async def add_product(product: ProductAdd):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Validate price
        if not validate_price(product.price):
            raise HTTPException(
                status_code=400,
                detail="Invalid price. Price must be positive, have at most 2 decimal places, and be less than 100 million"
            )
        
        # Validate GCS path
        if not validate_gcs_path(product.image_src):
            raise HTTPException(status_code=400, detail="Invalid GCS image path")
        
        # Insert product
        try:
            cursor.execute("""
                INSERT INTO product (product_id, name, description, image_src, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (product.product_id, product.name, product.description, product.image_src, product.price))
            
            connection.commit()
            return {"message": "Product added successfully"}
        except Exception as e:
            handle_database_error(e)
    
    except Exception as e:
        handle_database_error(e)
    finally:
        cursor.close()
        connection.close()

@app.delete("/remove/{product_id}")
async def remove_product(product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Delete from view table first (due to foreign key constraint)
        try:
            cursor.execute("DELETE FROM view WHERE product_id = %s", (product_id,))
            
            # Delete from product table
            cursor.execute("DELETE FROM product WHERE product_id = %s", (product_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Product not found")
            
            connection.commit()
            return {"message": "Product removed successfully"}
        except Exception as e:
            handle_database_error(e)
    
    except Exception as e:
        handle_database_error(e)
    finally:
        cursor.close()
        connection.close()

@app.get("/search")
async def search_products(name: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        try:
            cursor.execute("""
                SELECT p.*, v.view_count 
                FROM product p
                LEFT JOIN view v ON p.product_id = v.product_id
                WHERE SOUNDEX(p.name) = SOUNDEX(%s)
                ORDER BY p.product_id DESC
                LIMIT 20
            """, (name,))
            
            products = cursor.fetchall()
            return {"products": products}
        except Exception as e:
            handle_database_error(e)
    
    except Exception as e:
        handle_database_error(e)
    finally:
        cursor.close()
        connection.close()

@app.post("/purchase")
async def purchase_product(purchase: PurchaseRequest):
    # Simply print the purchase details as requested
    print(f"Purchase request - User ID: {purchase.user_id}, Product ID: {purchase.product_id}")
    return {"message": "Purchase request received"}

@app.get("/getall")
async def get_all_products():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.*, COALESCE(v.view_count, 0) as view_count 
            FROM product p
            LEFT JOIN view v ON p.product_id = v.product_id
            ORDER BY v.view_count DESC, p.product_id DESC
            LIMIT 20
        """)
        
        products = cursor.fetchall()
        return {"products": products}
    except Exception as e:
        handle_database_error(e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 