import React, { createContext, useContext, useState, useEffect } from 'react';

const BikeContext = createContext();

export const useBike = () => {
  const context = useContext(BikeContext);
  if (!context) {
    throw new Error('useBike must be used within BikeProvider');
  }
  return context;
};

export const BikeProvider = ({ children }) => {
  const [selectedBike, setSelectedBike] = useState(() => {
    const saved = localStorage.getItem('selectedBike');
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    if (selectedBike) {
      localStorage.setItem('selectedBike', JSON.stringify(selectedBike));
    } else {
      localStorage.removeItem('selectedBike');
    }
  }, [selectedBike]);

  const setBikeCompatibility = (brand, model, variant) => {
    setSelectedBike({ brand, model, variant });
  };

  const clearBikeCompatibility = () => {
    setSelectedBike(null);
  };

  return (
    <BikeContext.Provider value={{ selectedBike, setBikeCompatibility, clearBikeCompatibility }}>
      {children}
    </BikeContext.Provider>
  );
};
