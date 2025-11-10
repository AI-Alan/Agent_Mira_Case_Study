'use client';

import styles from '../styles/PropertyCard.module.css';

interface Property {
  id: string;
  title: string;
  price: string;
  location: string;
  bedrooms: number;
  image?: string;
}

interface PropertyCardProps {
  property: Property;
  onSave: (propertyId: string) => void;
  isSaving?: boolean;
}

export default function PropertyCard({ property, onSave, isSaving = false }: PropertyCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.imageContainer}>
        {property.image ? (
          <img src={property.image} alt={property.title} className={styles.image} />
        ) : (
          <div className={styles.placeholderImage}>🏠</div>
        )}
      </div>
      <div className={styles.content}>
        <h3 className={styles.title}>{property.title}</h3>
        <p className={styles.price}>₹{property.price}</p>
        <p className={styles.location}>📍 {property.location}</p>
        <p className={styles.bedrooms}>🛏️ {property.bedrooms} Bedrooms</p>
        <button 
          onClick={() => onSave(property.id)} 
          className={styles.saveButton}
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save'}
        </button>
      </div>
    </div>
  );
}

