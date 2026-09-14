"use client";

export default function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Upload Papers",
      description: "Add 2–5 research papers.",
      icon: (
        <svg
          className="w-10 h-10"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
      ),
    },
    {
      number: "02",
      title: "Analyze & Ask",
      description: "Get grounded answers from your papers.",
      icon: (
        <svg
          className="w-10 h-10"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      ),
    },
    {
      number: "03",
      title: "Compare",
      description:
        "View methods, datasets, results, and limitations side by side.",
      icon: (
        <svg
          className="w-10 h-10"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
    },
    {
      number: "04",
      title: "Discover Gaps",
      description: "Get AI-suggested research gaps and contradictions.",
      icon: (
        <svg
          className="w-10 h-10"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
      ),
    },
  ];

  return (
    <section id="how-it-works" className="py-20 px-4 sm:px-6 lg:px-8 bg-cream/30">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="font-serif text-4xl sm:text-5xl mb-4 text-gray-900">
            HOW IT WORKS
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            From scattered papers to structured insights in four simple steps
          </p>
        </div>

        {/* Desktop: Horizontal Layout */}
        <div className="hidden md:flex items-start justify-between gap-8">
          {steps.map((step, index) => (
            <div key={index} className="flex flex-col items-center flex-1">
              {/* Circle with number */}
              <div className="relative mb-6">
                <div className="w-20 h-20 rounded-full bg-light-blue/20 flex items-center justify-center border-2 border-light-blue/40">
                  <span className="font-serif text-2xl font-bold text-light-blue">
                    {step.number}
                  </span>
                </div>
                {/* Arrow (except for last item) */}
                {index < steps.length - 1 && (
                  <svg
                    className="absolute top-1/2 -right-12 transform -translate-y-1/2 w-8 h-8 text-gray-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                )}
              </div>

              {/* Icon */}
              <div className="w-16 h-16 rounded-lg bg-gray-100 flex items-center justify-center mb-4 text-gray-600">
                {step.icon}
              </div>

              {/* Content */}
              <h3 className="font-serif text-xl mb-2 text-gray-900 text-center">
                {step.title}
              </h3>
              <p className="text-sm text-gray-600 text-center leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>

        {/* Mobile: Vertical Layout */}
        <div className="md:hidden space-y-8">
          {steps.map((step, index) => (
            <div key={index} className="flex gap-6">
              {/* Left side - Number and line */}
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 rounded-full bg-light-blue/20 flex items-center justify-center border-2 border-light-blue/40">
                  <span className="font-serif text-xl font-bold text-light-blue">
                    {step.number}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div className="w-0.5 h-full bg-gray-200 mt-4"></div>
                )}
              </div>

              {/* Right side - Content */}
              <div className="flex-1 pb-8">
                <div className="w-14 h-14 rounded-lg bg-gray-100 flex items-center justify-center mb-4 text-gray-600">
                  {step.icon}
                </div>
                <h3 className="font-serif text-xl mb-2 text-gray-900">
                  {step.title}
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
