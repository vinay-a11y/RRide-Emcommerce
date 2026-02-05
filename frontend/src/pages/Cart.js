import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Trash2, Plus, Minus } from "lucide-react";
import { toast } from "sonner";

import { useAuth, api } from "../context/AuthContext";

export default function Cart() {
  const navigate = useNavigate();
  const { token } = useAuth();

  const [cart, setCart] = useState({ items: [] });
  const [loading, setLoading] = useState(true);

  /* ================================
     FETCH CART ON LOAD
  ================================ */
  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    fetchCart();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const fetchCart = async () => {
    try {
      const response = await api.get("/cart");
      setCart(response.data);
    } catch (error) {
      console.error("Failed to fetch cart:", error);
      toast.error("Failed to load cart");
    } finally {
      setLoading(false);
    }
  };

  /* ================================
     UPDATE QUANTITY
  ================================ */
  const updateQuantity = async (productId, newQuantity) => {
    if (newQuantity < 1) return;

    try {
      await api.post("/cart/update", {
        product_id: productId,
        quantity: newQuantity,
      });
      fetchCart();
    } catch (error) {
      console.error("Failed to update quantity:", error);
      toast.error("Failed to update quantity");
    }
  };

  /* ================================
     REMOVE ITEM
  ================================ */
  const removeItem = async (productId) => {
    try {
      await api.delete(`/cart/remove/${productId}`);
      toast.success("Item removed from cart");
      fetchCart();
    } catch (error) {
      console.error("Failed to remove item:", error);
      toast.error("Failed to remove item");
    }
  };

  /* ================================
     TOTAL CALCULATION
  ================================ */
  const calculateTotal = () => {
    return cart.items.reduce(
      (total, item) => total + item.product.price * item.quantity,
      0
    );
  };

  /* ================================
     LOADING STATE
  ================================ */
  if (loading) {
    return (
      <div className="min-h-screen bg-black pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="h-8 bg-zinc-900 rounded w-48 mb-8 loading-shimmer" />
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 h-32 loading-shimmer"
              />
            ))}
          </div>
        </div>
      </div>
    );
  }

  /* ================================
     UI
  ================================ */
  return (
    <div className="min-h-screen bg-black pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4">
        <h1
          className="text-5xl font-bold text-white uppercase mb-8"
          style={{ fontFamily: "Teko, sans-serif" }}
        >
          Your <span className="text-primary">Cart</span>
        </h1>

        {cart.items.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-zinc-400 text-xl mb-6">
              Your cart is empty
            </p>
            <button
              onClick={() => navigate("/products")}
              className="px-8 py-4 bg-primary text-black font-bold uppercase hover:bg-orange-400 transition-all"
            >
              Continue Shopping
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* CART ITEMS */}
            <div className="lg:col-span-2 space-y-4">
              {cart.items.map((item, index) => (
                <motion.div
                  key={item.product_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 flex items-center space-x-4"
                >
                  <img
                    src={item.product.image_url}
                    alt={item.product.name}
                    className="w-24 h-24 object-cover rounded-lg"
                  />

                  <div className="flex-1">
                    <h3
                      className="text-white font-semibold text-lg uppercase"
                      style={{ fontFamily: "Teko, sans-serif" }}
                    >
                      {item.product.name}
                    </h3>
                    <p className="text-zinc-400 text-sm">
                      {item.product.category}
                    </p>
                    <span className="text-primary font-bold text-xl">
                      ₹{item.product.price.toLocaleString()}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() =>
                        updateQuantity(item.product_id, item.quantity - 1)
                      }
                      className="w-8 h-8 bg-zinc-800 text-white"
                    >
                      <Minus size={16} />
                    </button>

                    <span className="w-10 text-center text-white font-bold">
                      {item.quantity}
                    </span>

                    <button
                      onClick={() =>
                        updateQuantity(item.product_id, item.quantity + 1)
                      }
                      className="w-8 h-8 bg-zinc-800 text-white"
                    >
                      <Plus size={16} />
                    </button>
                  </div>

                  <button
                    onClick={() => removeItem(item.product_id)}
                    className="text-zinc-400 hover:text-red-500"
                  >
                    <Trash2 size={20} />
                  </button>
                </motion.div>
              ))}
            </div>

            {/* SUMMARY */}
            <div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 sticky top-24">
                <h2
                  className="text-2xl font-bold text-white uppercase mb-6"
                  style={{ fontFamily: "Teko, sans-serif" }}
                >
                  Order Summary
                </h2>

                <div className="space-y-4 mb-6">
                  <div className="flex justify-between text-zinc-400">
                    <span>Subtotal</span>
                    <span>
                      ₹{calculateTotal().toLocaleString()}
                    </span>
                  </div>

                  <div className="flex justify-between text-zinc-400">
                    <span>Shipping</span>
                    <span className="text-green-500">FREE</span>
                  </div>

                  <div className="border-t border-zinc-800 pt-4 flex justify-between text-white font-bold text-xl">
                    <span>Total</span>
                    <span className="text-primary">
                      ₹{calculateTotal().toLocaleString()}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => navigate("/checkout")}
                  className="w-full px-6 py-4 bg-primary text-black font-bold uppercase hover:bg-orange-400 transition-all"
                >
                  Proceed to Checkout
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
