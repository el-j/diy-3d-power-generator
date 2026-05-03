import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './src/App';
import './src/app.css';

const rootEl = document.getElementById('root');
if (!rootEl) {
  throw new Error('Missing root element');
}

createRoot(rootEl).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
