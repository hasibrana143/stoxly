import React from 'react';
import ReactDOM from 'react-dom/client';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

const render = () => {
  const App = React.lazy(() => import('./App'));
  root.render(
    <React.StrictMode>
      <React.Suspense fallback={<div className="flex h-screen items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" /></div>}>
        <App />
      </React.Suspense>
    </React.StrictMode>
  );
};

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js');
  });
}

render();
