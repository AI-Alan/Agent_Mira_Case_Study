'use client';

import { useState, useEffect, useRef } from 'react';
import FilterForm from './FilterForm';
import PropertyCard from './PropertyCard';
import { getProperties, saveProperty } from '../lib/api';
import styles from '../styles/ChatbotUI.module.css';

interface Message {
  id: string;
  type: 'bot' | 'user';
  content: string;
  timestamp: Date;
}

interface Property {
  id: string;
  title: string;
  price: string;
  location: string;
  bedrooms: number;
  image?: string;
}

interface SearchResult {
  properties: Property[];
  filters: {
    location: string;
    budget: string;
    bedrooms: string;
  };
}

export default function ChatbotUI() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: "👋 Hi! I'm Mira. Let's find your dream home.",
      timestamp: new Date(),
    },
  ]);
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, searchResults]);

  const handleSearch = async (filters: { location: string; budget: string; bedrooms: string }) => {
    setIsLoading(true);
    // Clear previous results when starting a new search
    setSearchResults(null);
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: `Looking for ${filters.bedrooms} bedroom homes in ${filters.location} with budget ${filters.budget}`,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await getProperties(filters);
      const properties = response.data.properties || response.data || [];
      
      // Add bot message
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: properties.length > 0 
          ? "Here are some homes that match your choices." 
          : "Sorry, no properties found matching your criteria. Please try different filters.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
      
      if (properties.length > 0) {
        setSearchResults({
          properties,
          filters,
        });
      }
    } catch (error) {
      console.error('Error fetching properties:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: "Sorry, I encountered an error while searching. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async (propertyId: string) => {
    setIsSaving(propertyId);
    try {
      // For now, using a placeholder user_id. In a real app, this would come from auth context
      const user_id = 'user_123';
      await saveProperty({ user_id, property_id: propertyId });
      
      const successMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: "✅ Saved successfully!",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, successMessage]);
    } catch (error) {
      console.error('Error saving property:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: "❌ Failed to save property. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSaving(null);
    }
  };

  return (
    <div className={styles.chatbotContainer}>
      <div className={styles.messagesContainer}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`${styles.message} ${styles[message.type]}`}
          >
            <div className={styles.messageContent}>
              {message.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className={`${styles.message} ${styles.bot}`}>
            <div className={styles.messageContent}>
              <span className={styles.loading}>Searching for properties...</span>
            </div>
          </div>
        )}

        {searchResults && searchResults.properties.length > 0 && (
          <div className={styles.resultsContainer}>
            <div className={styles.propertiesGrid}>
              {searchResults.properties.map((property) => (
                <PropertyCard
                  key={property.id}
                  property={property}
                  onSave={handleSave}
                  isSaving={isSaving === property.id}
                />
              ))}
            </div>
          </div>
        )}

        {!isLoading && (
          <div className={styles.filterContainer}>
            <FilterForm onSearch={handleSearch} />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

