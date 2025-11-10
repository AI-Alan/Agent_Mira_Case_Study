import axios from 'axios';

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({ baseURL: API_BASE });

export const sendMessage = (data: { 
  message?: string; 
  filters?: { location?: string; budget?: string; bedrooms?: string } 
}) => 
  api.post('/chat/message', data);

export const getProperties = (params: { location?: string; budget?: string; bedrooms?: string }) => 
  api.get('/properties', { params });

export const saveProperty = (data: { user_id: string; property_id: string }) => 
  api.post('/user/save', data);

