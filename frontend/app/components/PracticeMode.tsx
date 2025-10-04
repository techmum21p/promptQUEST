'use client'

export function PracticeMode() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Practice Mode</h1>
        <p className="text-gray-600">Choose your difficulty level and start practicing!</p>
      </div>

      {/* Coming Soon */}
      <div className="max-w-md mx-auto">
        <div className="card text-center">
          <div className="mx-auto h-20 w-20 bg-warning-100 rounded-full flex items-center justify-center mb-6">
            <span className="text-warning-600 text-4xl">🚧</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Practice Mode
          </h2>
          <p className="text-gray-600 mb-6">
            Practice mode components are being developed. This will include scenario selection, 
            prompt writing interface, and AI-powered evaluation feedback.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Features Coming:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Scenario difficulty selection</li>
              <li>• Interactive prompt writing</li>
              <li>• Real-time AI evaluation</li>
              <li>• Detailed feedback and scores</li>
              <li>• Progress tracking</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
