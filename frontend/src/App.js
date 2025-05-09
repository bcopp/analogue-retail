import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useParams } from 'react-router-dom';
import './App.css';

function ProductList() {
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
    <div className="product-list">
      {products.map((product) => (
        <Link to={`/product/${product.product_id}`} key={product.product_id} className="product-link">
          <div className="product-card">
            <div className="product-image">
              <img 
                src={product.image_src} 
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
        </Link>
      ))}
    </div>
  );
}

function ProductDetail() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        // First, update the view count
        await fetch(`/api/analytics/view/${productId}`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });

        // Then fetch the product details
        const response = await fetch('/api/getall', {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch products: ${response.status}`);
        }
        
        const data = await response.json();
        const product = data.products.find(p => p.product_id === parseInt(productId));
        
        if (!product) {
          throw new Error('Product not found');
        }
        
        setProduct(product);
      } catch (err) {
        console.error('Error details:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId]);

  if (loading) return <div className="loading">Loading product details...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!product) return <div className="error">Product not found</div>;

  return (
    <div className="product-detail">
      <h1>{product.name}</h1>
      <div className="product-detail-content">
        <div className="product-detail-image">
          <img 
            src={product.image_src} 
            alt={product.name}
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = 'https://via.placeholder.com/150?text=No+Image';
            }}
          />
        </div>
        <div className="product-detail-info">
          <p className="price">${product.price.toFixed(2)}</p>
          <p className="views">Views: {product.view_count || 0}</p>
          <p className="description">{product.description}</p>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Retail Products</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<ProductList />} />
            <Route path="/product/:productId" element={<ProductDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
