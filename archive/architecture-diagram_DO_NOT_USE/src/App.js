import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ArchitectureDiagram from './components/ArchitectureDiagram';
import './App.css';

function App() {
  const [selectedComponent, setSelectedComponent] = useState(null);

  return (
    <div className="App min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-lg border-b-4 border-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              MuleSoft to SAP Integration Suite
            </h1>
            <p className="text-xl text-gray-600">
              AI-Powered Migration Architecture
            </p>
          </motion.div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="bg-white rounded-2xl shadow-2xl overflow-hidden"
        >
          <ArchitectureDiagram 
            selectedComponent={selectedComponent}
            setSelectedComponent={setSelectedComponent}
          />
        </motion.div>

        {selectedComponent && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mt-8 bg-white rounded-xl shadow-lg p-6"
          >
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {selectedComponent.title}
            </h3>
            <p className="text-gray-700 mb-4">
              {selectedComponent.description}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Key Features:</h4>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  {selectedComponent.features?.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Technologies:</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedComponent.technologies?.map((tech, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </main>

      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2024 IT Resonance • MuleSoft to SAP Integration Suite Migration Platform
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
