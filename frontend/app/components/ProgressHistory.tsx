'use client'

export function ProgressHistory() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Progress History</h1>
        <p className="text-gray-600">Track your improvement over time</p>
      </div>

      {/* Coming Soon */}
      <div className="max-w-md mx-auto">
        <div className="card text-center">
          <div className="mx-auto h-20 w-20 bg-warning-100 rounded-full flex items-center justify-center mb-6">
            <span className="text-warning-600 text-4xl">📈</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Progress History
          </h2>
          <p className="text-gray-600 mb-6">
            Progress history components are being developed. This will show detailed 
            analytics, graphs, and improvement tracking.
          </p>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h3 className="font-semibold text-purple-900 mb-2">Features Coming:</h3>
            <ul className="text-sm text-purple-800 space-y-1">
              <li>• Detailed attempt history</li>
              <li>• Score trend analysis</li>
              <li>• Skill progression charts</li>
              <li>• Badge achievement timeline</li>
              <li>• Performance insights</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
