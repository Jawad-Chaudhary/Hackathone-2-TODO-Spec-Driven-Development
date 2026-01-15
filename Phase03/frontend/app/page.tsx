import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-float-slow" />
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-float-delayed" />
        <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-float" />
      </div>

      <div className="max-w-4xl w-full relative z-10">
        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 md:p-12 border border-white/20">
          {/* Header */}
          <div className="text-center mb-10 animate-fade-in-up">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mb-6 shadow-xl transform hover:scale-105 transition-transform duration-300 hover:rotate-3">
              <span className="text-5xl text-white font-bold">AI</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-4 leading-tight">
              AI Todo Chatbot
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Your intelligent task management assistant powered by AI
            </p>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-2 gap-4 mb-10">
            <div className="group flex items-start gap-4 p-5 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200/50 hover:border-green-300 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl flex items-center justify-center text-2xl shadow-md group-hover:scale-110 transition-transform duration-300">
                ➕
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1 text-lg">Add Tasks</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Create tasks with natural language instantly
                </p>
              </div>
            </div>

            <div className="group flex items-start gap-4 p-5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200/50 hover:border-blue-300 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-xl flex items-center justify-center text-2xl shadow-md group-hover:scale-110 transition-transform duration-300">
                📋
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1 text-lg">List Tasks</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  View and filter your tasks with ease
                </p>
              </div>
            </div>

            <div className="group flex items-start gap-4 p-5 bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl border border-orange-200/50 hover:border-orange-300 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-orange-400 to-amber-500 rounded-xl flex items-center justify-center text-2xl shadow-md group-hover:scale-110 transition-transform duration-300">
                ✏️
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1 text-lg">Update Tasks</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Modify and refine tasks on the fly
                </p>
              </div>
            </div>

            <div className="group flex items-start gap-4 p-5 bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl border border-purple-200/50 hover:border-purple-300 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-purple-400 to-violet-500 rounded-xl flex items-center justify-center text-2xl shadow-md group-hover:scale-110 transition-transform duration-300">
                ✅
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1 text-lg">Complete Tasks</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Mark tasks as done with a simple message
                </p>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="text-center animate-fade-in-up flex flex-col gap-4" style={{ animationDelay: '0.5s' }}>
            <div className="flex items-center justify-center gap-4">
              <Link
                href="/signin"
                className="group inline-flex items-center gap-3 px-8 py-4 bg-white text-blue-600 font-semibold text-lg rounded-xl hover:shadow-xl active:scale-95 shadow-lg transform hover:-translate-y-1 transition-all duration-300 border-2 border-blue-600"
              >
                <span className="relative z-10">Sign In</span>
              </Link>
              <Link
                href="/signup"
                className="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white font-semibold text-lg rounded-xl hover:shadow-2xl active:scale-95 shadow-xl transform hover:-translate-y-1 transition-all duration-300 relative overflow-hidden"
              >
                <span className="relative z-10">Get Started</span>
                <span className="relative z-10 text-2xl group-hover:translate-x-1 transition-transform duration-300">→</span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-700 via-indigo-700 to-purple-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </Link>
            </div>
            <p className="mt-2 text-sm text-gray-500">
              Create an account to start managing your tasks
            </p>
          </div>

          {/* Footer info */}
          <div className="mt-10 pt-8 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-500">
              Backend API:{' '}
              <a
                href={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 font-medium hover:underline transition-colors"
              >
                {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
              </a>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
