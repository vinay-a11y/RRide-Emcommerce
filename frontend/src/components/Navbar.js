'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShoppingCart,
  User,
  Menu,
  X,
  Search,
} from 'lucide-react';
import axios from 'axios';

import { useAuth } from '../context/AuthContext';
import { useBike } from '../context/BikeContext';

/* =========================================================
   CONFIG
========================================================= */
const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/* =========================================================
   NAVBAR COMPONENT
========================================================= */
const Navbar = ({ cartCount = 0 }) => {
  /* ---------------- STATE ---------------- */
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);

  /* ---------------- CONTEXT ---------------- */
  const { user, logout } = useAuth();
  const { selectedBike, clearBikeCompatibility } = useBike();

  /* ---------------- ROUTING ---------------- */
  const navigate = useNavigate();
  const location = useLocation();

  /* ---------------- REFS ---------------- */
  const searchRef = useRef(null);

  /* =========================================================
     SEARCH LOGIC (BACKEND: /products/search)
  ========================================================= */
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        const res = await axios.get(`${API}/products/search`, {
          params: { q: searchQuery, limit: 8 },
        });
        setSearchResults(res.data || []);
        setShowResults(true);
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  /* =========================================================
     CLOSE SEARCH DROPDOWN ON OUTSIDE CLICK
  ========================================================= */
  useEffect(() => {
    const handler = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowResults(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  /* =========================================================
     HELPERS
  ========================================================= */
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleProductSelect = (productId) => {
    setSearchQuery('');
    setShowResults(false);
    navigate(`/products/${productId}`);
  };

  const closeMobileMenu = () => setIsMenuOpen(false);

  const isActive = (path) =>
    location.pathname + location.search === path;

  /* =========================================================
     RENDER
  ========================================================= */
  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 w-full z-50 bg-black/80 backdrop-blur-xl border-b border-white/5"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* =====================================================
            TOP BAR
        ====================================================== */}
        <div className="flex items-center justify-between h-20">
          {/* LOGO */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-white">RRIDE</span>
            <span className="text-2xl font-bold text-primary">GARAGE</span>
          </Link>

          {/* =====================================================
              DESKTOP NAV LINKS
          ====================================================== */}
          <div className="hidden lg:flex items-center gap-8 ml-12">
            <NavItem to="/products" label="All Products" />
            <NavItem to="/products?type=spare" label="Spares" />
            <NavItem to="/products?type=accessory" label="Accessories" />
          </div>

          {/* =====================================================
              SEARCH (DESKTOP)
          ====================================================== */}
          <div
            className="hidden md:block flex-1 max-w-md mx-6"
            ref={searchRef}
          >
            <div className="relative">
              <Search
                size={18}
                className="absolute left-3 top-3 text-zinc-500"
              />
              <input
                type="text"
                placeholder="Search parts, brands, accessories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-white placeholder-zinc-500 focus:outline-none focus:border-primary"
              />

              {/* SEARCH RESULTS */}
              <AnimatePresence>
                {showResults && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full left-0 right-0 mt-2 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl overflow-hidden z-50"
                  >
                    {loading && (
                      <div className="p-4 text-sm text-zinc-400 text-center">
                        Searching…
                      </div>
                    )}

                    {!loading && searchResults.length === 0 && (
                      <div className="p-4 text-sm text-zinc-400 text-center">
                        No products found
                      </div>
                    )}

                    {!loading &&
                      searchResults.map((product) => (
                        <button
                          key={product.id}
                          onClick={() =>
                            handleProductSelect(product.id)
                          }
                          className="w-full flex items-center gap-3 px-4 py-3 hover:bg-zinc-800 transition border-b border-zinc-800 last:border-0 text-left"
                        >
                          <img
                            src={
                              product.images?.[0] ||
                              'https://via.placeholder.com/40'
                            }
                            alt={product.name}
                            className="w-10 h-10 rounded object-cover"
                          />
                          <div className="flex-1">
                            <p className="text-white text-sm truncate">
                              {product.name}
                            </p>
                            <p className="text-primary text-xs font-bold">
                              ₹{product.price}
                            </p>
                          </div>
                        </button>
                      ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* =====================================================
              RIGHT SIDE ACTIONS
          ====================================================== */}
          <div className="flex items-center gap-4">
            {/* BIKE BADGE */}
            {selectedBike && (
              <div className="hidden xl:flex items-center gap-2 px-3 py-2 bg-zinc-900 border border-primary/30 rounded-sm text-xs">
                <span className="text-primary font-semibold">
                  {selectedBike.brand} {selectedBike.model}
                </span>
                <button
                  onClick={clearBikeCompatibility}
                  className="text-zinc-400 hover:text-white"
                >
                  <X size={14} />
                </button>
              </div>
            )}

            {/* CART */}
            <Link
              to="/cart"
              className="relative text-zinc-400 hover:text-primary"
            >
              <ShoppingCart size={22} />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-primary text-black text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                  {cartCount}
                </span>
              )}
            </Link>

            {/* USER */}
            {user ? (
              <div className="relative group">
                <User className="text-zinc-400 hover:text-primary" />
                <div className="absolute right-0 mt-2 w-44 bg-zinc-900 border border-zinc-800 rounded-sm opacity-0 invisible group-hover:opacity-100 group-hover:visible transition">
                  <Link
                    to="/orders"
                    className="block px-4 py-3 text-sm text-zinc-300 hover:bg-zinc-800"
                  >
                    My Orders
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-3 text-sm text-zinc-300 hover:bg-zinc-800"
                  >
                    Logout
                  </button>
                </div>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 bg-primary text-black font-bold text-sm uppercase hover:bg-orange-400"
              >
                Login
              </Link>
            )}

            {/* MOBILE TOGGLE */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="lg:hidden text-zinc-400 hover:text-primary"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* =====================================================
            MOBILE MENU
        ====================================================== */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="lg:hidden border-t border-zinc-800 pb-4"
            >
              <div className="flex flex-col gap-4 pt-4">
                <MobileNavItem
                  to="/products"
                  label="All Products"
                  onClick={closeMobileMenu}
                />
                <MobileNavItem
                  to="/products?type=spare"
                  label="Spares"
                  onClick={closeMobileMenu}
                />
                <MobileNavItem
                  to="/products?type=accessory"
                  label="Accessories"
                  onClick={closeMobileMenu}
                />

                {selectedBike && (
                  <div className="mx-4 mt-2 flex items-center justify-between px-3 py-2 bg-zinc-900 border border-primary/30">
                    <span className="text-primary text-sm font-semibold">
                      {selectedBike.brand} {selectedBike.model}
                    </span>
                    <button
                      onClick={clearBikeCompatibility}
                      className="text-zinc-400"
                    >
                      <X size={16} />
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.nav>
  );
};

/* =========================================================
   SUB COMPONENTS
========================================================= */
const NavItem = ({ to, label }) => (
  <Link
    to={to}
    className="text-sm uppercase tracking-widest text-zinc-400 hover:text-primary transition"
  >
    {label}
  </Link>
);

const MobileNavItem = ({ to, label, onClick }) => (
  <Link
    to={to}
    onClick={onClick}
    className="px-4 text-sm uppercase tracking-widest text-zinc-400 hover:text-primary"
  >
    {label}
  </Link>
);

export default Navbar;
