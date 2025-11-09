import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { CalendarProvider } from './context/CalendarContext';
import './index.css';
import '../assets/css/fontawesome-all.min.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <CalendarProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </CalendarProvider>
  </React.StrictMode>
);