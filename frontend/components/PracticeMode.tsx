'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { toast } from 'react-hot-toast'

export default function PracticeMode() {
  const {
    userStats,
    currentScenario,
    evaluationResults,
    showResults,
    scenarioGenerationMode,
    aiProbability,
    generateScenario,
    submitPrompt,
    setScenarioGenerationMode,
    setAiProbability,
    resetResults,
  } = useAppStore()

  const [selectedLevel, setSelectedLevel] = useState(
    userStats?.skill_level || 'beginner'
  )
  const [userPrompt, setUserPrompt] = useState('')
  const [hoverHints, setHoverHints] = useState(false)

  const handleGenerateScenario = async () => {
    try {
      await generateScenario(selectedLevel)
      setUserPrompt('')
      resetResults()
      toast.success('New scenario generated!')
    } catch (error) {
      toast.error('Failed to generate scenario')
      console.error('Scenario generation error:', error)
    }
  }

  const handleSubmitPrompt = async () => {
    if (!userPrompt.trim()) {
      toast.error('Please write a prompt before submitting')
      return
    }

    if (!currentScenario) {
      toast.error('Please generate a scenario first')
      return
    }

    try {
      await submitPrompt(userPrompt, currentScenario)
      toast.success('Prompt evaluated successfully!')
    } catch (error) {
      toast.error('Failed to evaluate prompt')
      console.error('Evaluation error:', error)
    }
  }

  const getScenarioButtonText = () => {
    switch (scenarioGenerationMode) {
      case 'preset': return '📚 Get Random Preset Scenario'
      case 'ai': return '🤖 Generate AI Scenario'
      case 'mixed': return '🎲 Get Random Scenario'
      default: return 'Get Scenario'
    }
  }

  const getNewScenarioButtonText = () => {
    switch (scenarioGenerationMode) {
      case 'preset': return 'Try Different Preset Scenario'
      case 'ai': return '🤖 Generate New AI Scenario'
      case 'mixed': return '🎲 Get Another Random Scenario'
      default: return 'New Scenario'
    }
  }

  const getNextScenarioButtonText = () => {
    switch (scenarioGenerationMode) {
      case 'preset': return 'Next Preset Scenario'
      case 'ai': return '🤖 Generate New AI Scenario'
      case 'mixed': return '🎲 Next Random Scenario'
      default: return 'Next Scenario'
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-➧">📝 Practice Mode</h1>

      {/* Scenario Generation */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🎲 Scenario Generation</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Choose scenario source:
                </label>
                <select
                  value={scenarioGenerationMode}
                  onChange={(e) => setScenarioGenerationMode(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="preset">📚 Preset Scenarios (Curated by experts)</option>
                  <option value="ai">🤖 AI-Generated Scenarios (Fresh & dynamic)</option>
                  <option value="mixed">🎲 Mixed Mode (Blend of preset & AI)</option>
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Choose difficulty level:
                  </label>
                  <select
                    value={selectedLevel}
                    onChange={(e) => setSelectedLevel(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                {scenarioGenerationMode === 'mixed' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      AI Generation Probability: {aiProbability}
                    </label>
                    <input
                      type="range"
                      min="0.1"
                      max="0.9"
                      step="0.1"
                      value={aiProbability}
                      onChange={(e) => setAiProbability(parseFloat(e.target.value))}
                      className="w-full"
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-col space-y-3">
            <button
              onClick={handleGenerateScenario}
              className="btn-primary flex items-center justify-center"
            >
              {getScenarioButtonText()}
            </button>
            
            {currentScenario && (
              <button
                onClick={handleGenerateScenario}
                className="btn-secondary"
              >
                {getNewScenarioButtonText()}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Current Scenario */}
      {currentScenario && (
        <div className="scenario-card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              📋 {currentScenario.title}
            </h3>
            <span className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
              {currentScenario.id?.endsWith('.99') || scenarioGenerationMode === 'ai' ? '🤖 AI-Generated' : '📚 Preset'}
            </span>
          </div>
          
          <div className="space-y-3 mb-4">
            <p><strong>Product:</strong> {currentScenario.product}</p>
            <p><strong>Scenario:</strong> {currentScenario.description}</p>
            <p><strong>Goal:</strong> {currentScenario.goal}</p>
            <p><strong>Context:</strong> {currentScenario.context}</p>
          </div>

          {/* Hints */}
          <div className="mt-4">
            <button
              onClick={() => setHoverHints(!hoverHints)}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              💡 Need hints? {hoverHints ? 'Hide' : 'Show'}
            </button>
            
            {hoverHints && (
              <div className="mt-2 p-4 bg-blue-50 rounded-lg">
                <ul className="space-y-2">
                  {currentScenario.hints.map((hint, index) => (
                    <li key={index} className="text-sm">
                      {index + 1}. {hint}
                    </li>
                  ))}
                </ul>
                
                <details className="mt-3">
                  <summary className="cursor-pointer text-sm font-medium text-blue-800">
                    Show example of a good prompt
                  </summary>
                  <div className="mt-2 p-3 bg-green-50 border-l-4 border-green-500 rounded">
                    <p className="text-sm text-gray-800">
                      <strong>Example:</strong> {currentScenario.example_good}
                    </p>
                  </div>
                </details>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Prompt Input */}
      {currentScenario && (
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">✍️ Write Your Prompt</h3>
          
          <textarea
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            placeholder="Write your prompt for the scenario above..."
            className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none resize-none"
          />
          
          <div className="flex gap-4 mt-4">
            <button
              onClick={handleSubmitPrompt}
              disabled={!userPrompt.trim() || showResults}
              className="btn-primary"
            >
              Submit for Evaluation
            </button>
            
            <button
              onClick={handleGenerateScenario}
              className="btn-secondary"
            >
              {getNextScenarioButtonText()}
            </button>
          </div>
        </div>
      )}

      {/* Evaluation Results */}
      {showResults && evaluationResults && (
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 Evaluation Results</h2>
          </div>

          {/* Score Display */}
          <div className={`p-6 rounded-xl ${
            evaluationResults.total_score >= 85 ? 'feedback-excellent' :
            evaluationResults.total_score >= 70 ? 'feedback-good' :
            'feedback-needs-work'
          }`}>
            <h2 className="text-2xl font-bold text-center">
              {evaluationResults.total_score >= 85 ? '🌟 Excellent!' :
               evaluationResults.total_score >= 70 ? '👍 Good job!' :
               '💪 Keep practicing!'}
              {' '}
              Your Score: {evaluationResults.total_score}/100
            </h2>
          </div>

          {/* Your Original Prompt */}
          <div className="bg-white rounded-lg shadow p-4 mb-6">
            <h4 className="font-medium text-gray-900 mb-2">✍️ Your Original Prompt:</h4>
            <div className="bg-gray-50 p-3 rounded-lg">
              <code className="text-sm text-gray-800">
                {userPrompt}
              </code>
            </div>
          </div>

          {/* Detailed Scores */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg text-center shadow">
              <div className="text-2xl font-bold text-blue-600">
                {evaluationResults.clarity_score}/25
              </div>
              <div className="text-sm text-gray-600">Clarity</div>
            </div>
            <div className="bg-white p-4 rounded-lg text-center shadow">
              <div className="text-2xl font-bold text-green-600">
                {evaluationResults.specificity_score}/25
              </div>
              <div className="text-sm text-gray-600">Specificity</div>
            </div>
            <div className="bg-white p-4 rounded-lg text-center shadow">
              <div className="text-2xl font-bold text-purple-600">
                {evaluationResults.structure_score}/25
              </div>
              <div className="text-sm text-gray-600">Structure</div>
            </div>
            <div className="bg-white p-4 rounded-lg text-center shadow">
              <div className="text-2xl font-bold text-orange-600">
                {evaluationResults.task_alignment_score}/25
              </div>
              <div className="text-sm text-gray-600">Task Alignment</div>
            </div>
          </div>

          {/* Feedback */}
          <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
            <h3 className="text-xl font-semibold text-gray-900">💬 Detailed Feedback</h3>
            <p className="text-gray-700">{evaluationResults.feedback}</p>
            
            {/* Strengths */}
            {evaluationResults.strengths.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">✅ Strengths</h4>
                <ul className="space-y-1">
                  {evaluationResults.strengths.map((strength: string, index: number) => (
                    <li key={index} className="text-green-700">✓ {strength}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Improvements */}
            {evaluationResults.improvements.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">🔧 Areas for Improvement</h4>
                <ul className="space-y-1">
                  {evaluationResults.improvements.map((improvement: string, index: number) => (
                    <li key={index} className="text-yellow-700">→ {improvement}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center">
            <button onClick={resetResults} className="btn-secondary">
              Try This Scenario Again
            </button>
            <button onClick={handleGenerateScenario} className="btn-primary">
              {getNextScenarioButtonText()}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
