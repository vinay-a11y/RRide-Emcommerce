import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MessageCircle } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-black border-t border-zinc-900 pt-16 pb-8" data-testid="footer">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="text-2xl font-bold mb-4" style={{ fontFamily: 'Teko, sans-serif' }}>
              <span className="text-white">RRIDE</span>
              <span className="text-primary ml-1">GARAGE</span>
            </div>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Discover India's most trusted collection of genuine spares & upgrade.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 uppercase tracking-wider" style={{ fontFamily: 'Teko, sans-serif' }}>
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li>
                <Link to="/products" className="text-zinc-400 hover:text-primary transition-colors text-sm">
                  Shop
                </Link>
              </li>
              <li>
                <Link to="/orders" className="text-zinc-400 hover:text-primary transition-colors text-sm">
                  Track Order
                </Link>
              </li>
            </ul>
          </div>

          {/* Categories */}
          <div>
            <h3 className="text-white font-semibold mb-4 uppercase tracking-wider" style={{ fontFamily: 'Teko, sans-serif' }}>
              Categories
            </h3>
            <ul className="space-y-2">
              <li>
                <Link to="/products?category=performance" className="text-zinc-400 hover:text-primary transition-colors text-sm">
                  Performance
                </Link>
              </li>
              <li>
                <Link to="/products?category=safety_gear" className="text-zinc-400 hover:text-primary transition-colors text-sm">
                  Safety Gear
                </Link>
              </li>
              <li>
                <Link to="/products?category=pro_spares" className="text-zinc-400 hover:text-primary transition-colors text-sm">
                  Pro Spares
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-white font-semibold mb-4 uppercase tracking-wider" style={{ fontFamily: 'Teko, sans-serif' }}>
              Support
            </h3>
            <a
              href="https://wa.me/919876543210"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-sm hover:bg-green-500 transition-colors"
              data-testid="whatsapp-btn"
            >
              <MessageCircle size={18} />
              <span className="text-sm font-semibold">WhatsApp Expert</span>
            </a>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-zinc-900 text-center">
          <p className="text-zinc-500 text-sm">
            © 2024 RRIDE GARAGE. All rights reserved. | Built for Riders, By Riders.
          </p>
        </div>
      </div>
    </footer>
  );
};
