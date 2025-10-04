'use client'

export function AdminPanel() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Panel</h1>
        <p className="text-gray-600">Manage users, scenarios, and system settings</p>
      </div>

      {/* Coming Soon */}
      <div className="max-w-md mx-auto">
        <div className="card text-center">
          <div className="mx-auto h-20 w-20 bg-warning-100 rounded-full flex items-center justify-center mb-6">
            <span className="text-warning-600 text-4xl">⚙️</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Admin Panel
          </h2>
          <p className="text-gray-600 mb-6">
            Admin panel components are being developed. This will provide comprehensive 
            administrative tools and analytics.
          </p>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="font-semibold text-red-900 mb-2">Features Coming:</h3>
            <ul className="text-sm text-red-800 space-y-1">
              <li>• User management</li>
              <li>• Scenario administration</li>
              <li>• Analytics dashboard</li>
              <li>• System health monitoring</li>
              <li>• Export capabilities</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
