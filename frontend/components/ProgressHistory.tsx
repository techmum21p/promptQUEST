'use client'

import { useEffect } from 'react'
import { useAppStore } from '@/lib/store'

export default function ProgressHistory() {
  const { userStats, fetchUserStats } = useAppStore()

  useEffect(() => {
    fetchUserStats()
  }, [fetchUserStats])

  if (!userStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">📈 Your Progress History</h1>
      
      {userStats.history.length === 0 ? (
        <div className="bg-white rounded-xl shadow-md p-8 text-center">
          <div className="text-4xl mb-4">🚀</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No attempts yet
          </h2>
          <p className="text-gray-600">
            Start practicing to see your progress history here!
          </p>
        </div>
      ) : (
        <div>
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Total Attempts: {userStats.history.length}
            </h2>
          </div>
          
          <div className="space-y-6">
            {userStats.history
              .slice()
              .reverse()
              .map((attempt, index) => {
                const attemptNumber = userStats.history.length - index
                const evaluation = attempt.evaluation
                
                return (
                  <div key={index} className="bg-white rounded-xl shadow-md p-6">
                    <div className="flex items-center justify-between mb-4">
                      <button className="text-left hover:bg-gray-50 p-3 rounded-lg transition-colors">
                            ▲
                      </button>
                      <div className="pb-3">
                        <h3 className="text-lg font-semibold text-gray-900">
                          Attempt {attemptNumber}: Score {attempt.score}/100
                        </h3>
                        <p className="text-sm text-gray-600">
                          {attempt.scenario_id} • {new Date(attempt.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                      <button className="text-left hover:bg-gray-50 p-3 rounded-lg transition-colors"
                              onClick={() => {
                                const summary = document.getElementById(`summary-${index}`)
                                if (summary) {
                                  summary.classList.toggle('hidden')
                                }
                              }}>
                        ▼ Show Details
                      </button>
                    </div>
                    
                    {/* Score Breakdown */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                      <div className="bg-blue-50 p-3 rounded-lg text-center">
                        <div className="text-lg font-bold text-blue-600">
                          {evaluation.clarity_score || 0}/25
                        </div>
                        <div className="text-xs text-blue-800">Clarity</div>
                      </div>
                      <div className="bg-green-50 p-3 rounded-lg text-center">
                        <div className="text-lg font-bold text-green-600">
                          {evaluation.specificity_score || 0}/25
                        </div>
                        <div className="text-xs text-green-800">Specificity</div>
                      </div>
                      <div className="bg-purple-50 p-3 rounded-lg text-center">
                        <div className="text-lg font-bold text-purple-600">
                          {evaluation.structure_score || 0}/25
                        </div>
                        <div className="text-xs text-purple-800">Structure</div>
                      </div>
                      <div className="bg-orange-50 p-3 rounded-lg text-center">
                        <div className="text-lg font-bold text-orange-600">
                          {evaluation.task_alignment_score || 0}/25
                        </div>
                        <div className="text-xs text-orange-800">Alignment</div>
                      </div>
                    </div>
                    
                    {/* Detailed Information */}
                    <div id={`summary-${index}`} className="hidden space-y-4">
                      {/* User's Original Prompt */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">
                          Your Original Prompt:
                        </h4>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <code className="text-sm text-gray-800">
                            {attempt.user_prompt || 'No prompt recorded'}
                          </code>
                        </div>
                      </div>
                      
                      {/* Feedback Grid */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        {/* Strengths */}
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">
                            ✅ Strengths:
                          </h4>
                          {evaluation.strengths?.length > 0 ? (
                            <ul className="space-y-1">
                              {evaluation.strengths.map((strength: string, idx: number) => (
                                <li key={idx} className="text-sm text-green-700">
                                  ✓ {strength}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-sm text-gray-500">No specific strengths identified</p>
                          )}
                        </div>
                        
                        {/* Areas for Improvement */}
                        <div>
                          <h4 className="font-medium text-green-900 mb-2">
                            🔧 Areas for Improvement:
                          </h4>
                          {evaluation.improvements?.length > 0 ? (
                            <ul className="space-y-1">
                              {evaluation.improvements.map((improvement: string, idx: number) => (
                                <li key={idx} className="text-sm text-yellow-700">
                                  → {improvement}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-sm text-gray-500">Great job! No specific areas for improvement identified</p>
                          )}
                        </div>
                      </div>
                      
                      {/* Detailed Feedback */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">
                          💬 Detailed Feedback:
                        </h4>
                        <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded-lg">
                          {evaluation.feedback || 'No detailed feedback available'}
                        </p>
                      </div>
                    </div>
                  </div>
                )
              })
            }
          </div>
        </div>
      )}
    </div>
  )
}
