'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ChevronRight, Zap, Shield, Package, Search } from 'lucide-react';
import { API } from '../context/AuthContext';
import { useBike } from '../context/BikeContext';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const Home = () => {
  const navigate = useNavigate();
  const { setBikeCompatibility } = useBike();
  const [brands, setBrands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
 const [selectedBrand, setSelectedBrand] = useState(undefined);
const [selectedModel, setSelectedModel] = useState(undefined);
const [selectedVariant, setSelectedVariant] = useState(undefined);

  const [models, setModels] = useState([]);
  const [variants, setVariants] = useState([]);
  const [searchInput, setSearchInput] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearch, setShowSearch] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedBrand) {
      fetchModels(selectedBrand);
    }
  }, [selectedBrand]);

  useEffect(() => {
    if (selectedBrand && selectedModel) {
      fetchVariants(selectedBrand, selectedModel);
    }
  }, [selectedModel]);

  // Search handler
  useEffect(() => {
    if (searchInput.trim().length > 1) {
      searchProducts();
    } else {
      setSearchResults([]);
      setShowSearch(false);
    }
  }, [searchInput]);

  const fetchData = async () => {
    try {
      const [brandsRes, categoriesRes, productsRes] = await Promise.all([
        axios.get(`${API}/bikes/brands`),
        axios.get(`${API}/categories`),
        axios.get(`${API}/products?best_sellers=true`)
      ]);
      setBrands(brandsRes.data);
      setCategories(categoriesRes.data);
      setProducts(productsRes.data.slice(0, 8));
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

const fetchModels = async (brand) => {
  setSelectedModel(undefined);
  setSelectedVariant(undefined);
  setVariants([]);

  const response = await axios.get(`${API}/bikes/models/${brand}`);
  setModels(response.data);
};
const fetchVariants = async (brand, model) => {
  setSelectedVariant(undefined);

  const response = await axios.get(
    `${API}/bikes/variants/${brand}/${model}`
  );
  setVariants(response.data);
};



  const searchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products/search?q=${searchInput}&limit=6`);
      setSearchResults(response.data);
      setShowSearch(true);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

 const handleExploreGear = () => {
  if (selectedBrand && selectedModel && selectedVariant) {
    setBikeCompatibility(selectedBrand, selectedModel, selectedVariant);

    navigate(
      `/products?bike_brand=${encodeURIComponent(selectedBrand)}&bike_model=${encodeURIComponent(selectedModel)}&bike_variant=${encodeURIComponent(selectedVariant)}`
    );
  } else {
    navigate('/products');
  }
};


  const handleBrandClick = (brandName) => {
    setSelectedBrand(brandName);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleProductSelect = (productId) => {
    navigate(`/products/${productId}`);
    setSearchInput('');
    setShowSearch(false);
  };

  return (
    <div className="min-h-screen bg-black pt-20">
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1553940085-7c4bd7911c90?crop=entropy&cs=srgb&fm=jpg&q=85"
            alt="Hero Bike"
            className="w-full h-full object-cover opacity-40"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1
              className="text-5xl sm:text-7xl lg:text-8xl font-bold mb-6 uppercase"
              style={{ fontFamily: 'Teko, sans-serif' }}
            >
              <span className="text-white">Level Up</span>
              <br />
              <span className="text-primary text-shadow-glow">Level The Ride.</span>
            </h1>
            <p className="text-zinc-300 text-lg sm:text-xl mb-12 max-w-2xl mx-auto">
              Discover India's most trusted collection of genuine spares & Upgrades
            </p>

            {/* Bike Compatibility Selector */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="max-w-4xl mx-auto mb-8"
            >
              <div className="backdrop-blur-xl bg-black/60 border border-white/10 p-6 sm:p-8 rounded-lg">
                <h3 className="text-white text-xl sm:text-2xl font-semibold mb-6 uppercase" style={{ fontFamily: 'Teko, sans-serif' }}>
                  Find Parts For Your Bike
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
{/* BRAND */}
<Select
  value={
    brands.some(b => b.name === selectedBrand)
      ? selectedBrand
      : undefined
  }
  onValueChange={setSelectedBrand}
>
  <SelectTrigger className="bg-zinc-900/80 border-zinc-700 text-white">
    <SelectValue placeholder="Select Brand" />
  </SelectTrigger>
  <SelectContent className="bg-zinc-900 border-zinc-700">
    {brands.map((brand) => (
      <SelectItem
        key={brand.name}
        value={brand.name}
        className="text-white hover:bg-zinc-800"
      >
        {brand.name}
      </SelectItem>
    ))}
  </SelectContent>
</Select>

{/* MODEL */}
<Select
  value={
    models.includes(selectedModel)
      ? selectedModel
      : undefined
  }
  onValueChange={setSelectedModel}
  disabled={!selectedBrand}
>
  <SelectTrigger className="bg-zinc-900/80 border-zinc-700 text-white">
    <SelectValue placeholder="Select Model" />
  </SelectTrigger>
  <SelectContent className="bg-zinc-900 border-zinc-700">
    {models.map((model) => (
      <SelectItem
        key={model}
        value={model}
        className="text-white hover:bg-zinc-800"
      >
        {model}
      </SelectItem>
    ))}
  </SelectContent>
</Select>

{/* VARIANT */}
<Select
  value={
    variants.includes(selectedVariant)
      ? selectedVariant
      : undefined
  }
  onValueChange={setSelectedVariant}
  disabled={!selectedModel}
>
  <SelectTrigger className="bg-zinc-900/80 border-zinc-700 text-white">
    <SelectValue placeholder="Select Variant" />
  </SelectTrigger>
  <SelectContent className="bg-zinc-900 border-zinc-700">
    {variants.map((variant) => (
      <SelectItem
        key={variant}
        value={variant}
        className="text-white hover:bg-zinc-800"
      >
        {variant}
      </SelectItem>
    ))}
  </SelectContent>
</Select>

                </div>
                <button
                  onClick={handleExploreGear}
                  className="w-full mt-6 px-8 py-4 bg-primary text-black font-bold uppercase tracking-wider hover:bg-orange-400 transition-all text-lg"
                >
                  <span className="flex items-center justify-center">
                    Explore Gear
                    <ChevronRight className="ml-2" size={20} />
                  </span>
                </button>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Search Section */}
      <section className="py-12 bg-gradient-to-b from-black to-zinc-950 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <div className="relative flex items-center">
                <Search className="absolute left-4 text-primary" size={20} />
                <input
                  type="text"
                  placeholder="Search products, brands, categories..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-zinc-900 border-2 border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-primary transition-colors"
                />
              </div>

              {/* Search Results Dropdown */}
              {showSearch && searchResults.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute top-full left-0 right-0 mt-2 bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden shadow-2xl"
                >
                  <div className="max-h-80 overflow-y-auto">
                    {searchResults.map((product) => (
                      <button
                        key={product.id}
                        onClick={() => handleProductSelect(product.id)}
                        className="w-full flex items-center space-x-4 px-4 py-3 hover:bg-zinc-800 transition-colors border-b border-zinc-800 last:border-0 text-left"
                      >
                        <img
                          src={product.images?.[0] || 'https://via.placeholder.com/50'}
                          alt={product.name}
                          className="w-12 h-12 rounded object-cover"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-white text-sm font-medium truncate">{product.name}</p>
                          <p className="text-primary text-xs font-bold">₹{product.price.toLocaleString()}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Shop By Brand Section */}
      <section className="py-24 bg-gradient-to-b from-black to-zinc-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl sm:text-6xl font-bold text-white uppercase mb-4" style={{ fontFamily: 'Teko, sans-serif' }}>
              Shop By <span className="text-primary">Bike Brand</span>
            </h2>
            <p className="text-zinc-400 text-lg">Choose your ride, we'll show you the perfect parts</p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {brands.map((brand, index) => (
              <motion.div
                key={brand.name}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                onClick={() => handleBrandClick(brand.name)}
                className="relative group cursor-pointer"
              >
                <div className="aspect-square rounded-full overflow-hidden border-4 border-zinc-800 group-hover:border-primary transition-all">
                  <img src={brand.logo || "/placeholder.svg"} alt={brand.name} className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-black/60 group-hover:bg-black/40 transition-all" />
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span
                    className="text-2xl font-bold text-white uppercase tracking-wider text-center"
                    style={{ fontFamily: 'Teko, sans-serif' }}
                  >
                    {brand.name}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-24 bg-zinc-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl sm:text-6xl font-bold text-white uppercase mb-4" style={{ fontFamily: 'Teko, sans-serif' }}>
              Shop By <span className="text-primary">Category</span>
            </h2>
            <p className="text-zinc-400">Find what you're looking for</p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {categories.map((category, index) => (
              <motion.div
                key={category.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -8 }}
onClick={() => navigate(`/products?category=${category.id}`)}
                className="relative h-64 overflow-hidden group cursor-pointer border border-zinc-800 hover:border-primary/50 transition-all rounded-lg"
              >
                <img src={category.image || "/placeholder.svg"} alt={category.name} className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/70 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-6">
                  <h3
                    className="text-2xl font-bold text-white uppercase mb-2 group-hover:text-primary transition-colors"
                    style={{ fontFamily: 'Teko, sans-serif' }}
                  >
                    {category.name}
                  </h3>
                  <p className="text-zinc-400 text-sm">Browse collection</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Best Sellers Section */}
      <section className="py-24 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl sm:text-6xl font-bold text-white uppercase mb-4" style={{ fontFamily: 'Teko, sans-serif' }}>
              Best <span className="text-primary">Sellers</span>
            </h2>
            <p className="text-zinc-400">Most loved products by our customers</p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -8 }}
                onClick={() => navigate(`/products/${product.id}`)}
                className="bg-zinc-900 border border-zinc-800 hover:border-primary/50 transition-all cursor-pointer rounded-lg overflow-hidden"
              >
                <div className="aspect-square overflow-hidden relative">
                  <img src={product.images?.[0] || 'https://via.placeholder.com/300'} alt={product.name} className="w-full h-full object-cover" />
                  {product.is_best_seller && (
                    <div className="absolute top-2 right-2 bg-primary text-black px-2 py-1 text-xs font-bold uppercase">Best Seller</div>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="text-white font-semibold mb-2 uppercase line-clamp-2" style={{ fontFamily: 'Teko, sans-serif' }}>
                    {product.name}
                  </h3>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-primary font-bold text-xl">₹{product.price.toLocaleString()}</span>
                      {product.original_price && (
                        <span className="text-zinc-500 line-through ml-2 text-sm">
                          ₹{product.original_price.toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="mt-2 flex items-center text-xs text-zinc-400">
                    <span className="text-yellow-500 mr-1">★</span>
                    {product.rating} ({product.reviews_count} reviews)
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <button
              onClick={() => navigate('/products')}
              className="px-8 py-4 bg-primary text-black font-bold uppercase tracking-wider hover:bg-orange-400 transition-all"
            >
              <span>View All Products</span>
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-zinc-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center p-8 backdrop-blur-xl bg-black/40 border border-white/10 rounded-lg"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-4">
                <Zap className="text-primary" size={32} />
              </div>
              <h3 className="text-white font-bold text-xl mb-2 uppercase" style={{ fontFamily: 'Teko, sans-serif' }}>
                Performance Parts
              </h3>
              <p className="text-zinc-400">Upgrade your ride with premium performance parts</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-center p-8 backdrop-blur-xl bg-black/40 border border-white/10 rounded-lg"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-4">
                <Shield className="text-primary" size={32} />
              </div>
              <h3 className="text-white font-bold text-xl mb-2 uppercase" style={{ fontFamily: 'Teko, sans-serif' }}>
                Genuine Quality
              </h3>
              <p className="text-zinc-400">100% authentic parts with warranty</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-center p-8 backdrop-blur-xl bg-black/40 border border-white/10 rounded-lg"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-4">
                <Package className="text-primary" size={32} />
              </div>
              <h3 className="text-white font-bold text-xl mb-2 uppercase" style={{ fontFamily: 'Teko, sans-serif' }}>
                Fast Delivery
              </h3>
              <p className="text-zinc-400">Quick delivery across India</p>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
