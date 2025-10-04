'use client'

import { useEffect, useState } from 'react'
import { useAppStore } from '@/lib/store'
import { toast } from 'react-hot-toast'

export default function DataExport() {
  const { exportSummary, fetchExportSummary, exportToCsv } = useAppStore()
  const [customFilename, setCustomFilename] = useState('')
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    fetchExportSummary()
  }, [fetchExportSummary])

  const handleExport = async (filename?: string) => {
    try {
      setExporting(true)
      
      await exportToCsv(filename || customFilename || undefined)
      toast.success(`Data exported successfully!`)
      
      // Refresh the export summary after successful export
      await fetchExportSummary()
    } catch (error) {
      toast.error('Export failed')
      console.error('Export error:', error)
    } finally {
      setExporting(false)
    }
  }

  const nextAutoBackup = exportSummary 
    ? ((exportSummary.active_users / 5) + 1) * 5
    : 5

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">📊 Data Export & Analytics</h1>
      
      {/* Summary Stats */}
      {exportSummary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {exportSummary.total_users}
            </div>
            <div className="text-sm text-gray-600">Total Users</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {exportSummary.active_users}
            </div>
            <div className="text-sm text-gray-600">Active Users</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {exportSummary.total_attempts}
            </div>
            <div className="text-sm text-gray-600">Total Attempts</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow text-center">
            <div className="text-1xl font-bold text-orange-600 mb-2">
              {exportSummary.avg_score_all_users.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">Overall Avg Score</div>
          </div>
        </div>
      )}

      {/* Export Options */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Custom Export */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            📥 Export Data
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom filename (optional):
              </label>
              <input
                type="text"
                value={customFilename}
                onChange={(e) => setCustomFilename(e.target.value)}
                placeholder="e.g., my_export.csv"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Leave empty for auto-generated timestamp filename
              </p>
            </div>
            
            <button
              onClick={() => handleExport(customFilename.trim() || undefined)}
              disabled={exporting}
              className="w-full btn-primary flex items-center justify-center"
            >
              {exporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 4 w-4 border-b-2 border-white mr-2"></div>
                  📊 Exporting...
                </>
              ) : (
                '📊 Export to CSV'
              )}
            </button>
          </div>
        </div>

        {/* Quick Export */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            🔄 Quick Export
          </h2>
          
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Export data instantly with an auto-generated timestamp filename.
            </p>
            
            <button
              onClick={() => handleExport()}
              disabled={exporting}
              className="w-full btn-secondary flex items-center justify-center"
            >
              {exporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
                  Exporting...
                </>
              ) : (
                '📄 Export Now with Timestamp'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* What's Included */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          📋 What's Included in Export
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">👤 User Information:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Username and skill level</li>
              <li>• Total attempts and cumulative score</li>
              <li>• Average score and badges earned</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900 mb-2">📊 Attempt Details:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Timestamp of each attempt</li>
              <li>• Scenario ID attempted</li>
              <li>• User's original prompt text</li>
              <li>• Score breakdown (clarity, specificity, structure, alignment)</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900 mb-2">🎯 Learning Insights:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• AI-identified strengths</li>
              <li>• Areas for improvement suggestions</li>
              <li>• Detailed feedback summary</li>
              <li>• Compatible with Excel, Google Sheets, Python, R</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Auto-backup Status */}
      {exportSummary && exportSummary.total_users > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-center">
            <div className="text-blue-600 mr-3">🔄</div>
            <div className="text-sm text-blue-800">
              <span className="font-medium">Auto-Backup Status:</span>{' '}
              Next automatic backup will be created at {nextAutoBackup} active users 
              (currently: {exportSummary.active_users})
            </div>
          </div>
        </div>
      )}

      {/* Usage Tips */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <button className="btn-secondary mb-4">📝 Export Usage Tips</button>
        
        <div className="space-y-4 text-sm">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">💡 Data Analysis Ideas</h3>
            
            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-gray-800 mb-1">Excel/Google Sheets:</h4>
                <ul className="text-gray-600 space-y-1 ml-2">
                  <li>• Create pivot tables to analyze performance by scenario</li>
                  <li>• Generate charts showing improvement over time</li>
                  <li>• Filter by skill level or score ranges</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-800 mb-1">Python Analysis:</h4>
                <div className="bg-gray-50 p-3 rounded-lg text-xs">
                  <code>
{`import pandas as pd
df = pd.read_csv('your_export.csv')

# User performance trends
df.groupby('username')['total_score'].mean()

# Scenario difficulty analysis  
df.groupby('scenario_id')['total_score'].agg(['mean', 'count'])

# Learning progress over time
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.plot(x='timestamp', y='total_score')`}
                  </code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
