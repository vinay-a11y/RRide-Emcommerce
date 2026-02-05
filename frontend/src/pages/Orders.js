import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Package, ChevronRight } from 'lucide-react';
import { API } from '../context/AuthContext';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

export default function Orders() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchOrders();
  }, [token]);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      placed: 'text-blue-500',
      processing: 'text-yellow-500',
      shipped: 'text-purple-500',
      delivered: 'text-green-500',
      cancelled: 'text-red-500'
    };
    return colors[status] || 'text-zinc-400';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-8 bg-zinc-900 rounded w-48 mb-8 loading-shimmer" />
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 loading-shimmer h-48" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black pt-24 pb-16" data-testid="orders-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1
          className="text-5xl sm:text-6xl font-bold text-white uppercase mb-8"
          style={{ fontFamily: 'Teko, sans-serif' }}
          data-testid="orders-title"
        >
          Your <span className="text-primary">Orders</span>
        </h1>

        {orders.length === 0 ? (
          <div className="text-center py-20" data-testid="no-orders">
            <Package className="mx-auto text-zinc-600 mb-4" size={64} />
            <p className="text-zinc-400 text-xl mb-6">No orders yet</p>
            <button
              onClick={() => navigate('/products')}
              className="px-8 py-4 bg-primary text-black font-bold uppercase tracking-wider hover:bg-orange-400 transition-all skew-button"
              data-testid="start-shopping-btn"
            >
              <span>Start Shopping</span>
            </button>
          </div>
        ) : (
          <div className="space-y-6" data-testid="orders-list">
            {orders.map((order, index) => (
              <motion.div
                key={order.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 hover:border-zinc-700 transition-all"
                data-testid={`order-${index}`}
              >
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4">
                  <div>
                    <div className="flex items-center space-x-4 mb-2">
                      <h3 className="text-white font-semibold text-lg" data-testid={`order-id-${index}`}>
                        Order #{order.id.slice(0, 8).toUpperCase()}
                      </h3>
                      <span className={`font-semibold uppercase text-sm ${getStatusColor(order.order_status)}`} data-testid={`order-status-${index}`}>
                        {order.order_status}
                      </span>
                    </div>
                    <p className="text-zinc-400 text-sm">
                      Placed on {new Date(order.created_at).toLocaleDateString('en-IN', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                  <div className="mt-4 lg:mt-0 text-right">
                    <p className="text-zinc-400 text-sm mb-1">Total Amount</p>
                    <p className="text-primary font-bold text-2xl" data-testid={`order-amount-${index}`}>
                      ₹{order.total_amount.toLocaleString()}
                    </p>
                  </div>
                </div>

                {/* Order Items */}
                <div className="border-t border-zinc-800 pt-4 mb-4">
                  <div className="space-y-3">
                    {order.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="flex items-center space-x-4">
                        <div className="w-2 h-2 bg-primary rounded-full" />
                        <div className="flex-1">
                          <p className="text-white font-semibold">{item.product_name}</p>
                          <p className="text-zinc-400 text-sm">
                            Quantity: {item.quantity} x ₹{item.price.toLocaleString()}
                          </p>
                        </div>
                        <p className="text-white font-semibold">
                          ₹{(item.quantity * item.price).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Shipping Address */}
                <div className="border-t border-zinc-800 pt-4 mb-4">
                  <p className="text-zinc-400 text-sm mb-2">Shipping Address:</p>
                  <p className="text-white text-sm">
                    {order.shipping_address.name}, {order.shipping_address.mobile}
                    <br />
                    {order.shipping_address.address_line}, {order.shipping_address.city}
                    <br />
                    {order.shipping_address.state} - {order.shipping_address.pincode}
                  </p>
                </div>

                {/* Payment Method */}
                <div className="border-t border-zinc-800 pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-zinc-400 text-sm">Payment Method:</p>
                      <p className="text-white font-semibold uppercase">{order.payment_method}</p>
                    </div>
                    <button
                      onClick={() => navigate(`/products/${order.items[0].product_id}`)}
                      className="flex items-center space-x-2 text-primary hover:text-orange-400 transition-colors"
                      data-testid={`reorder-btn-${index}`}
                    >
                      <span className="font-semibold">View Items</span>
                      <ChevronRight size={16} />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
