import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import { store } from './store/store';
import { useAppSelector, useAppDispatch } from './hooks/redux';
import { loadUserFromStorage } from './store/authSlice';
import Navbar from './components/Layout/Navbar';
import ErrorBoundary from './shared/ui/ErrorBoundary';
import LoadingSpinner from './shared/ui/LoadingSpinner';
import './App.css';

const Home = lazy(() => import('./features/home').then(m => ({ default: m.Home })));
const Dashboard = lazy(() => import('./features/dashboard').then(m => ({ default: m.Dashboard })));
const Login = lazy(() => import('./features/auth').then(m => ({ default: m.Login })));
const Register = lazy(() => import('./features/auth').then(m => ({ default: m.Register })));
const StockSearch = lazy(() => import('./features/stocks').then(m => ({ default: m.StockSearch })));
const StockDetails = lazy(() => import('./features/stocks').then(m => ({ default: m.StockDetails })));
const IndianStockExplorer = lazy(() => import('./features/stocks').then(m => ({ default: m.IndianStockExplorer })));
const Portfolio = lazy(() => import('./features/portfolio').then(m => ({ default: m.Portfolio })));
const PortfolioOptimizer = lazy(() => import('./features/portfolio').then(m => ({ default: m.PortfolioOptimizer })));
const ManagePortfolio = lazy(() => import('./features/portfolio').then(m => ({ default: m.ManagePortfolio })));
const PortfolioHoldings = lazy(() => import('./features/portfolio').then(m => ({ default: m.PortfolioHoldings })));
const ChatBot = lazy(() => import('./features/chat').then(m => ({ default: m.ChatBot })));
const Screener = lazy(() => import('./features/screener').then(m => ({ default: m.Screener })));
const Profile = lazy(() => import('./features/profile').then(m => ({ default: m.Profile })));
const InvestmentProfileOnboarding = lazy(() => import('./features/profile').then(m => ({ default: m.InvestmentProfileOnboarding })));
const Watchlist = lazy(() => import('./features/watchlist').then(m => ({ default: m.Watchlist })));

const LegacyStockRedirect: React.FC = () => {
  const { symbol } = useParams();
  return <Navigate to={`/stocks/${symbol}`} replace />;
};

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const AppContent: React.FC = () => {
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  React.useEffect(() => {
    dispatch(loadUserFromStorage());
    
    // Fetch CSRF token on startup to initialize the csrf_token cookie
    const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
    fetch(`${apiBaseUrl}/auth/csrf-token`)
      .catch((err) => console.error('Failed to initialize CSRF token:', err));
  }, [dispatch]);

  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className={'pt-16'}>
          <ErrorBoundary>
          <Suspense fallback={<LoadingSpinner fullScreen />}>
          <Routes>
            <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
            <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/stocks" element={<ProtectedRoute><StockSearch /></ProtectedRoute>} />
            <Route path="/stocks/:symbol" element={<ProtectedRoute><StockDetails /></ProtectedRoute>} />
            <Route path="/stock/:symbol" element={<LegacyStockRedirect />} />
            <Route path="/portfolio" element={<ProtectedRoute><Portfolio /></ProtectedRoute>} />
            <Route path="/portfolio/manage" element={<ProtectedRoute><ManagePortfolio /></ProtectedRoute>} />
            <Route path="/portfolio/holdings" element={<ProtectedRoute><PortfolioHoldings /></ProtectedRoute>} />
            <Route path="/watchlist" element={<ProtectedRoute><Watchlist /></ProtectedRoute>} />
            <Route path="/optimizer" element={<ProtectedRoute><PortfolioOptimizer /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute><ChatBot /></ProtectedRoute>} />
            <Route path="/indian-stocks" element={<ProtectedRoute><IndianStockExplorer /></ProtectedRoute>} />
            <Route path="/profile-setup" element={<ProtectedRoute><InvestmentProfileOnboarding /></ProtectedRoute>} />
            <Route path="/screener" element={<ProtectedRoute><Screener /></ProtectedRoute>} />
            <Route path="/" element={<Home />} />
          </Routes>
          </Suspense>
          </ErrorBoundary>
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
