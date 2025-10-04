'use client'

export function Leaderboard() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Leaderboard</h1>
        <p className="text-gray-600">See how you rank against other players!</p>
      </div>

      {/* Coming Soon */}
      <div className="max-w-md mx-auto">
        <div className="card text-center">
          <div className="mx-auto h-20 w-20 bg-warning-100 rounded-full flex items-center justify-center mb-6">
            <span className="text-warning-600 text-4xl">🏆</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Leaderboard
          </h2>
          <p className="text-gray-600 mb-6">
            Leaderboard components are being developed. This will show rankings, 
            progress comparisons, and competitive features.
          </p>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-900 mb-2">Features Coming:</h3>
            <ul className="text-sm text-green-800 space-y-1">
              <li>• Overall rankings</li>
              <li>• Department-based leaderboards</li>
              <li>• Weekly/monthly competitions</li>
              <li>• Achievement showcases</li>
              <li>• Progress tracking</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
