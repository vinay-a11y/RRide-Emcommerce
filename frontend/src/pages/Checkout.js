import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '../context/AuthContext';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

export default function Checkout() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [cart, setCart] = useState({ items: [] });
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('razorpay');
  const [address, setAddress] = useState({
    name: '',
    mobile: '',
    pincode: '',
    address_line: '',
    city: '',
    state: ''
  });

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchCart();
  }, [token]);

  const fetchCart = async () => {
    try {
      const response = await axios.get(`${API}/cart`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.items.length === 0) {
        navigate('/cart');
        return;
      }
      setCart(response.data);
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateTotal = () => {
    return cart.items.reduce((total, item) => total + item.product.price * item.quantity, 0);
  };

  const loadRazorpayScript = () => {
    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    setProcessing(true);

    try {
      if (paymentMethod === 'razorpay') {
        const scriptLoaded = await loadRazorpayScript();
        if (!scriptLoaded) {
          toast.error('Failed to load Razorpay SDK');
          setProcessing(false);
          return;
        }

        const paymentResponse = await axios.post(
          `${API}/payment/create-order`,
          { amount: calculateTotal() },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const options = {
          key: paymentResponse.data.key_id,
          amount: paymentResponse.data.amount,
          currency: paymentResponse.data.currency,
          name: 'RRIDE GARAGE',
          description: 'Bike Parts & Accessories',
          handler: async function (response) {
            await createOrder(response.razorpay_payment_id);
          },
          prefill: {
            name: address.name,
            contact: address.mobile
          },
          theme: {
            color: '#FF8C42'
          }
        };

        const razorpay = new window.Razorpay(options);
        razorpay.open();
        setProcessing(false);
      } else {
        await createOrder();
      }
    } catch (error) {
      console.error('Payment failed:', error);
      toast.error('Payment failed. Please try again.');
      setProcessing(false);
    }
  };

  const createOrder = async (paymentId = null) => {
    try {
      const orderData = {
        items: cart.items.map((item) => ({
          product_id: item.product_id,
          product_name: item.product.name,
          quantity: item.quantity,
          price: item.product.price
        })),
        total_amount: calculateTotal(),
        shipping_address: address,
        payment_method: paymentMethod,
        razorpay_payment_id: paymentId
      };

      await axios.post(`${API}/orders/create`, orderData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Order placed successfully!');
      navigate('/orders');
    } catch (error) {
      console.error('Failed to create order:', error);
      toast.error('Failed to create order');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-8 bg-zinc-900 rounded w-48 mb-8 loading-shimmer" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black pt-24 pb-16" data-testid="checkout-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1
          className="text-5xl sm:text-6xl font-bold text-white uppercase mb-8"
          style={{ fontFamily: 'Teko, sans-serif' }}
          data-testid="checkout-title"
        >
          <span className="text-primary">Checkout</span>
        </h1>

        <form onSubmit={handlePlaceOrder} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            {/* Shipping Address */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-zinc-900 border border-zinc-800 rounded-lg p-6"
            >
              <h2
                className="text-2xl font-bold text-white uppercase mb-6"
                style={{ fontFamily: 'Teko, sans-serif' }}
              >
                Shipping Address
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Full Name"
                  value={address.name}
                  onChange={(e) => setAddress({ ...address, name: e.target.value })}
                  className="px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                  required
                  data-testid="name-input"
                />
                <input
                  type="tel"
                  placeholder="Mobile Number"
                  value={address.mobile}
                  onChange={(e) => setAddress({ ...address, mobile: e.target.value })}
                  className="px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                  required
                  data-testid="mobile-input"
                />
                <input
                  type="text"
                  placeholder="Pincode"
                  value={address.pincode}
                  onChange={(e) => setAddress({ ...address, pincode: e.target.value })}
                  className="px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                  required
                  data-testid="pincode-input"
                />
                <input
                  type="text"
                  placeholder="City"
                  value={address.city}
                  onChange={(e) => setAddress({ ...address, city: e.target.value })}
                  className="px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                  required
                  data-testid="city-input"
                />
                <input
                  type="text"
                  placeholder="State"
                  value={address.state}
                  onChange={(e) => setAddress({ ...address, state: e.target.value })}
                  className="col-span-2 px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                  required
                  data-testid="state-input"
                />
                <textarea
                  placeholder="Address Line"
                  value={address.address_line}
                  onChange={(e) => setAddress({ ...address, address_line: e.target.value })}
                  className="col-span-2 px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                  rows="3"
                  required
                  data-testid="address-input"
                />
              </div>
            </motion.div>

            {/* Payment Method */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-zinc-900 border border-zinc-800 rounded-lg p-6"
            >
              <h2
                className="text-2xl font-bold text-white uppercase mb-6"
                style={{ fontFamily: 'Teko, sans-serif' }}
              >
                Payment Method
              </h2>
              <div className="space-y-4">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="payment"
                    value="razorpay"
                    checked={paymentMethod === 'razorpay'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-5 h-5 text-primary"
                    data-testid="razorpay-radio"
                  />
                  <span className="text-white font-semibold">Razorpay (UPI / Cards / Net Banking)</span>
                </label>
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="payment"
                    value="cod"
                    checked={paymentMethod === 'cod'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-5 h-5 text-primary"
                    data-testid="cod-radio"
                  />
                  <span className="text-white font-semibold">Cash on Delivery</span>
                </label>
              </div>
            </motion.div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 sticky top-24"
            >
              <h2
                className="text-2xl font-bold text-white uppercase mb-6"
                style={{ fontFamily: 'Teko, sans-serif' }}
              >
                Order Summary
              </h2>
              <div className="space-y-4 mb-6">
                {cart.items.map((item) => (
                  <div key={item.product_id} className="flex justify-between text-sm">
                    <span className="text-zinc-400">
                      {item.product.name} x {item.quantity}
                    </span>
                    <span className="text-white">₹{(item.product.price * item.quantity).toLocaleString()}</span>
                  </div>
                ))}
                <div className="border-t border-zinc-800 pt-4">
                  <div className="flex justify-between text-zinc-400 mb-2">
                    <span>Subtotal</span>
                    <span>₹{calculateTotal().toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-zinc-400 mb-2">
                    <span>Shipping</span>
                    <span className="text-green-500">FREE</span>
                  </div>
                  <div className="flex justify-between text-white font-bold text-xl">
                    <span>Total</span>
                    <span className="text-primary" data-testid="order-total">₹{calculateTotal().toLocaleString()}</span>
                  </div>
                </div>
              </div>
              <button
                type="submit"
                disabled={processing}
                className="w-full px-6 py-4 bg-primary text-black font-bold uppercase tracking-wider hover:bg-orange-400 transition-all skew-button disabled:opacity-50"
                data-testid="place-order-btn"
              >
                <span>{processing ? 'Processing...' : 'Place Order'}</span>
              </button>
            </motion.div>
          </div>
        </form>
      </div>
    </div>
  );
}
