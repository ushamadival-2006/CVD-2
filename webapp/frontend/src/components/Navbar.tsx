import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Activity, LogOut, User, History, PlusCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();

  const handleLogout = () => { logout(); navigate('/login'); };
  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to={isAuthenticated ? '/dashboard' : '/'} className="flex items-center gap-2">
            <div className="bg-blue-600 text-white p-1.5 rounded-lg">
              <Activity size={20} />
            </div>
            <span className="font-bold text-gray-900 text-lg">CVD<span className="text-blue-600">Risk</span></span>
          </Link>

          {/* Nav Links */}
          {isAuthenticated ? (
            <div className="flex items-center gap-1">
              <Link to="/dashboard"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors
                  ${isActive('/dashboard') ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}`}>
                Dashboard
              </Link>
              <Link to="/assessment"
                className={`flex items-center gap-1 px-3 py-2 rounded-md text-sm font-medium transition-colors
                  ${isActive('/assessment') ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}`}>
                <PlusCircle size={16} /> New Assessment
              </Link>
              <Link to="/history"
                className={`flex items-center gap-1 px-3 py-2 rounded-md text-sm font-medium transition-colors
                  ${isActive('/history') ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}`}>
                <History size={16} /> History
              </Link>
              <div className="flex items-center gap-2 ml-4 pl-4 border-l border-gray-200">
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <User size={16} className="text-blue-600" />
                  </div>
                  <span className="hidden sm:block font-medium">{user?.name}</span>
                </div>
                <button onClick={handleLogout}
                  className="flex items-center gap-1 text-gray-500 hover:text-red-600 transition-colors px-2 py-1 rounded">
                  <LogOut size={16} />
                  <span className="hidden sm:block text-sm">Logout</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-gray-900">Login</Link>
              <Link to="/signup" className="text-sm font-medium bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
