import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import axios from 'axios';
import '@/App.css';
import { AuthProvider, useAuth, API } from './context/AuthContext';
import { BikeProvider } from './context/BikeContext';
import Navbar from './components/Navbar';
import { Footer } from './components/Footer';
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';
import Login from './pages/Login';

function AppContent() {
  const { token } = useAuth();
  const [cartCount, setCartCount] = useState(0);

  useEffect(() => {
    if (token) {
      fetchCartCount();
    }
  }, [token]);

  const fetchCartCount = async () => {
    try {
      const response = await axios.get(`${API}/cart`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const count = response.data.items.reduce((sum, item) => sum + item.quantity, 0);
      setCartCount(count);
    } catch (error) {
      console.error('Failed to fetch cart count:', error);
    }
  };

  return (
    <div className="App min-h-screen bg-black">
      <Navbar cartCount={cartCount} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetail />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/login" element={<Login />} />
      </Routes>
      <Footer />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#27272A',
            color: '#FAFAFA',
            border: '1px solid #3F3F46'
          }
        }}
      />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <BikeProvider>
          <AppContent />
        </BikeProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
