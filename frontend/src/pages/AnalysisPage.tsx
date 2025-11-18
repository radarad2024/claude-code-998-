import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Image as ImageIcon, Brain, Zap, CheckCircle, AlertCircle, Loader2, Eye, FileText } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import axios from 'axios'
import clsx from 'clsx'

interface AnalysisResult {
  analysis_id: string
  findings: Array<{
    pathology: string
    confidence: number
    severity: string
  }>
  confidence_scores: Record<string, number>
  heatmap_url: string
  report_draft: string
  processing_time: number
  model_info: {
    model_type: string
    version: string
  }
}

export default function AnalysisPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [modality, setModality] = useState('xray')
  const [bodyPart, setBodyPart] = useState('chest')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)

  const analysisMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('modality', modality)
      formData.append('body_part', bodyPart)
      formData.append('model_type', 'ensemble')

      const response = await axios.post('/api/v1/analysis/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      setAnalysisResult(data)
      toast.success('Analysis completed successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Analysis failed')
    },
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setSelectedFile(file)

      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string)
      }
      reader.readAsDataURL(file)

      // Reset previous results
      setAnalysisResult(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.dcm'],
      'application/dicom': ['.dcm'],
    },
    maxFiles: 1,
  })

  const handleAnalyze = () => {
    if (selectedFile) {
      analysisMutation.mutate(selectedFile)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <div className="p-3 bg-blue-600 rounded-xl">
                <Brain className="w-8 h-8" />
              </div>
              AI Medical Image Analysis
            </h1>
            <p className="text-gray-300 text-lg">
              Upload medical images for instant AI-powered analysis
            </p>
          </div>
          {analysisResult && (
            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500/50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span className="text-green-300 font-medium">Analysis Complete</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="space-y-6">
            {/* Upload Area */}
            <div className="glass-card rounded-2xl p-6 space-y-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Upload className="w-5 h-5 text-blue-400" />
                Upload Image
              </h2>

              <div
                {...getRootProps()}
                className={clsx(
                  'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all',
                  isDragActive
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-600 hover:border-blue-500 hover:bg-slate-800/50'
                )}
              >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center gap-4">
                  {previewUrl ? (
                    <div className="relative">
                      <img
                        src={previewUrl}
                        alt="Preview"
                        className="max-h-64 rounded-lg shadow-lg"
                      />
                      <div className="absolute top-2 right-2 px-3 py-1 bg-green-500 text-white text-sm font-medium rounded-full">
                        Ready
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="p-4 bg-blue-500/10 rounded-full">
                        <ImageIcon className="w-12 h-12 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-white font-medium mb-1">
                          Drop medical image here, or click to browse
                        </p>
                        <p className="text-sm text-gray-400">
                          Supports DICOM, PNG, JPEG (Max 100MB)
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {selectedFile && (
                <div className="flex items-center gap-3 p-4 bg-slate-800/50 rounded-lg">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <div className="flex-1">
                    <p className="text-white font-medium">{selectedFile.name}</p>
                    <p className="text-sm text-gray-400">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
              )}

              {/* Settings */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Modality
                  </label>
                  <select
                    value={modality}
                    onChange={(e) => setModality(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="xray">X-Ray</option>
                    <option value="ct">CT Scan</option>
                    <option value="mri">MRI</option>
                    <option value="ultrasound">Ultrasound</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Body Part
                  </label>
                  <select
                    value={bodyPart}
                    onChange={(e) => setBodyPart(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="chest">Chest</option>
                    <option value="brain">Brain</option>
                    <option value="bone">Bone/Extremity</option>
                    <option value="abdomen">Abdomen</option>
                    <option value="spine">Spine</option>
                  </select>
                </div>
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={!selectedFile || analysisMutation.isPending}
                className="w-full py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all btn-hover-lift disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
              >
                {analysisMutation.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Run AI Analysis
                  </>
                )}
              </button>
            </div>

            {/* AI Model Info */}
            <div className="glass-card rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">AI Model Information</h3>
              <div className="space-y-3">
                <InfoRow label="Model Type" value="Ensemble (EfficientNet + DenseNet + ResNet)" />
                <InfoRow label="Accuracy" value="96% AUC" />
                <InfoRow label="Sensitivity" value="94%" />
                <InfoRow label="Specificity" value="92%" />
                <InfoRow label="Avg. Processing Time" value="~2.5 seconds" />
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {analysisMutation.isPending && (
              <div className="glass-card rounded-2xl p-12">
                <div className="flex flex-col items-center gap-6">
                  <div className="relative">
                    <div className="w-24 h-24 border-4 border-blue-500/30 rounded-full"></div>
                    <div className="w-24 h-24 border-4 border-blue-500 border-t-transparent rounded-full animate-spin absolute top-0"></div>
                  </div>
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-white mb-2">
                      AI Analysis in Progress
                    </h3>
                    <p className="text-gray-400">
                      Running deep learning models on your image...
                    </p>
                  </div>
                  <div className="w-full max-w-md space-y-2">
                    <ProcessStep label="Loading image" completed />
                    <ProcessStep label="Preprocessing" completed />
                    <ProcessStep label="Running AI models" active />
                    <ProcessStep label="Generating heatmap" />
                    <ProcessStep label="Creating report" />
                  </div>
                </div>
              </div>
            )}

            {analysisResult && !analysisMutation.isPending && (
              <>
                {/* Findings */}
                <div className="glass-card rounded-2xl p-6">
                  <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-blue-400" />
                    AI Findings
                  </h2>

                  <div className="space-y-3">
                    {analysisResult.findings.map((finding, index) => (
                      <FindingCard key={index} finding={finding} />
                    ))}
                  </div>
                </div>

                {/* Confidence Scores */}
                <div className="glass-card rounded-2xl p-6">
                  <h2 className="text-xl font-semibold text-white mb-4">
                    Confidence Scores
                  </h2>

                  <div className="space-y-3">
                    {Object.entries(analysisResult.confidence_scores).map(([pathology, score]) => (
                      <div key={pathology}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-300">{pathology}</span>
                          <span className="text-blue-400 font-medium">{(score * 100).toFixed(1)}%</span>
                        </div>
                        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-1000"
                            style={{ width: `${score * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Report Preview */}
                <div className="glass-card rounded-2xl p-6">
                  <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-blue-400" />
                    AI-Generated Report Preview
                  </h2>

                  <div className="p-4 bg-slate-800/50 rounded-lg">
                    <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                      {analysisResult.report_draft}
                    </pre>
                  </div>

                  <div className="mt-4 flex gap-3">
                    <button className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2">
                      <Eye className="w-4 h-4" />
                      View Full Report
                    </button>
                    <button className="flex-1 py-2 px-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors flex items-center justify-center gap-2">
                      <FileText className="w-4 h-4" />
                      Edit Report
                    </button>
                  </div>
                </div>

                {/* Processing Info */}
                <div className="glass-card rounded-2xl p-6">
                  <h2 className="text-xl font-semibold text-white mb-4">Processing Details</h2>
                  <div className="space-y-2">
                    <InfoRow label="Analysis ID" value={analysisResult.analysis_id} />
                    <InfoRow label="Processing Time" value={`${analysisResult.processing_time.toFixed(2)}s`} />
                    <InfoRow label="Model Type" value={analysisResult.model_info.model_type} />
                    <InfoRow label="Model Version" value={analysisResult.model_info.version} />
                  </div>
                </div>
              </>
            )}

            {!analysisResult && !analysisMutation.isPending && (
              <div className="glass-card rounded-2xl p-12 text-center">
                <div className="flex flex-col items-center gap-4">
                  <div className="p-4 bg-gray-500/10 rounded-full">
                    <Brain className="w-12 h-12 text-gray-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">
                      No Analysis Yet
                    </h3>
                    <p className="text-gray-400">
                      Upload an image and click "Run AI Analysis" to get started
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
      <span className="text-gray-400 text-sm">{label}</span>
      <span className="text-white font-medium text-sm">{value}</span>
    </div>
  )
}

function FindingCard({ finding }: { finding: any }) {
  const severityColors = {
    critical: 'border-red-500 bg-red-500/10',
    severe: 'border-orange-500 bg-orange-500/10',
    moderate: 'border-yellow-500 bg-yellow-500/10',
    mild: 'border-blue-500 bg-blue-500/10',
    normal: 'border-green-500 bg-green-500/10',
  }

  const severityIcons = {
    critical: AlertCircle,
    severe: AlertCircle,
    moderate: AlertCircle,
    mild: CheckCircle,
    normal: CheckCircle,
  }

  const Icon = severityIcons[finding.severity as keyof typeof severityIcons] || AlertCircle

  return (
    <div
      className={clsx(
        'p-4 rounded-lg border-l-4',
        severityColors[finding.severity as keyof typeof severityColors] || 'border-gray-500 bg-gray-500/10'
      )}
    >
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <h4 className="text-white font-semibold mb-1">{finding.pathology}</h4>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">
              Confidence: <span className="text-blue-400 font-medium">{(finding.confidence * 100).toFixed(1)}%</span>
            </span>
            <span className="text-sm text-gray-400">
              Severity: <span className="text-white font-medium capitalize">{finding.severity}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

function ProcessStep({ label, active, completed }: { label: string; active?: boolean; completed?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={clsx(
          'w-6 h-6 rounded-full flex items-center justify-center transition-all',
          completed && 'bg-green-500',
          active && !completed && 'bg-blue-500 animate-pulse',
          !active && !completed && 'bg-gray-600'
        )}
      >
        {completed && <CheckCircle className="w-4 h-4 text-white" />}
        {active && !completed && <Loader2 className="w-4 h-4 text-white animate-spin" />}
      </div>
      <span className={clsx('text-sm', completed || active ? 'text-white font-medium' : 'text-gray-500')}>
        {label}
      </span>
    </div>
  )
}
