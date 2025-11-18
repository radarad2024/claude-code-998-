import { useState } from 'react'
import { User, Bell, Monitor, Brain, Save, Check } from 'lucide-react'
import clsx from 'clsx'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  // User Profile Settings
  const [displayName, setDisplayName] = useState('Dr. Sarah Johnson')
  const [email, setEmail] = useState('sarah.johnson@hospital.com')
  const [role, setRole] = useState('Senior Radiologist')

  // Notification Settings
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [pushNotifications, setPushNotifications] = useState(true)
  const [analysisComplete, setAnalysisComplete] = useState(true)
  const [newPatient, setNewPatient] = useState(false)

  // Display Settings
  const [theme, setTheme] = useState('dark')
  const [language, setLanguage] = useState('en')
  const [dateFormat, setDateFormat] = useState('MM/DD/YYYY')

  // AI Settings
  const [defaultModel, setDefaultModel] = useState('ensemble')
  const [autoAnalyze, setAutoAnalyze] = useState(false)
  const [confidenceThreshold, setConfidenceThreshold] = useState(75)

  const handleSaveSettings = () => {
    // Simulate saving settings
    toast.success('Settings saved successfully!', {
      icon: '✓',
      style: {
        borderRadius: '10px',
        background: '#1e293b',
        color: '#fff',
        border: '1px solid #334155',
      },
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <div className="p-3 bg-purple-600 rounded-xl">
              <Monitor className="w-8 h-8" />
            </div>
            Settings
          </h1>
          <p className="text-gray-300 text-lg">Configure your application preferences</p>
        </div>

        {/* User Profile */}
        <div className="glass-card rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <User className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-semibold text-white">User Profile</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Display Name
              </label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Senior Radiologist">Senior Radiologist</option>
                <option value="Radiologist">Radiologist</option>
                <option value="Resident">Resident</option>
                <option value="Fellow">Fellow</option>
                <option value="Technician">Technician</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="glass-card rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Bell className="w-6 h-6 text-yellow-400" />
            <h2 className="text-2xl font-semibold text-white">Notifications</h2>
          </div>

          <div className="space-y-4">
            <SettingToggle
              label="Email Notifications"
              description="Receive notifications via email"
              checked={emailNotifications}
              onChange={setEmailNotifications}
            />
            <SettingToggle
              label="Push Notifications"
              description="Receive push notifications in browser"
              checked={pushNotifications}
              onChange={setPushNotifications}
            />
            <SettingToggle
              label="Analysis Complete"
              description="Notify when AI analysis is complete"
              checked={analysisComplete}
              onChange={setAnalysisComplete}
            />
            <SettingToggle
              label="New Patient"
              description="Notify when a new patient is added"
              checked={newPatient}
              onChange={setNewPatient}
            />
          </div>
        </div>

        {/* Display Settings */}
        <div className="glass-card rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Monitor className="w-6 h-6 text-green-400" />
            <h2 className="text-2xl font-semibold text-white">Display</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Theme
              </label>
              <select
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="auto">Auto</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="en">English</option>
                <option value="ko">한국어 (Korean)</option>
                <option value="es">Español (Spanish)</option>
                <option value="fr">Français (French)</option>
                <option value="de">Deutsch (German)</option>
                <option value="ja">日本語 (Japanese)</option>
                <option value="zh">中文 (Chinese)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Date Format
              </label>
              <select
                value={dateFormat}
                onChange={(e) => setDateFormat(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                <option value="DD MMM YYYY">DD MMM YYYY</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI Settings */}
        <div className="glass-card rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Brain className="w-6 h-6 text-purple-400" />
            <h2 className="text-2xl font-semibold text-white">AI Configuration</h2>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Default AI Model
              </label>
              <select
                value={defaultModel}
                onChange={(e) => setDefaultModel(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="ensemble">Ensemble (Recommended)</option>
                <option value="efficientnet">EfficientNet-B7</option>
                <option value="densenet">DenseNet-201</option>
                <option value="resnet">ResNet-152</option>
                <option value="vit">Vision Transformer</option>
              </select>
              <p className="text-sm text-gray-400 mt-2">
                Ensemble combines multiple models for best accuracy
              </p>
            </div>

            <SettingToggle
              label="Auto-Analyze"
              description="Automatically analyze images upon upload"
              checked={autoAnalyze}
              onChange={setAutoAnalyze}
            />

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-300">
                  Confidence Threshold
                </label>
                <span className="text-lg font-semibold text-blue-400">
                  {confidenceThreshold}%
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="100"
                step="5"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>50%</span>
                <span>75%</span>
                <span>100%</span>
              </div>
              <p className="text-sm text-gray-400 mt-2">
                Minimum confidence level to show AI findings
              </p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSaveSettings}
            className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all btn-hover-lift"
          >
            <Save className="w-5 h-5" />
            Save All Settings
          </button>
        </div>
      </div>
    </div>
  )
}

interface SettingToggleProps {
  label: string
  description: string
  checked: boolean
  onChange: (checked: boolean) => void
}

function SettingToggle({ label, description, checked, onChange }: SettingToggleProps) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-700 last:border-0">
      <div className="flex-1">
        <h3 className="text-white font-medium">{label}</h3>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={clsx(
          'relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900',
          checked ? 'bg-blue-600' : 'bg-gray-600'
        )}
      >
        <span
          className={clsx(
            'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
            checked ? 'translate-x-6' : 'translate-x-1'
          )}
        />
      </button>
    </div>
  )
}
