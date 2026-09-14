export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-cream/30 border-t border-gray-200 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Brand and tagline */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-7 h-7 flex items-center justify-center text-light-blue">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                className="w-5 h-5"
              >
                <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span className="font-serif text-xl font-semibold text-gray-900">
              ResearchMate <span className="text-lavender">AI</span>
            </span>
          </div>
          <p className="text-sm text-gray-600">
            From Papers to Possibilities
          </p>
        </div>

        {/* Navigation links */}
        <nav className="flex flex-wrap justify-center items-center gap-4 sm:gap-6 mb-6 text-sm">
          <a
            href="#features"
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            Features
          </a>
          <span className="text-gray-300">·</span>
          <a
            href="#how-it-works"
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            How It Works
          </a>
          <span className="text-gray-300">·</span>
          <a
            href="#about"
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            About
          </a>
          <span className="text-gray-300">·</span>
          <a
            href="https://github.com"
            className="text-gray-600 hover:text-gray-900 transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </nav>

        {/* Copyright and disclaimer */}
        <div className="text-center space-y-2">
          <p className="text-sm text-gray-600">
            © {currentYear} ResearchMate AI
          </p>
          <p className="text-xs text-gray-500 italic max-w-2xl mx-auto">
            AI-generated suggestions should be verified against the original literature.
          </p>
        </div>
      </div>
    </footer>
  );
}
