import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        console.log('Fetching products from /api/getall');
        const response = await fetch('/api/getall', {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Failed to fetch products: ${response.status} ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Received data:', data);
        setProducts(data.products);
      } catch (err) {
        console.error('Error details:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) return <div className="loading">Loading products...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="App">
      <header className="App-header">
        <h1>Retail Products</h1>
      </header>
      <main className="product-list">
        {products.map((product) => (
          <div key={product.product_id} className="product-card">
            <div className="product-image">
              <img 
                src={`/image/products/${product.image_key}`} 
                alt={product.name}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://via.placeholder.com/150?text=No+Image';
                }}
              />
            </div>
            <div className="product-details">
              <h2>{product.name}</h2>
              <p className="description">{product.description}</p>
              <p className="price">${product.price.toFixed(2)}</p>
              <p className="views">Views: {product.view_count || 0}</p>
            </div>
          </div>
        ))}
      </main>
    </div>
  );
}

export default App;
