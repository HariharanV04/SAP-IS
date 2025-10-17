import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText } from 'lucide-react';

const Header: React.FC = () => {
  const location = useLocation();

  return (
    <header className="bg-white shadow-sm border-b-2 border-company-orange-500">
      <div className="container mx-auto px-4 py-3 max-w-4xl">
        {/* Main header layout with logo on left, title centered */}
        <div className="flex justify-between items-center h-16">
          {/* Company Logo positioned at extreme left */}
          <div className="flex-shrink-0">
            {/* Company Logo */}
            <img
              src="/static/images/company-logo.png"
              alt="Company Logo"
              className="h-12 w-auto"
              onError={(e) => {
                // Fallback to icon if image fails to load
                e.currentTarget.style.display = 'none';
                const fallbackIcon = document.getElementById('fallback-icon');
                if (fallbackIcon) {
                  fallbackIcon.style.display = 'block';
                }
              }}
            />
            {/* Fallback icon if logo image is not found */}
            <FileText id="fallback-icon" className="h-10 w-10 text-company-orange-600" style={{display: 'none'}} />
          </div>

          {/* Center-aligned title and navigation */}
          <div className="flex-grow flex flex-col items-center justify-center">
            <h1 className="text-2xl font-bold text-company-orange-600 mb-2">Integration Flow Analyzer</h1>

            {/* Navigation links */}
            <nav className="flex space-x-8">
              <Link
                to="/"
                className={`font-medium ${
                  location.pathname === '/'
                    ? 'text-company-orange-600 border-b-2 border-company-orange-600'
                    : 'text-gray-600 hover:text-company-orange-600 transition-colors duration-200'
                }`}
              >
                Home
              </Link>
              <Link
                to="/api_docs"
                className={`font-medium ${
                  location.pathname === '/api_docs'
                    ? 'text-company-orange-600 border-b-2 border-company-orange-600'
                    : 'text-gray-600 hover:text-company-orange-600 transition-colors duration-200'
                }`}
              >
                API Documentation
              </Link>
            </nav>
          </div>

          {/* Empty div to balance the layout */}
          <div className="flex-shrink-0 w-12"></div>
        </div>
      </div>
    </header>
  );
};

export default Header;