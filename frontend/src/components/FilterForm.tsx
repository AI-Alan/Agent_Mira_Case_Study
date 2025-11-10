'use client';

import { useState } from 'react';
import styles from '../styles/FilterForm.module.css';

interface FilterFormProps {
  onSearch: (filters: { location: string; budget: string; bedrooms: string }) => void;
}

export default function FilterForm({ onSearch }: FilterFormProps) {
  const [location, setLocation] = useState('');
  const [budget, setBudget] = useState('');
  const [bedrooms, setBedrooms] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (location && budget && bedrooms) {
      onSearch({ location, budget, bedrooms });
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.formGroup}>
        <label htmlFor="location" className={styles.label}>City</label>
        <select
          id="location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className={styles.select}
          required
        >
          <option value="">Select City</option>
          <option value="Mumbai">Mumbai</option>
          <option value="Delhi">Delhi</option>
          <option value="Bangalore">Bangalore</option>
          <option value="Pune">Pune</option>
        </select>
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="budget" className={styles.label}>Budget</label>
        <select
          id="budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          className={styles.select}
          required
        >
          <option value="">Select Budget</option>
          <option value="0-50L">0-50L</option>
          <option value="50L-1Cr">50L-1Cr</option>
          <option value="1Cr-2Cr">1Cr-2Cr</option>
        </select>
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="bedrooms" className={styles.label}>Bedrooms</label>
        <select
          id="bedrooms"
          value={bedrooms}
          onChange={(e) => setBedrooms(e.target.value)}
          className={styles.select}
          required
        >
          <option value="">Select Bedrooms</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
        </select>
      </div>

      <button type="submit" className={styles.button}>
        Find Homes
      </button>
    </form>
  );
}

