'use client';

import { useState } from 'react';
import styles from '../styles/QuickFilters.module.css';

interface QuickFiltersProps {
  onFilter: (filters: { location?: string; budget?: string; bedrooms?: string }) => void;
  onClose: () => void;
}

export default function QuickFilters({ onFilter, onClose }: QuickFiltersProps) {
  const [location, setLocation] = useState('');
  const [budget, setBudget] = useState('');
  const [bedrooms, setBedrooms] = useState('');

  const handleApply = () => {
    if (location || budget || bedrooms) {
      onFilter({ location, budget, bedrooms });
    }
  };

  const handleClear = () => {
    setLocation('');
    setBudget('');
    setBedrooms('');
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.filtersPanel} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h3>Quick Filters</h3>
          <button onClick={onClose} className={styles.closeButton}>×</button>
        </div>
        <div className={styles.filters}>
          <div className={styles.filterGroup}>
            <label>📍 City</label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className={styles.select}
            >
              <option value="">Any City</option>
              <option value="Mumbai">Mumbai</option>
              <option value="Delhi">Delhi</option>
              <option value="Bangalore">Bangalore</option>
              <option value="Pune">Pune</option>
            </select>
          </div>

          <div className={styles.filterGroup}>
            <label>💰 Budget</label>
            <select
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className={styles.select}
            >
              <option value="">Any Budget</option>
              <option value="0-50L">0-50L</option>
              <option value="50L-1Cr">50L-1Cr</option>
              <option value="1Cr-2Cr">1Cr-2Cr</option>
            </select>
          </div>

          <div className={styles.filterGroup}>
            <label>🛏️ Bedrooms</label>
            <select
              value={bedrooms}
              onChange={(e) => setBedrooms(e.target.value)}
              className={styles.select}
            >
              <option value="">Any</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            </select>
          </div>
        </div>
        <div className={styles.actions}>
          <button onClick={handleClear} className={styles.clearButton}>
            Clear
          </button>
          <button onClick={handleApply} className={styles.applyButton}>
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
}

