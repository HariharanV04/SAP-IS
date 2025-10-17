import React from 'react';
import { Route, Routes, BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Home from './pages/Home';
import ApiDocs from './pages/ApiDocs';
import './index.css';

function App() {
  const handleLogoLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    e.currentTarget.style.display = 'block';
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Toaster
          position="top-right"
          toastOptions={{
            success: {
              style: {
                background: '#fff8f1',
                border: '1px solid #ff7a1a',
                color: '#7a3100',
              },
              iconTheme: {
                primary: '#ff6600',
                secondary: '#fff8f1',
              },
            },
            error: {
              style: {
                background: '#fff8f1',
                border: '1px solid #ff6600',
                color: '#7a3100',
              },
            },
          }}
        />
        <Header />
        <main className="container mx-auto px-4 py-8 max-w-4xl">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/api_docs" element={<ApiDocs />} />
          </Routes>
        </main>
        <footer className="bg-white border-t border-company-orange-200 py-5 mt-8">
          <div className="container mx-auto px-4 max-w-4xl text-center text-sm text-gray-500">
            <div className="flex flex-col items-center">
              <img
                src="/static/images/company-logo-small.png"
                alt="Company Logo"
                className="h-8 w-auto mb-3"
                style={{ display: 'none' }}
                onLoad={handleLogoLoad}
              />
              <p>© {new Date().getFullYear()} IT Resonance • Integration Flow Analyzer</p>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;