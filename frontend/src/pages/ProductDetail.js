'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShoppingCart, Check, MessageCircle, ArrowLeft, Heart } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { API } from '../context/AuthContext';
import { toast } from 'sonner';

const ProductDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { token, isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`${API}/products/${id}`);
      setProduct(response.data);
      setLoading(false);
    } catch (error) {
      console.error('[v0] Failed to fetch product:', error);
      toast.error('Product not found');
      navigate('/products');
    }
  };

  const addToCart = async () => {
    if (!isAuthenticated || !token) {
      toast.error('Please login to add items to cart');
      navigate('/login');
      return;
    }

    setAdding(true);
    try {
      await axios.post(
        `${API}/cart/add`,
        { product_id: product.id, quantity },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Added to cart!');
      setQuantity(1);
    } catch (error) {
      console.error('[v0] Failed to add to cart:', error);
      toast.error(error.response?.data?.detail || 'Failed to add to cart');
    } finally {
      setAdding(false);
    }
  };

  const buyNow = async () => {
    if (!isAuthenticated || !token) {
      navigate('/login');
      return;
    }
    await addToCart();
    navigate('/cart');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="aspect-square bg-zinc-900 rounded animate-pulse" />
            <div className="space-y-4">
              <div className="h-8 bg-zinc-900 rounded animate-pulse" />
              <div className="h-4 bg-zinc-900 rounded w-2/3 animate-pulse" />
              <div className="h-12 bg-zinc-900 rounded animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) return null;

  const images = product.images?.length > 0 ? product.images : ['https://via.placeholder.com/600'];

  return (
    <div className="min-h-screen bg-black pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-primary hover:text-orange-400 transition-colors mb-8"
        >
          <ArrowLeft size={20} />
          <span>Back</span>
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Images */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-4"
          >
            <div className="aspect-square overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900">
              <img
                src={images[selectedImage] || "/placeholder.svg"}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            </div>
            {images.length > 1 && (
              <div className="grid grid-cols-4 gap-2">
                {images.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedImage(idx)}
                    className={`aspect-square rounded-lg overflow-hidden border-2 transition-all ${
                      selectedImage === idx ? 'border-primary' : 'border-zinc-800'
                    }`}
                  >
                    <img src={img || "/placeholder.svg"} alt={`Product ${idx + 1}`} className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </motion.div>

          {/* Details */}
          <motion.div initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
            <div>
              <h1
                className="text-4xl sm:text-5xl font-bold text-white uppercase mb-4"
                style={{ fontFamily: 'Teko, sans-serif' }}
              >
                {product.name}
              </h1>
              <div className="flex items-center space-x-4 mb-4">
                <div className="flex items-center text-yellow-500">
                  <span className="text-2xl mr-1">★</span>
                  <span className="text-white font-semibold">{product.rating}</span>
                  <span className="text-zinc-400 ml-2">({product.reviews_count} reviews)</span>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-primary font-bold text-4xl">
                  ₹{product.price.toLocaleString()}
                </span>
                {product.original_price && (
                  <span className="text-zinc-500 line-through text-2xl">
                    ₹{product.original_price.toLocaleString()}
                  </span>
                )}
              </div>
              {product.original_price && (
                <div className="mt-2 text-green-500 font-semibold">
                  Save ₹{(product.original_price - product.price).toLocaleString()} ({Math.round(((product.original_price - product.price) / product.original_price) * 100)}%)
                </div>
              )}
            </div>

            {/* Stock */}
            <div className="flex items-center space-x-2">
              {product.stock > 0 ? (
                <>
                  <Check className="text-green-500" size={20} />
                  <span className="text-green-500 font-semibold">In Stock ({product.stock} units)</span>
                </>
              ) : (
                <span className="text-red-500 font-semibold">Out of Stock</span>
              )}
            </div>

            {/* Description */}
            <div>
              <h3 className="text-white font-semibold text-xl mb-2 uppercase" style={{ fontFamily: 'Teko, sans-serif' }}>
                Description
              </h3>
              <p className="text-zinc-300 leading-relaxed">{product.description}</p>
            </div>

            {/* Compatibility */}
            {product.compatibility && product.compatibility.length > 0 && (
              <div>
                <h3 className="text-white font-semibold text-xl mb-2 uppercase" style={{ fontFamily: 'Teko, sans-serif' }}>
                  Compatible Bikes
                </h3>
                <div className="flex flex-wrap gap-2">
                  {product.compatibility.map((bike, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-primary/10 border border-primary/30 text-primary text-sm rounded-sm"
                    >
                      {bike.brand} {bike.model} {bike.variant}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Quantity & Actions */}
            <div className="space-y-4 pt-6 border-t border-zinc-800">
              <div className="flex items-center space-x-4">
                <span className="text-white font-semibold">Quantity:</span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="w-10 h-10 bg-zinc-800 text-white rounded hover:bg-zinc-700 transition-colors"
                  >
                    −
                  </button>
                  <span className="w-12 text-center text-white font-bold text-lg">{quantity}</span>
                  <button
                    onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                    className="w-10 h-10 bg-zinc-800 text-white rounded hover:bg-zinc-700 transition-colors"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={addToCart}
                  disabled={product.stock === 0 || adding}
                  className="flex items-center justify-center space-x-2 px-6 py-4 bg-zinc-800 border border-zinc-700 text-white hover:border-primary hover:text-primary transition-all uppercase tracking-wider disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ShoppingCart size={20} />
                  <span>{adding ? 'Adding...' : 'Add to Cart'}</span>
                </button>
                <button
                  onClick={buyNow}
                  disabled={product.stock === 0 || adding}
                  className="px-6 py-4 bg-primary text-black font-bold uppercase tracking-wider hover:bg-orange-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span>{adding ? 'Processing...' : 'Buy Now'}</span>
                </button>
              </div>

              {/* Wishlist Button */}
              <button
                onClick={() => setIsWishlisted(!isWishlisted)}
                className={`w-full py-4 border-2 rounded transition-colors ${
                  isWishlisted
                    ? 'border-primary text-primary bg-primary/10'
                    : 'border-zinc-700 text-zinc-400 hover:border-primary hover:text-primary'
                }`}
              >
                <div className="flex items-center justify-center space-x-2">
                  <Heart size={20} fill={isWishlisted ? 'currentColor' : 'none'} />
                  <span>{isWishlisted ? 'Added to Wishlist' : 'Add to Wishlist'}</span>
                </div>
              </button>

              {/* WhatsApp CTA */}
              <a
                href="https://wa.me/919876543210"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center space-x-2 px-6 py-4 bg-green-600 text-white rounded hover:bg-green-500 transition-colors"
              >
                <MessageCircle size={20} />
                <span className="font-semibold">Ask Garage Expert</span>
              </a>
            </div>
          </motion.div>
        </div>

        {/* Specifications */}
        {product.specifications && Object.keys(product.specifications).length > 0 && (
          <div className="mt-20 border-t border-zinc-800 pt-12">
            <h2
              className="text-3xl font-bold text-white uppercase mb-8"
              style={{ fontFamily: 'Teko, sans-serif' }}
            >
              Specifications
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
                {Object.entries(product.specifications).map(([key, value]) => (
                  <div key={key} className="flex justify-between py-3 border-b border-zinc-800 last:border-0">
                    <span className="text-zinc-400 capitalize">{key.replace(/_/g, ' ')}:</span>
                    <span className="text-white font-semibold">{String(value)}</span>
                  </div>
                ))}
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
                <div className="flex justify-between py-3 border-b border-zinc-800">
                  <span className="text-zinc-400">Warranty:</span>
                  <span className="text-white font-semibold">1 Year</span>
                </div>
                <div className="flex justify-between py-3 border-b border-zinc-800">
                  <span className="text-zinc-400">Installation:</span>
                  <span className="text-white font-semibold">Professional</span>
                </div>
                <div className="flex justify-between py-3">
                  <span className="text-zinc-400">Authenticity:</span>
                  <span className="text-green-500 font-semibold">✓ Verified</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductDetails;
