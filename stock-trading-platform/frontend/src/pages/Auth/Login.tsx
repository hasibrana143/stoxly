import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAppDispatch } from '../../hooks/redux';
import { useLoginMutation } from '../../services/api';
import { loginSuccess } from '../../store/authSlice';
import toast from 'react-hot-toast';
import {
  EnvelopeIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [login, { isLoading }] = useLoginMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const result = await login({ email, password }).unwrap();
      dispatch(loginSuccess({
        user: result.user,
        token: result.access_token
      }));
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.data?.detail || 'Login failed');
    }
  };

  const handleSocialLogin = (provider: string) => {
    console.log(`Initiating ${provider} login...`);
    toast.success(`${provider} login initiated`);
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-[#E8E5FF] to-[#F0F4FF] p-4 font-sans">
      <div className="bg-white rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.1)] overflow-hidden w-full max-w-5xl flex flex-col lg:flex-row min-h-[700px] transition-all duration-300">

        {/* LEFT: Form Section */}
        <div className="w-full lg:w-1/2 p-8 sm:p-12 flex flex-col justify-center relative z-10 bg-white">
          <div className="mb-8">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-2 tracking-tight">Hello!</h1>
            <p className="text-gray-500 text-lg">Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <EnvelopeIcon className="h-6 w-6 text-gray-400 group-focus-within:text-[#7C3AED] transition-colors duration-300" />
              </div>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="block w-full pl-12 pr-4 py-3.5 border-0 bg-gray-50 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/20 focus:bg-white shadow-sm transition-all duration-300"
                placeholder="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            {/* Password Field */}
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <LockClosedIcon className="h-6 w-6 text-gray-400 group-focus-within:text-[#7C3AED] transition-colors duration-300" />
              </div>
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                required
                className="block w-full pl-12 pr-12 py-3.5 border-0 bg-gray-50 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/20 focus:bg-white shadow-sm transition-all duration-300"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-4 flex items-center cursor-pointer"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeSlashIcon className="h-6 w-6 text-gray-400 hover:text-[#7C3AED] transition-colors" />
                ) : (
                  <EyeIcon className="h-6 w-6 text-gray-400 hover:text-[#7C3AED] transition-colors" />
                )}
              </button>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between text-sm px-1">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-[#7C3AED] focus:ring-[#7C3AED] border-gray-300 rounded cursor-pointer"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <label htmlFor="remember-me" className="ml-2 block text-gray-600 cursor-pointer select-none">
                  Remember me
                </label>
              </div>
              <div className="text-sm">
<button type="button" className="font-semibold text-[#7C3AED] hover:text-[#6D28D9] transition-colors bg-transparent border-none cursor-pointer p-0">
                  Forgot password?
                </button>
              </div>
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-3.5 px-4 border border-transparent rounded-full shadow-[0_10px_20px_rgba(124,58,237,0.3)] text-base font-bold text-white bg-gradient-to-r from-[#8B5CF6] to-[#7C3AED] hover:shadow-[0_15px_25px_rgba(124,58,237,0.4)] hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-[#7C3AED]/30 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed transform"
            >
              {isLoading ? (
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : 'SIGN IN'}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500 font-medium">OR</span>
            </div>
          </div>

          {/* Social Login Buttons */}
          <div className="grid grid-cols-4 gap-3">
            {/* Google */}
            <button
              onClick={() => handleSocialLogin('Google')}
              className="flex items-center justify-center h-12 border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 group"
              aria-label="Sign in with Google"
            >
              <svg className="h-6 w-6" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
              </svg>
            </button>

            {/* Facebook */}
            <button
              onClick={() => handleSocialLogin('Facebook')}
              className="flex items-center justify-center h-12 border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-[#1877F2] transition-all duration-200 group"
              aria-label="Sign in with Facebook"
            >
              <svg className="h-6 w-6 text-[#1877F2]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036c-2.048 0-2.606.498-2.606 1.693v2.278h3.922l-.566 3.667h-3.356v7.98h-5.208Z" />
              </svg>
            </button>

            {/* Apple */}
            <button
              onClick={() => handleSocialLogin('Apple')}
              className="flex items-center justify-center h-12 border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-black transition-all duration-200 group"
              aria-label="Sign in with Apple"
            >
              <svg className="h-6 w-6 text-black" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.127 3.675-.552 9.127 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701" />
              </svg>
            </button>

            {/* Microsoft */}
            <button
              onClick={() => handleSocialLogin('Microsoft')}
              className="flex items-center justify-center h-12 border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-[#F25022] transition-all duration-200 group"
              aria-label="Sign in with Microsoft"
            >
              <svg className="h-6 w-6" viewBox="0 0 23 23">
                <path fill="#f25022" d="M1 1h10v10H1z" />
                <path fill="#00a4ef" d="M1 12h10v10H1z" />
                <path fill="#7fba00" d="M12 1h10v10H12z" />
                <path fill="#ffb900" d="M12 12h10v10H12z" />
              </svg>
            </button>
          </div>

          <div className="mt-8 text-center">
            <p className="text-gray-600">
              Don't have an account?{' '}
              <Link to="/register" className="font-bold text-[#7C3AED] hover:text-[#6D28D9] transition-colors">
                Create
              </Link>
            </p>
          </div>
        </div>

        {/* RIGHT: Visual Section */}
        <div className="hidden lg:block w-1/2 relative bg-gradient-to-br from-[#8B5CF6] to-[#6D28D9] overflow-hidden">
          {/* Decorative Circles/Blobs */}
          <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 rounded-full bg-[#A78BFA] opacity-20 blur-3xl"></div>
          <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 rounded-full bg-[#7C3AED] opacity-30 blur-3xl"></div>

          {/* Wave Graphics */}
          <div className="absolute inset-0 z-0">
            {/* Top Right Wave */}
            <svg className="absolute top-0 right-0 w-full h-full opacity-10" viewBox="0 0 100 100" preserveAspectRatio="none">
              <path d="M0 0 L100 0 L100 100 Q50 50 0 0 Z" fill="white" />
            </svg>

            {/* Bottom Flowing Waves */}
            <svg className="absolute bottom-0 left-0 w-full" viewBox="0 0 1440 320" preserveAspectRatio="none">
              <path fill="#ffffff" fillOpacity="0.1" d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,224C672,245,768,267,864,261.3C960,256,1056,224,1152,197.3C1248,171,1344,149,1392,138.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
              <path fill="#ffffff" fillOpacity="0.15" d="M0,256L48,245.3C96,235,192,213,288,192C384,171,480,149,576,160C672,171,768,213,864,229.3C960,245,1056,235,1152,213.3C1248,192,1344,160,1392,144L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
            </svg>
          </div>

          <div className="relative z-10 h-full flex flex-col justify-center items-center text-white p-16 text-center">
            <h2 className="text-5xl font-extrabold mb-6 tracking-tight drop-shadow-lg">Welcome Back!</h2>
            <p className="text-lg text-purple-100 max-w-md mx-auto leading-relaxed font-medium">
              Access your personalized dashboard and stay ahead of the market trends with our AI-powered tools.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
