'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { toast } from 'react-hot-toast'

export default function AdminPanel() {
  const { fetchLeaderboard, exportToCsv, getRawData } = useAppStore()
  const [showRawData, setShowRawData] = useState(false)
  const [rawData, setRawData] = useState(null)
  const [creatingBackup, setCreatingBackup] = useState(false)

  const refreshData = async () => {
    try {
      await fetchLeaderboard()
      toast.success('Data refreshed successfully!')
    } catch (error) {
      toast.error('Failed to refresh data')
      console.error('Refresh error:', error)
    }
  }

  const viewRawJson = async () => {
    try {
      const data = await getRawData()
      setRawData(data)
      setShowRawData(true)
    } catch (error) {
      toast.error('Failed to fetch raw data')
      console.error('Raw data error:', error)
    }
  }

  const createEmergencyBackup = async () => {
    try {
      setCreatingBackup(true)
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')
      const filename = `emergency_backup_${timestamp}.csv`
      
      await exportToCsv(filename)
      toast.success(`Emergency backup created: ${filename}`)
    } catch (error) {
      toast.error('Backup failed')
      console.error('Backup error:', error)
    } finally {
      setCreatingBackup(false)
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">⚙️ Admin Panel</h1>
      
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-8">
        <div className="flex items-center">
          <div className="text-yellow-600 mr-3">🔧</div>
          <div className="text-sm text-yellow-800">
            <span className="font-medium">Administrative functions - use with caution!</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Data Management */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🗃️ Data Management</h2>
          
          <div className="space-y-4">
            <button
              onClick={refreshData}
              className="w-full btn-secondary flex items-center justify-center"
            >
              <div className="mr-2">🔄</div>
              Refresh Data
              <div className="ml-2 text-xs">Reload data from JSON file</div>
            </button>
            
            <button
              onClick={viewRawJson}
              className="w-full btn-secondary flex items-center justify-center"
            >
              <div className="mr-2">📋</div>
              View Raw JSON
              <div className="ml-2 text-xs">Display raw JSON data structure</div>
            </button>
          </div>
        </div>

        {/* File Information */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📁 File Information</h2>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">File Status:</span>
              <span className="text-sm font-medium text-green-600">🟢 Active</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Storage Format:</span>
              <span className="text-sm font-medium">JSON</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Auto-Backup:</span>
              <span className="text-sm font-medium text-green-600">🟢 Enabled</span>
            </div>
          </div>
        </div>
      </div>

      {/* Backup Management */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">💾 Backup Management</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-4">
            <button
              onClick={createEmergencyBackup}
              disabled={creatingBackup}
              className="w-full btn-secondary flex items-center justify-center"
            >
              {creatingBackup ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
                  🆘 Creating...
                </>
              ) : (
                <>
                  <div className="mr-2">🆘</div>
                  Create Emergency Backup
                </>
              )}
            </button>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Recommended Actions:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Export data regularly for analysis</li>
              <li>• Keep backups before major updates</li>
              <li>• Monitor file size as users grow</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Raw Data Display */}
      {showRawData && rawData && (
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">📋 Raw JSON Data</h2>
            <button
              onClick={() => setShowRawData(false)}
              className="btn-secondary"
            >
              Close
            </button>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
            <pre className="text-sm text-gray-800">
              {JSON.stringify(rawData, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* System Status */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 System Status</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-medium text-green-900 mb-2">API Health</h3>
            <div className="text-sm text-green-800">🟢 All systems operational</div>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">AI Services</h3>
            <div className="text-sm text-blue-800">🟢 Google Gemini connected</div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="font-medium text-purple-900 mb-2">Data Storage</h3>
            <div className="text-sm text-purple-800">🟢 Local storage active</div>
          </div>
        </div>
      </div>
    </div>
  )
}
