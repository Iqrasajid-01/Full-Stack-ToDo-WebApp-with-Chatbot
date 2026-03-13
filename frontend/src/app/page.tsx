'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useTheme } from '@/contexts/theme-context';

export default function HomePage() {
  const { theme } = useTheme();
  const [isMounted, setIsMounted] = useState(false);

  // Check if user is authenticated and redirect to dashboard
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      window.location.href = '/dashboard';
    }

    // Trigger animation after mount
    setIsMounted(true);
  }, []);

  return (
    <div className={`min-h-screen flex flex-col items-center transition-colors duration-500 ${
      theme === 'dark'
        ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white'
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 text-gray-900'
    }`}>
      {/* Navigation */}
      <nav className="w-full py-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="h-10 w-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">
              TaskFlow
            </span>
          </div>
          <div className="hidden md:flex space-x-8">
            
          </div>
          <div className="flex items-center space-x-4">
            <Link
              href="/signin"
              className="text-sm font-medium hover:text-indigo-600 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="py-2 px-4 text-sm font-medium rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 transition-all duration-300"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl w-full px-4 sm:px-6 lg:px-8 py-16 md:py-24 flex-grow">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div className={`transition-all duration-700 ${isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-5'}`}>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
              Streamline Your <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">Tasks</span>, Amplify Your Productivity
            </h1>
            <p className="mt-6 text-lg md:text-xl opacity-80 max-w-lg">
              A powerful and intuitive todo app designed to boost your productivity.
              Organize your tasks, set priorities, and achieve your goals with ease.
            </p>
            <div className={`mt-10 space-y-5 transition-all duration-700 delay-150 ${isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/signup"
                  className="group relative flex items-center justify-center py-3 px-6 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 hover:scale-105 active:scale-95"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  Get Started Free
                </Link>
                <Link
                  href="/signin"
                  className="group relative flex items-center justify-center py-3 px-6 border border-gray-300 text-base font-medium rounded-xl text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow hover:shadow-md transition-all duration-300 dark:bg-gray-700 dark:text-white dark:border-gray-600 dark:hover:bg-gray-600 transform hover:scale-105 active:scale-95"
                >
                  Sign In to Your Account
                </Link>
              </div>
            </div>
          </div>
          <div className={`transition-all duration-700 delay-300 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 p-6 shadow-xl">
              {/* Mockup of TaskFlow App Interface */}
              <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg overflow-hidden w-full h-auto max-w-md mx-auto border border-gray-200 dark:border-gray-700">
                {/* App Header/Mock Browser */}
                <div className="bg-gray-100 dark:bg-gray-800 px-4 py-2 flex items-center space-x-2 border-b border-gray-200 dark:border-gray-700">
                  <div className="w-3 h-3 rounded-full bg-red-400"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                  <div className="w-3 h-3 rounded-full bg-green-400"></div>
                  <div className="flex-1 text-center text-xs text-gray-500 dark:text-gray-400 font-medium">
                    TaskFlow Dashboard
                  </div>
                </div>
                
                {/* App Content */}
                <div className="p-4">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-semibold text-gray-800 dark:text-white">Today's Tasks</h3>
                    <button className="text-indigo-600 dark:text-indigo-400 text-sm font-medium">+ Add</button>
                  </div>
                  
                  {/* Sample Tasks */}
                  <div className="space-y-3">
                    <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <input type="checkbox" className="h-4 w-4 text-indigo-600 rounded focus:ring-indigo-500" />
                      <span className="ml-3 text-gray-700 dark:text-gray-300 text-sm">Complete project proposal</span>
                      <span className="ml-auto bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 text-xs px-2 py-1 rounded-full">High</span>
                    </div>
                    
                    <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <input type="checkbox" className="h-4 w-4 text-indigo-600 rounded focus:ring-indigo-500" />
                      <span className="ml-3 text-gray-700 dark:text-gray-300 text-sm">Schedule team meeting</span>
                      <span className="ml-auto bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 text-xs px-2 py-1 rounded-full">Medium</span>
                    </div>
                    
                    <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <input type="checkbox" className="h-4 w-4 text-indigo-600 rounded focus:ring-indigo-500" />
                      <span className="ml-3 text-gray-700 dark:text-gray-300 text-sm">Review documentation</span>
                      <span className="ml-auto bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 text-xs px-2 py-1 rounded-full">Low</span>
                    </div>
                  </div>
                  
                  {/* Stats Section */}
                  <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-800">
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="bg-indigo-50 dark:bg-indigo-900/20 p-2 rounded">
                        <div className="text-xs text-indigo-600 dark:text-indigo-400">Pending</div>
                        <div className="text-lg font-bold text-gray-800 dark:text-white">12</div>
                      </div>
                      <div className="bg-green-50 dark:bg-green-900/20 p-2 rounded">
                        <div className="text-xs text-green-600 dark:text-green-400">Completed</div>
                        <div className="text-lg font-bold text-gray-800 dark:text-white">24</div>
                      </div>
                      <div className="bg-purple-50 dark:bg-purple-900/20 p-2 rounded">
                        <div className="text-xs text-purple-600 dark:text-purple-400">Overdue</div>
                        <div className="text-lg font-bold text-gray-800 dark:text-white">3</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="w-full py-16 bg-white/5 dark:bg-black/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">Powerful Features for Maximum Productivity</h2>
            <p className="mt-4 text-lg opacity-80 max-w-2xl mx-auto">
              Everything you need to organize your tasks and boost your efficiency
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature Card 1 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 p-8 hover:scale-[1.02] transition-all duration-300 group">
              <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="mt-6 text-xl font-semibold">Task Management</h3>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Create, organize, and prioritize your tasks with our intuitive interface. Set due dates, categories, and reminders to stay on track.
              </p>
            </div>

            {/* Feature Card 2 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 p-8 hover:scale-[1.02] transition-all duration-300 group">
              <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="mt-6 text-xl font-semibold">Secure Authentication</h3>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Protect your data with industry-standard security measures. Secure login and encrypted storage keep your information safe.
              </p>
            </div>

            {/* Feature Card 3 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 p-8 hover:scale-[1.02] transition-all duration-300 group">
              <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </div>
              <h3 className="mt-6 text-xl font-semibold">Smart Organization</h3>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Categorize tasks by projects, priority levels, and custom tags. Visualize your workflow with Kanban boards and calendars.
              </p>
            </div>

            {/* Feature Card 4 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 p-8 hover:scale-[1.02] transition-all duration-300 group">
              <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="mt-6 text-xl font-semibold">Reminders & Notifications</h3>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Never miss a deadline with customizable reminders and notifications. Get alerts via email or push notifications.
              </p>
            </div>

            {/* Feature Card 5 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 p-8 hover:scale-[1.02] transition-all duration-300 group">
              <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="mt-6 text-xl font-semibold">Cross-Platform Sync</h3>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Access your tasks from anywhere. Seamless synchronization across all your devices - web, mobile, and desktop.
              </p>
            </div>

            {/* Feature Card 6 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 p-8 hover:scale-[1.02] transition-all duration-300 group">
              <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="mt-6 text-xl font-semibold">Analytics & Insights</h3>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Track your productivity with detailed analytics. Understand your habits and improve your efficiency over time.
              </p>
            </div>
          </div>
        </div>
      </div>


      {/* Simple, Secure, Powerful Section */}
      <div className="w-full py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`grid grid-cols-1 md:grid-cols-3 gap-8 text-center transition-all duration-700 delay-300 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
            <div className="p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 hover:scale-105 transition-transform">
              <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">Simple</div>
              <div className="mt-2 text-lg font-medium">Easy to use</div>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Intuitive interface designed for everyone. No learning curve needed.
              </p>
            </div>
            <div className="p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 hover:scale-105 transition-transform">
              <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">Secure</div>
              <div className="mt-2 text-lg font-medium">Privacy focused</div>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Military-grade encryption keeps your data safe and private.
              </p>
            </div>
            <div className="p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 dark:bg-gray-800/30 dark:border-gray-700/50 hover:scale-105 transition-transform">
              <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">Powerful</div>
              <div className="mt-2 text-lg font-medium">Feature rich</div>
              <p className="mt-3 text-gray-600 dark:text-gray-300">
                Advanced features to supercharge your productivity.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className={`w-full py-12 bg-white/5 dark:bg-black/10 transition-opacity duration-500 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="mt-12 pt-8 border-t border-gray-700/30 text-center text-sm opacity-75">
            © {new Date().getFullYear()} TaskFlow. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}