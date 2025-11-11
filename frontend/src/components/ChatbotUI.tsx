'use client';

import { useState, useEffect, useRef } from 'react';
import PropertyCard from './PropertyCard';
import QuickFilters from './QuickFilters';
import ConfirmModal from './ConfirmModal';
import { sendMessage, saveProperty, getSavedProperties } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Property, Message } from '../types/property';
import styles from '../styles/ChatbotUI.module.css';

export default function ChatbotUI() {
  const { isAuthenticated } = useAuth();
  
  // Load messages from localStorage or use default welcome message
  const getInitialMessages = (): Message[] => {
    if (typeof window === 'undefined') return [];
    
    try {
      const savedMessages = localStorage.getItem('chatMessages');
      if (savedMessages) {
        const parsed = JSON.parse(savedMessages);
        // Convert timestamp strings back to Date objects
        return parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
      }
    } catch (error) {
      console.error('Error loading messages from localStorage:', error);
    }
    
    // Return default welcome message
    return [
      {
        id: '1',
        type: 'bot',
        content: "👋 Hi! I'm Mira, your AI real estate assistant. How can I help you find your dream home today?",
        timestamp: new Date(),
      },
    ];
  };
  
  const [messages, setMessages] = useState<Message[]>(getInitialMessages);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState<string | null>(null);
  const [savedPropertyIds, setSavedPropertyIds] = useState<Set<string>>(new Set());
  const [showFilters, setShowFilters] = useState(false);
  const [showClearModal, setShowClearModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (typeof window !== 'undefined' && messages.length > 0) {
      try {
        localStorage.setItem('chatMessages', JSON.stringify(messages));
      } catch (error) {
        console.error('Error saving messages to localStorage:', error);
      }
    }
  }, [messages]);

  // Load saved properties on mount
  useEffect(() => {
    if (isAuthenticated) {
      loadSavedProperties();
    }
  }, [isAuthenticated]);

  const loadSavedProperties = async () => {
    try {
      const response = await getSavedProperties();
      const savedProps = response.data.saved_properties || [];
      const savedIds = new Set<string>(savedProps.map((p: Property) => p.id));
      setSavedPropertyIds(savedIds);
    } catch (error) {
      console.error('Error loading saved properties:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputMessage.trim()) {
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageToSend = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);
    setShowFilters(false);

    try {
      const response = await sendMessage({
        message: messageToSend,
      });

      const botResponse = response.data.response || response.data.message || "I'm processing your request...";
      const properties: Property[] = response.data.properties || [];

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: botResponse,
        timestamp: new Date(),
        properties: properties.length > 0 ? properties : undefined,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickFilter = (filters: { location?: string; budget?: string; bedrooms?: string }) => {
    setShowFilters(false);
    const filterText = `Search for ${filters.bedrooms || 'any'} bedroom homes in ${filters.location || 'any city'} with budget ${filters.budget || 'any'}`;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: filterText,
      timestamp: new Date(),
      filters,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    sendMessage({
      message: filterText,
      filters,
    })
      .then((response) => {
        const botResponse = response.data.response || response.data.message || "Here are some properties that match your criteria.";
        const properties: Property[] = response.data.properties || [];

        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          content: botResponse,
          timestamp: new Date(),
          properties: properties.length > 0 ? properties : undefined,
        };
        setMessages((prev) => [...prev, botMessage]);
      })
      .catch((error) => {
        console.error('Error:', error);
        const errorMessage: Message = {
          id: Date.now().toString(),
          type: 'bot',
          content: "Sorry, I encountered an error. Please try again.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const handleSave = async (propertyId: string, property?: Property) => {
    // Check if already saved
    if (savedPropertyIds.has(propertyId)) {
      const message: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: "ℹ️ This property is already saved!",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, message]);
      return;
    }

    setIsSaving(propertyId);
    try {
      // Find property data from messages if not provided
      let propertyData = property;
      if (!propertyData) {
        for (const msg of messages) {
          if (msg.properties) {
            const foundProp = msg.properties.find(p => p.id === propertyId);
            if (foundProp) {
              propertyData = foundProp;
              break;
            }
          }
        }
      }
      
      // Convert property to backend format (need to reconstruct from display format)
      const backendPropertyData = propertyData ? {
        id: propertyData.id,
        title: propertyData.title,
        price: propertyData.price, // This is already formatted, but backend will handle it
        location: propertyData.location,
        bedrooms: propertyData.bedrooms,
        image_url: propertyData.image,
        image: propertyData.image
      } : undefined;
      
      const response = await saveProperty(propertyId, backendPropertyData);
      
      // Add to saved properties set immediately for better UX
      setSavedPropertyIds(prev => new Set([...prev, propertyId]));
      
      // Reload saved properties to keep in sync with backend
      await loadSavedProperties();

      const responseData = response.data || {};
      const isAlreadySaved = responseData.already_saved;
      
      const successMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: isAlreadySaved 
          ? "ℹ️ Property is already saved!" 
          : "✅ Property saved successfully! You can save multiple properties in this chat.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, successMessage]);
    } catch (error: any) {
      console.error('Error saving property:', error);
      const errorMsg = error.response?.data?.detail || 'Failed to save property';
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: `❌ ${errorMsg}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSaving(null);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle mobile viewport height changes (keyboard)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleResize = () => {
      // Force a reflow to ensure proper height calculation
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  const clearChat = () => {
    setShowClearModal(true);
  };

  const handleConfirmClear = () => {
    const welcomeMessage: Message = {
      id: '1',
      type: 'bot',
      content: "👋 Hi! I'm Mira, your AI real estate assistant. How can I help you find your dream home today?",
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
    localStorage.removeItem('chatMessages');
    setShowClearModal(false);
  };

  const handleCancelClear = () => {
    setShowClearModal(false);
  };

  return (
    <div className={styles.chatbotContainer}>
      <div className={styles.messagesContainer}>
        {messages.map((message) => (
          <div key={message.id} className={styles.messageGroup}>
            {message.content && (
              <div className={`${styles.message} ${styles[message.type]}`}>
                <div className={styles.messageContent}>
                  {message.content}
                  {message.filters && (
                    <div className={styles.filtersTag}>
                      📍 {message.filters.location || 'Any'} • 💰 {message.filters.budget || 'Any'} • 🛏️ {message.filters.bedrooms || 'Any'} beds
                    </div>
                  )}
                </div>
              </div>
            )}
            {message.properties && message.properties.length > 0 && (
              <div className={styles.propertiesContainer}>
                <div className={styles.propertiesGrid}>
                  {message.properties.map((property) => (
                    <PropertyCard
                      key={property.id}
                      property={property}
                      onSave={handleSave}
                      isSaving={isSaving === property.id}
                      isSaved={savedPropertyIds.has(property.id)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className={styles.messageGroup}>
            <div className={`${styles.message} ${styles.bot}`}>
              <div className={styles.messageContent}>
                <div className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {showFilters && (
        <div className={styles.filtersOverlay}>
          <QuickFilters onFilter={handleQuickFilter} onClose={() => setShowFilters(false)} />
        </div>
      )}

      <div className={styles.inputContainer}>
        <button
          className={styles.filterButton}
          onClick={() => setShowFilters(!showFilters)}
          title="Quick Filters"
        >
          ⚙️
        </button>
        <button
          className={styles.clearButton}
          onClick={clearChat}
          title="Clear Chat History"
        >
          🗑️
        </button>
        <form onSubmit={handleSendMessage} className={styles.inputForm}>
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (e.g., 'I'm looking for a 2 bedroom apartment in Mumbai')"
            className={styles.chatInput}
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={isLoading || !inputMessage.trim()}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>
      </div>

      <ConfirmModal
        isOpen={showClearModal}
        title="Clear Chat History"
        message="Are you sure you want to delete all chat messages? This action cannot be undone."
        confirmText="Clear Chat"
        cancelText="Cancel"
        onConfirm={handleConfirmClear}
        onCancel={handleCancelClear}
        type="danger"
      />
    </div>
  );
}
