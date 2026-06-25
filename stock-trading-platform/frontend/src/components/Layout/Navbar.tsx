import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ChartBarIcon, HomeIcon, ChartPieIcon, UserCircleIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import AiChatModal from './AiChatModal';
import { useAppSelector, useAppDispatch } from '../../hooks/redux';
import { logout } from '../../store/authSlice';

const Navbar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);
  const [aiOpen, setAiOpen] = React.useState(false);
  const [dropdownOpen, setDropdownOpen] = React.useState(false);
  const [query, setQuery] = React.useState('');

  const navItems = [
    { name: 'Home', path: '/', icon: HomeIcon },
    { name: 'Screens', path: '/screener', icon: ChartBarIcon },
    { name: 'Portfolio', path: '/portfolio', icon: ChartPieIcon },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <>
      <nav className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-primary-600" />
                <span className="ml-2 text-2xl font-bold text-gray-900">stoxly</span>
                <span className="ml-1 text-2xl font-bold text-green-600">.ai</span>
              </Link>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-6">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.path}
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${isActive(item.path)
                      ? 'text-primary-700 bg-primary-50'
                      : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50'
                      }`}
                  >
                    <Icon className="h-5 w-5 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </div>

            {/* Search */}
            <div className="hidden lg:flex flex-1 mx-6 max-w-md">
              <input
                id="navbar-stock-search"
                name="stock_search"
                type="search"
                placeholder="Search for a company"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={async (e) => {
                  if (e.key === 'Enter' && query.trim().length > 0) {
                    try {
                      const resp = await fetch(`http://localhost:8000/api/stocks/search/${encodeURIComponent(query.trim())}`);
                      if (resp.ok) {
                        const data = await resp.json();
                        const first = data.stocks && data.stocks[0];
                        if (first?.symbol) {
                          navigate(`/stocks/${first.symbol}?tab=overview`);
                          setQuery('');
                        }
                      }
                    } catch { }
                  }
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <div className="relative">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900 focus:outline-none"
                  >
                    <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700">
                      <UserCircleIcon className="h-6 w-6" />
                    </div>
                    <span className="hidden md:block">{user?.username || 'User'}</span>
                    <ChevronDownIcon className="h-4 w-4 text-gray-500" />
                  </button>

                  {/* Dropdown Menu */}
                  {dropdownOpen && (
                    <>
                      <div
                        className="fixed inset-0 z-10"
                        onClick={() => setDropdownOpen(false)}
                      />
                      <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5 z-20">
                        <div className="px-4 py-2 border-b">
                          <p className="text-sm text-gray-900 font-medium">{user?.username}</p>
                          <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                        </div>
                        <Link
                          to="/profile"
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setDropdownOpen(false)}
                        >
                          Your Profile
                        </Link>
                        <Link
                          to="/profile-setup"
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setDropdownOpen(false)}
                        >
                          Investment Settings
                        </Link>
                        <button
                          onClick={() => {
                            setDropdownOpen(false);
                            dispatch(logout());
                            navigate('/login');
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                        >
                          Sign out
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="btn-primary text-sm"
                  >
                    Get Free Account
                  </Link>
                </>
              )}
              <button
                onClick={() => setAiOpen(true)}
                className="px-3 py-2 rounded-md text-sm font-semibold bg-primary-600 text-white hover:bg-primary-700"
              >
                AI
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-50 border-t">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ${isActive(item.path)
                    ? 'text-primary-700 bg-primary-50'
                    : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50'
                    }`}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
      <AiChatModal open={aiOpen} onClose={() => setAiOpen(false)} />
    </>
  );
};

export default Navbar;
