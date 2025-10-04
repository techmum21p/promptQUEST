'use client'

export default function LearningResources() {
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">📚 Learning Resources</h1>
      
      <div className="space-y-8">
        {/* AI-Powered Scenario Generation */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            🎯 AI-Powered Scenario Generation
          </h2>
          
          <p className="text-gray-700 mb-6">
            This app now features <strong>AI-Generated Scenarios</strong> that provide unlimited practice opportunities:
          </p>
          
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">🤖 How It Works</h3>
              <ul className="text-gray-700 space-y-2 ml-4">
                <li><strong>Few-Shot Prompting:</strong> The AI uses our curated preset scenarios as examples</li>
                <li><strong>Dynamic Generation:</strong> Creates fresh scenarios that match the difficulty level</li>
                <li><strong>Quality Consistency:</strong> Maintains the same structure and educational value as preset scenarios</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">🎲 Scenario Modes</h3>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">1. 📚 Preset Scenarios</h4>
                  <p className="text-sm text-blue-800">Hand-crafted by experts, tested and refined</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-900 mb-2">2. 🤖 AI-Generated</h4>
                  <p className="text-sm text-green-800">Fresh scenarios created on-demand using advanced AI</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-medium text-purple-900 mb-2">3. 🎲 Mixed Mode</h4>
                  <p className="text-sm text-purple-800">Randomly combines both types for variety</p>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">💡 Benefits of AI Generation</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ul className="text-gray-700 space-y-2">
                  <li>• <strong>Unlimited Practice:</strong> Never run out of scenarios to practice with</li>
                  <li>• <strong>Adaptive Learning:</strong> Each scenario is unique while maintaining difficulty standards</li>
                </ul>
                <ul className="text-gray-700 space-y-2">
                  <li>• <strong>Diverse Challenges:</strong> AI creates scenarios covering various Microsoft 365 use cases</li>
                  <li>• <strong>Real-World Relevance:</strong> Generated scenarios reflect current workplace challenges</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Best Practices */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Prompt Engineering Best Practices for Microsoft 365 Copilot
          </h2>
          
          <div className="space-y-6">
            {/* Core Principles */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">🎯 Core Principles</h3>
              
              <div className="space-y-4">
                <div className="border-l-4 border-blue-500 pl-6">
                  <h4 className="font-medium text-gray-900 mb-2">1. Be Specific and Clear</h4>
                  <ul className="text-gray-700 space-y-1 ml-4">
                    <li>• Use concrete language</li>
                    <li>• Define exactly what you want</li>
                    <li>• Avoid ambiguous terms</li>
                  </ul>
                </div>
                
                <div className="border-l-4 border-green-500 pl-6">
                  <h4 className="font-medium text-gray-900 mb-2">2. Provide Context</h4>
                  <ul className="text-gray-700 space-y-1 ml-4">
                    <li>• Mention relevant documents, time periods, or data sources</li>
                    <li>• Specify your role or perspective</li>
                    <li>• Include constraints or requirements</li>
                  </ul>
                </div>
                
                <div className="border-l-4 border-purple-500 pl-6">
                  <h4 className="font-medium text-gray-900 mb-2">3. Structure Your Prompt</h4>
                  <ul className="text-gray-700 space-y-1 ml-4">
                    <li>• Break complex requests into steps</li>
                    <li>• Use numbering or bullet points</li>
                    <li>• Organize information logically</li>
                  </ul>
                </div>
                
                <div className="border-l-4 border-orange-500 pl-6">
                  <h4 className="font-medium text-gray-900 mb-2">4. Iterate and Refine</h4>
                  <ul className="text-gray-700 space-y-1 ml-4">
                    <li>• Start broad, then narrow down</li>
                    <li>• Review and adjust based on results</li>
                    <li>• Learn from feedback</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Product-Specific Tips */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">💼 Product-Specific Tips</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Outlook Copilot:</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• Specify time ranges for email searches</li>
                      <li>• Mention specific senders or subjects</li>
                      <li>• Request specific output formats (summary, bullet points, etc.)</li>
                    </ul>
                  </div>
                  
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-2">Word Copilot:</h4>
                    <ul className="text-sm text-green-800 space-y-1">
                      <li>• Describe the tone and style you want</li>
                      <li>• Specify document structure (headings, sections)</li>
                      <li>• Mention formatting requirements</li>
                    </ul>
                  </div>
                  
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h4 className="font-medium text-purple-900 mb-2">Excel Copilot:</h4>
                    <ul className="text-sm text-purple-800 space-y-1">
                      <li>• Be clear about data ranges</li>
                      <li>• Specify analysis type (trends, comparisons, etc.)</li>
                      <li>• Request specific visualization types</li>
                    </ul>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <h4 className="font-medium text-orange-900 mb-2">PowerPoint Copilot:</h4>
                    <ul className="text-sm text-orange-800 space-y-1">
                      <li>• Define your audience</li>
                      <li>• Specify number of slides and structure</li>
                      <li>• Mention design preferences or templates</li>
                    </ul>
                  </div>
                  
                  <div className="bg-pink-50 p-4 rounded-lg">
                    <h4 className="font-medium text-pink-900 mb-2">Teams Copilot:</h4>
                    <ul className="text-sm text-pink-800 space-y-1">
                      <li>• Reference specific channels or time periods</li>
                      <li>• Request summaries of discussions or decisions</li>
                      <li>• Specify action items or follow-ups needed</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Resources */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">🔗 Additional Resources</h3>
              <div className="space-y-2">
                <a href="https://support.microsoft.com/copilot" target="_blank" rel="noopener noreferrer" className="block text-blue-600 hover:text-blue-800">
                  → Microsoft Copilot Documentation
                </a>
                <a href="https://www.promptingguide.ai/" target="_blank" rel="noopener noreferrer" className="block text-blue-600 hover:text-blue-800">
                  → Prompt Engineering Guide
                </a>
                <a href="https://adoption.microsoft.com/copilot/" target="_blank" rel="noopener noreferrer" className="block text-blue-600 hover:text-blue-800">
                  → Microsoft 365 Copilot Best Practices
                </a>
                <a href="https://www.hbs.net/blog/copilot-prompt-help" target="_blank" rel="noopener noreferrer" className="block text-blue-600 hover:text-blue-800">
                  → Best Microsoft Copilot Prompts--And How to Write Them
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* AI Generation Example */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <button className="btn-secondary mb-4">🔍 Example: How AI Scenarios Are Generated</button>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Input to AI:</h3>
              <ul className="text-gray-700 space-y-1 ml-4">
                <li>• Difficulty level (e.g., "intermediate")</li>
                <li>• 2-3 preset scenarios as examples (few-shot prompting)</li>
                <li>• Requirements for Microsoft 365 Copilot context</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">AI Output:</h3>
              <p className="text-gray-700 mb-2">A new scenario with the same structure:</p>
              <div className="bg-gray-50 p-4 rounded-lg text-sm">
                <code>
{`{
  "id": "i4",
  "title": "Customer Data Analysis Dashboard",
  "description": "You need to create an executive dashboard from customer survey data.",
  "goal": "Generate insights and visualizations from customer feedback",
  "context": "Quarterly customer satisfaction survey with 500+ responses",
  "product": "Excel Copilot", 
  "hints": ["Specify chart types", "Include trend analysis", "Request key metrics"],
  "example_good": "Create an executive dashboard from Q3 customer survey data..."
}`}
                </code>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Quality Assurance:</h3>
              <ul className="text-gray-700 space-y-1 ml-4">
                <li>• Same JSON structure as preset scenarios</li>
                <li>• Appropriate difficulty level</li>
                <li>• Realistic Microsoft 365 use case</li>
                <li>• Clear, actionable prompts</li>
              </ul>
            </div>
            
            <div className="text-center">
              <a href="/practice">
                <button className="btn-primary">
                  🎯 Try AI Generation Now!
                </button>
              </a>
              <p className="text-sm text-gray-600 mt-2">
                👆 Go to <strong>Practice Mode</strong> and select <strong>🤖 AI-Generated Scenarios</strong> to experience this feature!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
