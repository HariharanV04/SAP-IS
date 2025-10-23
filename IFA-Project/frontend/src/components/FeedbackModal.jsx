import React, { useState } from 'react'
import { X, Star, ThumbsUp, ThumbsDown, AlertCircle, CheckCircle } from 'lucide-react'
import * as api from '../services/api'

const FeedbackModal = ({ isOpen, onClose, jobInfo }) => {
  const [activeTab, setActiveTab] = useState('overall')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  
  // Overall Feedback
  const [overallRating, setOverallRating] = useState(3)
  const [docQualityRating, setDocQualityRating] = useState(3)
  const [iflowQualityRating, setIflowQualityRating] = useState(3)
  
  // What worked / didn't work
  const [whatWorkedWell, setWhatWorkedWell] = useState('')
  const [whatNeedsImprovement, setWhatNeedsImprovement] = useState('')
  
  // Business Logic
  const [businessLogicPreserved, setBusinessLogicPreserved] = useState(null)
  const [businessLogicIssues, setBusinessLogicIssues] = useState('')
  const [dataTransformationAccurate, setDataTransformationAccurate] = useState(null)
  const [dataTransformationIssues, setDataTransformationIssues] = useState('')
  
  // Documentation Feedback
  const [docCompletenessScore, setDocCompletenessScore] = useState(5)
  const [docMissingSections, setDocMissingSections] = useState('')
  const [docImprovements, setDocImprovements] = useState('')
  
  // iFlow Generation Feedback
  const [componentMappingAccuracy, setComponentMappingAccuracy] = useState(5)
  const [configAccuracy, setConfigAccuracy] = useState(5)
  const [integrationPatternCorrect, setIntegrationPatternCorrect] = useState(null)
  const [integrationPatternFeedback, setIntegrationPatternFeedback] = useState('')
  
  // Manual Fixes
  const [missingComponents, setMissingComponents] = useState('')
  const [incorrectComponents, setIncorrectComponents] = useState('')
  const [manualFixesRequired, setManualFixesRequired] = useState('')
  
  // Deployment
  const [deploymentSuccessful, setDeploymentSuccessful] = useState(null)
  const [deploymentIssues, setDeploymentIssues] = useState('')
  const [timeToFixMinutes, setTimeToFixMinutes] = useState('')
  const [effortLevel, setEffortLevel] = useState('moderate')
  
  // Additional Comments
  const [additionalComments, setAdditionalComments] = useState('')
  
  if (!isOpen) return null
  
  const StarRating = ({ rating, setRating, label }) => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
            className="focus:outline-none transition-transform hover:scale-110"
          >
            <Star
              size={28}
              className={star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
            />
          </button>
        ))}
        <span className="ml-2 text-sm text-gray-600">{rating > 0 ? `${rating}/5` : 'Not rated'}</span>
      </div>
    </div>
  )
  
  const BooleanChoice = ({ value, setValue, label, yesLabel = 'Yes', noLabel = 'No' }) => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <div className="flex gap-4">
        <button
          onClick={() => setValue(true)}
          className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
            value === true
              ? 'bg-green-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <ThumbsUp size={18} />
          {yesLabel}
        </button>
        <button
          onClick={() => setValue(false)}
          className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
            value === false
              ? 'bg-red-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <ThumbsDown size={18} />
          {noLabel}
        </button>
      </div>
    </div>
  )
  
  const handleSubmit = async () => {
    setSubmitting(true)
    
    try {
      const feedbackData = {
        job_id: jobInfo.id,
        source_platform: jobInfo.platform || 'boomi',
        source_file_name: jobInfo.file_name || jobInfo.fileName,
        
        // Overall ratings
        overall_rating: overallRating,
        documentation_quality_rating: docQualityRating,
        iflow_quality_rating: iflowQualityRating,
        
        // What worked / didn't work
        what_worked_well: whatWorkedWell.split('\n').filter(x => x.trim()),
        what_needs_improvement: whatNeedsImprovement.split('\n').filter(x => x.trim()),
        
        // Business logic
        business_logic_preserved: businessLogicPreserved,
        business_logic_issues: businessLogicIssues,
        data_transformation_accurate: dataTransformationAccurate,
        data_transformation_issues: dataTransformationIssues,
        
        // Documentation
        documentation_completeness_score: docCompletenessScore,
        documentation_missing_sections: docMissingSections.split('\n').filter(x => x.trim()),
        documentation_improvements: docImprovements,
        
        // iFlow generation
        component_mapping_accuracy: componentMappingAccuracy,
        configuration_accuracy: configAccuracy,
        integration_pattern_correct: integrationPatternCorrect,
        integration_pattern_feedback: integrationPatternFeedback,
        
        // Manual fixes
        missing_components: missingComponents.split('\n').filter(x => x.trim()),
        incorrect_components: incorrectComponents.split('\n').filter(x => x.trim()),
        manual_fixes_required: manualFixesRequired ? JSON.parse(manualFixesRequired) : {},
        
        // Deployment
        deployment_successful: deploymentSuccessful,
        deployment_issues: deploymentIssues,
        time_to_fix_minutes: timeToFixMinutes ? parseInt(timeToFixMinutes) : null,
        effort_level: effortLevel,
        
        // Comments
        comments: additionalComments
      }
      
      const response = await api.submitFeedback(feedbackData)
      
      if (response.status === 'success') {
        setSubmitted(true)
        setTimeout(() => {
          onClose()
        }, 2000)
      }
    } catch (error) {
      console.error('Error submitting feedback:', error)
      alert('Failed to submit feedback. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }
  
  if (submitted) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md text-center relative">
          <button 
            onClick={onClose} 
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full p-1 transition-colors"
            aria-label="Close"
          >
            <X size={20} />
          </button>
          <CheckCircle size={64} className="text-green-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-800 mb-2">Thank You!</h3>
          <p className="text-gray-600">Your feedback helps us improve the system for everyone.</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">Migration Feedback</h2>
            <p className="text-blue-100 text-sm mt-1">Help us improve the conversion quality</p>
          </div>
          <button onClick={onClose} className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2">
            <X size={24} />
          </button>
        </div>
        
        {/* Tabs */}
        <div className="border-b flex flex-wrap gap-2">
          {[
            { id: 'overall', label: 'Overall' },
            { id: 'documentation', label: 'Documentation' },
            { id: 'iflow', label: 'iFlow Quality' },
            { id: 'fixes', label: 'Manual Fixes' },
            { id: 'deployment', label: 'Deployment' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-600 text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'overall' && (
            <div>
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
                <div className="text-sm text-blue-800 space-y-1">
                  <p>
                    <strong>Job ID:</strong> {jobInfo.id}
                  </p>
                  <p>
                    <strong>Platform:</strong> {jobInfo.platform || 'Boomi'}
                  </p>
                  <p>
                    <strong>File:</strong> {jobInfo.file_name || jobInfo.fileName || 'N/A'}
                  </p>
                </div>
              </div>
              
              <StarRating
                rating={overallRating}
                setRating={setOverallRating}
                label="Overall Migration Quality"
              />
              
              <StarRating
                rating={docQualityRating}
                setRating={setDocQualityRating}
                label="Documentation Quality"
              />
              
              <StarRating
                rating={iflowQualityRating}
                setRating={setIflowQualityRating}
                label="Generated iFlow Quality"
              />
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What Worked Well? (one per line)
                </label>
                <textarea
                  value={whatWorkedWell}
                  onChange={(e) => setWhatWorkedWell(e.target.value)}
                  className="w-full border rounded-lg p-3 h-24"
                  placeholder="- Component mapping was accurate&#10;- Documentation was clear&#10;- Integration pattern was correct"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What Needs Improvement? (one per line)
                </label>
                <textarea
                  value={whatNeedsImprovement}
                  onChange={(e) => setWhatNeedsImprovement(e.target.value)}
                  className="w-full border rounded-lg p-3 h-24"
                  placeholder="- Missing SFTP polling component&#10;- Incorrect data mapping&#10;- Documentation lacked error handling details"
                />
              </div>
              
              <BooleanChoice
                value={businessLogicPreserved}
                setValue={setBusinessLogicPreserved}
                label="Was the Business Logic Preserved?"
              />
              
              {businessLogicPreserved === false && (
                <div className="mb-4 ml-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What Business Logic Issues Did You Find?
                  </label>
                  <textarea
                    value={businessLogicIssues}
                    onChange={(e) => setBusinessLogicIssues(e.target.value)}
                    className="w-full border rounded-lg p-3 h-20"
                    placeholder="Describe the business logic that was lost or incorrect..."
                  />
                </div>
              )}
              
              <BooleanChoice
                value={dataTransformationAccurate}
                setValue={setDataTransformationAccurate}
                label="Was Data Transformation Accurate?"
              />
              
              {dataTransformationAccurate === false && (
                <div className="mb-4 ml-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What Data Transformation Issues Did You Find?
                  </label>
                  <textarea
                    value={dataTransformationIssues}
                    onChange={(e) => setDataTransformationIssues(e.target.value)}
                    className="w-full border rounded-lg p-3 h-20"
                    placeholder="Describe the data transformation issues..."
                  />
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'documentation' && (
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Documentation Completeness (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={docCompletenessScore}
                  onChange={(e) => setDocCompletenessScore(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>Incomplete</span>
                  <span className="font-bold">{docCompletenessScore}/10</span>
                  <span>Complete</span>
                </div>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Missing Documentation Sections (one per line)
                </label>
                <textarea
                  value={docMissingSections}
                  onChange={(e) => setDocMissingSections(e.target.value)}
                  className="w-full border rounded-lg p-3 h-24"
                  placeholder="- Error handling details&#10;- Connection configuration&#10;- Authentication setup"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Suggested Documentation Improvements
                </label>
                <textarea
                  value={docImprovements}
                  onChange={(e) => setDocImprovements(e.target.value)}
                  className="w-full border rounded-lg p-3 h-32"
                  placeholder="Provide suggestions for how documentation could be improved..."
                />
              </div>
            </div>
          )}
          
          {activeTab === 'iflow' && (
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Component Mapping Accuracy (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={componentMappingAccuracy}
                  onChange={(e) => setComponentMappingAccuracy(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>Inaccurate</span>
                  <span className="font-bold">{componentMappingAccuracy}/10</span>
                  <span>Accurate</span>
                </div>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Configuration Accuracy (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={configAccuracy}
                  onChange={(e) => setConfigAccuracy(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>Inaccurate</span>
                  <span className="font-bold">{configAccuracy}/10</span>
                  <span>Accurate</span>
                </div>
              </div>
              
              <BooleanChoice
                value={integrationPatternCorrect}
                setValue={setIntegrationPatternCorrect}
                label="Was the Integration Pattern Correct?"
                yesLabel="Correct"
                noLabel="Incorrect"
              />
              
              {integrationPatternCorrect === false && (
                <div className="mb-4 ml-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What Was Wrong With the Integration Pattern?
                  </label>
                  <textarea
                    value={integrationPatternFeedback}
                    onChange={(e) => setIntegrationPatternFeedback(e.target.value)}
                    className="w-full border rounded-lg p-3 h-20"
                    placeholder="Describe what was wrong with the integration pattern..."
                  />
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'fixes' && (
            <div>
              <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-6">
                <p className="text-sm text-yellow-800">
                  <AlertCircle size={16} className="inline mr-2" />
                  This information is critical for training the system to improve future conversions.
                </p>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Missing Components (one per line)
                </label>
                <textarea
                  value={missingComponents}
                  onChange={(e) => setMissingComponents(e.target.value)}
                  className="w-full border rounded-lg p-3 h-24"
                  placeholder="- Timer (for polling)&#10;- SFTP Adapter&#10;- Error Handler"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Incorrect Components (one per line)
                </label>
                <textarea
                  value={incorrectComponents}
                  onChange={(e) => setIncorrectComponents(e.target.value)}
                  className="w-full border rounded-lg p-3 h-24"
                  placeholder="- Used HTTP instead of SFTP&#10;- Router logic was inverted"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time Spent on Manual Fixes (minutes)
                </label>
                <input
                  type="number"
                  value={timeToFixMinutes}
                  onChange={(e) => setTimeToFixMinutes(e.target.value)}
                  className="w-full border rounded-lg p-3"
                  placeholder="e.g., 30"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Effort Level Required
                </label>
                <select
                  value={effortLevel}
                  onChange={(e) => setEffortLevel(e.target.value)}
                  className="w-full border rounded-lg p-3"
                >
                  <option value="minimal">Minimal - Just minor tweaks</option>
                  <option value="moderate">Moderate - Some fixes needed</option>
                  <option value="significant">Significant - Major rework required</option>
                  <option value="major">Major - Almost rebuilt from scratch</option>
                </select>
              </div>
            </div>
          )}
          
          {activeTab === 'deployment' && (
            <div>
              <BooleanChoice
                value={deploymentSuccessful}
                setValue={setDeploymentSuccessful}
                label="Was Deployment Successful?"
                yesLabel="Success"
                noLabel="Failed"
              />
              
              {deploymentSuccessful === false && (
                <div className="mb-4 ml-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What Deployment Issues Did You Encounter?
                  </label>
                  <textarea
                    value={deploymentIssues}
                    onChange={(e) => setDeploymentIssues(e.target.value)}
                    className="w-full border rounded-lg p-3 h-24"
                    placeholder="Describe the deployment issues..."
                  />
                </div>
              )}
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Comments & Suggestions
                </label>
                <textarea
                  value={additionalComments}
                  onChange={(e) => setAdditionalComments(e.target.value)}
                  className="w-full border rounded-lg p-3 h-32"
                  placeholder="Any other feedback, suggestions, or comments..."
                />
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="border-t p-6 bg-gray-50 flex justify-between items-center">
          <button
            onClick={onClose}
            className="px-6 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || overallRating === 0}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default FeedbackModal

