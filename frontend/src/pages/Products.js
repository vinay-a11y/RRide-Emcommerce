'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Filter, X, ChevronDown } from 'lucide-react';
import { API } from '../context/AuthContext';
import { useBike } from '../context/BikeContext';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';

const Products = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { selectedBike } = useBike();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  /* ================= FILTER STATE (RADIX SAFE) ================= */

  const [filters, setFilters] = useState({
    category: searchParams.get('category') || '__all__',
    brand: '__all__',
    minPrice: '',
    maxPrice: '',
    sortBy: 'latest',
  });

  /* ================= EFFECTS ================= */

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [filters, selectedBike]);

  /* ================= API ================= */

  const fetchInitialData = async () => {
    try {
      const [categoriesRes, brandsRes] = await Promise.all([
        axios.get(`${API}/categories`),
        axios.get(`${API}/brands`),
      ]);
      setCategories(categoriesRes.data || []);
      setBrands(brandsRes.data || []);
    } catch (err) {
      console.error('Failed to fetch filters:', err);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();

      if (filters.category !== '__all__') {
        params.append('category', filters.category);
      }

      if (filters.brand !== '__all__') {
        params.append('brand', filters.brand);
      }

      if (filters.minPrice) {
        params.append('min_price', filters.minPrice);
      }

      if (filters.maxPrice) {
        params.append('max_price', filters.maxPrice);
      }

      if (filters.sortBy !== 'latest') {
        params.append('sort_by', filters.sortBy);
      }

      if (selectedBike) {
        params.append('bike_brand', selectedBike.brand);
        params.append('bike_model', selectedBike.model);
        params.append('bike_variant', selectedBike.variant);
      }

      const res = await axios.get(`${API}/products?${params.toString()}`);
      setProducts(res.data || []);
    } catch (err) {
      console.error('Failed to fetch products:', err);
    } finally {
      setLoading(false);
    }
  };

  /* ================= HELPERS ================= */

  const updateFilter = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      category: '__all__',
      brand: '__all__',
      minPrice: '',
      maxPrice: '',
      sortBy: 'latest',
    });
  };

  /* ================= RENDER ================= */

  return (
    <div className="min-h-screen bg-black pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4">

        {/* HEADER */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-white uppercase mb-4">
            Shop <span className="text-primary">Parts</span>
          </h1>
          {selectedBike && (
            <p className="text-zinc-400">
              Compatible with {selectedBike.brand} {selectedBike.model} {selectedBike.variant}
            </p>
          )}
        </div>

        {/* FILTERS */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 mb-8">
          <button
            onClick={() => setShowMobileFilters(!showMobileFilters)}
            className="md:hidden flex items-center gap-2 text-white"
          >
            <Filter size={18} />
            Filters
            <ChevronDown
              className={`transition-transform ${showMobileFilters ? 'rotate-180' : ''}`}
            />
          </button>

          <div className={`${showMobileFilters ? 'flex' : 'hidden'} md:flex flex-wrap gap-4 mt-4`}>

            {/* CATEGORY */}
            <Select
              value={filters.category}
              onValueChange={(val) => updateFilter('category', val)}
            >
              <SelectTrigger className="w-40 bg-zinc-800 text-white">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">All Categories</SelectItem>
                {categories.map((c) => (
                  <SelectItem key={c.id} value={c.id}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* BRAND */}
            <Select
              value={filters.brand}
              onValueChange={(val) => updateFilter('brand', val)}
            >
              <SelectTrigger className="w-40 bg-zinc-800 text-white">
                <SelectValue placeholder="Brand" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">All Brands</SelectItem>
                {brands.map((b) => (
                  <SelectItem key={b.id} value={b.id}>
                    {b.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* SORT */}
            <Select
              value={filters.sortBy}
              onValueChange={(val) => updateFilter('sortBy', val)}
            >
              <SelectTrigger className="w-44 bg-zinc-800 text-white">
                <SelectValue placeholder="Sort By" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="latest">Latest</SelectItem>
                <SelectItem value="price_low">Price: Low to High</SelectItem>
                <SelectItem value="price_high">Price: High to Low</SelectItem>
                <SelectItem value="popularity">Popularity</SelectItem>
              </SelectContent>
            </Select>

            {(filters.category !== '__all__' ||
              filters.brand !== '__all__' ||
              filters.sortBy !== 'latest') && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-2 text-zinc-400 hover:text-primary ml-auto"
              >
                <X size={16} /> Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* PRODUCTS */}
        {loading ? (
          <p className="text-zinc-400">Loading products...</p>
        ) : products.length === 0 ? (
          <div className="text-center py-20 text-zinc-400">
            No products found
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map((p, i) => (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => navigate(`/products/${p.id}`)}
                className="bg-zinc-900 border border-zinc-800 rounded-lg cursor-pointer overflow-hidden"
              >
                <img
                  src={p.images?.[0] || 'https://via.placeholder.com/300'}
                  className="w-full h-64 object-cover"
                />
                <div className="p-4">
                  <h3 className="text-white font-semibold uppercase line-clamp-2">
                    {p.name}
                  </h3>
                  <p className="text-primary font-bold mt-2">
                    ₹{p.price.toLocaleString()}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Products;
