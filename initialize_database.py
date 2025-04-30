import mysql.connector
from mysql.connector import Error

def initialize_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='example',
            database='retail_db'
        )

        if connection.is_connected():
            cursor = connection.cursor()

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
            print("Database tables created successfully!")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    initialize_database() 