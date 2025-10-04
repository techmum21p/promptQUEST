'use client'

export function Dashboard() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Ready to practice your prompt engineering skills?</p>
      </div>

      {/* Quick Start Guide */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="text-center">
            <div className="mx-auto h-16 w-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-primary-600 text-2xl">🎯</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">1️⃣ Choose Level</h3>
            <p className="text-gray-600 text-sm">
              Select your skill level: Beginner, Intermediate, or Advanced
            </p>
          </div>
        </div>

        <div className="card">
          <div className="text-center">
            <div className="mx-auto h-16 w-16 bg-success-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-success-600 text-2xl">✍️</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">2️⃣ Write Prompt</h3>
            <p className="text-gray-600 text-sm">
              Craft a prompt for the given Microsoft 365 Copilot scenario
            </p>
          </div>
        </div>

        <div className="card">
          <div className="text-center">
            <div className="mx-auto h-16 w-16 bg-warning-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-warning-600 text-2xl">🤖</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">3️⃣ Get Feedback</h3>
            <p className="text-gray-600 text-sm">
              Receive AI-powered evaluation and improve your skills
            </p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary-600 mb-2">0</div>
            <div className="text-sm text-gray-600 uppercase tracking-wide">Total Attempts</div>
          </div>
        </div>

        <div className="card">
          <div className="text-center">
            <div className="text-3xl font-bold text-success-600 mb-2">0%</div>
            <div className="text-sm text-gray-600 uppercase tracking-wide">Average Score</div>
          </div>
        </div>

        <div className="card">
          <div className="text-center">
            <div className="text-3xl font-bold text-warning-600 mb-2">0</div>
            <div className="text-sm text-gray-600 uppercase tracking-wide">Badges Earned</div>
          </div>
        </div>

        <div className="card">
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">Beginner</div>
            <div className="text-sm text-gray-600 uppercase tracking-wide">Skill Level</div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="mt-8 text-center">
        <div className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 transition-colors duration-200">
          <span className="mr-2">🚀</span>
          Start Practicing Now
        </div>
        <p className="mt-2 text-sm text-gray-600">
          Navigate to Practice Mode to begin your prompt engineering journey!
        </p>
      </div>
    </div>
  )
}
