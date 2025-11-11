'use client';

import { Property } from '../types/property';
import styles from '../styles/PropertyCard.module.css';

interface PropertyCardProps {
  property: Property;
  onSave: (propertyId: string, property?: Property) => void;
  isSaving?: boolean;
  isSaved?: boolean;
}

export default function PropertyCard({ property, onSave, isSaving = false, isSaved = false }: PropertyCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.imageContainer}>
        {property.image ? (
          <img src={property.image} alt={property.title} className={styles.image} />
        ) : (
          <div className={styles.placeholderImage}>🏠</div>
        )}
        {isSaved && (
          <div className={styles.savedBadge}>✓ Saved</div>
        )}
      </div>
      <div className={styles.content}>
        <h3 className={styles.title}>{property.title}</h3>
        <p className={styles.price}>{property.price}</p>
        <p className={styles.location}>📍 {property.location}</p>
        <p className={styles.bedrooms}>🛏️ {property.bedrooms} Bedrooms</p>
        <button 
          onClick={() => onSave(property.id, property)} 
          className={`${styles.saveButton} ${isSaved ? styles.saved : ''}`}
          disabled={isSaving || isSaved}
        >
          {isSaving ? 'Saving...' : isSaved ? '✓ Saved' : 'Save'}
        </button>
      </div>
    </div>
  );
}

