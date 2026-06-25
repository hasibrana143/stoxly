import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import { store } from './store/store';
import { useAppSelector, useAppDispatch } from './hooks/redux';
import { loadUserFromStorage } from './store/authSlice';
import Home from './pages/Home';
import Navbar from './components/Layout/Navbar';
import Dashboard from './pages/Dashboard';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import StockSearch from './pages/StockSearch';
import StockDetails from './pages/StockDetails';
import Portfolio from './pages/Portfolio';
import PortfolioOptimizer from './pages/PortfolioOptimizer';
import ChatBot from './pages/ChatBot';
import IndianStockExplorer from './pages/IndianStockExplorer';
import InvestmentProfileOnboarding from './pages/InvestmentProfileOnboarding';
import Screener from './pages/Screener';
import Profile from './pages/Profile';
import ManagePortfolio from './pages/ManagePortfolio';
import PortfolioHoldings from './pages/PortfolioHoldings';
import Watchlist from './pages/Watchlist';
import './App.css';

const LegacyStockRedirect: React.FC = () => {
  const { symbol } = useParams();
  return <Navigate to={`/stocks/${symbol}`} replace />;
};

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

// Main App Component
const AppContent: React.FC = () => {
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  React.useEffect(() => {
    dispatch(loadUserFromStorage());
  }, [dispatch]);

  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className={'pt-16'}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
            <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />

            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
            <Route path="/stocks" element={
              <ProtectedRoute>
                <StockSearch />
              </ProtectedRoute>
            } />
            <Route path="/stocks/:symbol" element={
              <ProtectedRoute>
                <StockDetails />
              </ProtectedRoute>
            } />
            <Route path="/stock/:symbol" element={<LegacyStockRedirect />} />
            <Route path="/portfolio" element={
              <ProtectedRoute>
                <Portfolio />
              </ProtectedRoute>
            } />
            <Route path="/portfolio/manage" element={
              <ProtectedRoute>
                <ManagePortfolio />
              </ProtectedRoute>
            } />
            <Route path="/portfolio/holdings" element={
              <ProtectedRoute>
                <PortfolioHoldings />
              </ProtectedRoute>
            } />
            <Route path="/watchlist" element={
              <ProtectedRoute>
                <Watchlist />
              </ProtectedRoute>
            } />
            <Route path="/optimizer" element={
              <ProtectedRoute>
                <PortfolioOptimizer />
              </ProtectedRoute>
            } />
            <Route path="/chat" element={
              <ProtectedRoute>
                <ChatBot />
              </ProtectedRoute>
            } />
            <Route path="/indian-stocks" element={
              <ProtectedRoute>
                <IndianStockExplorer />
              </ProtectedRoute>
            } />
            <Route path="/profile-setup" element={
              <ProtectedRoute>
                <InvestmentProfileOnboarding />
              </ProtectedRoute>
            } />
            <Route path="/screener" element={
              <ProtectedRoute>
                <Screener />
              </ProtectedRoute>
            } />

            {/* Default Route */}
            <Route path="/" element={<Home />} />
          </Routes>
        </main>
        <Toaster position="top-right" />
      </div>
    </BrowserRouter>
  );
};

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
};

export default App;
