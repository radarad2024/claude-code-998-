import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Brain,
  Heart,
  Bone,
  Users,
  FileText,
  Clock,
  Target,
  AlertCircle,
  CheckCircle,
} from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'

export default function AnalyticsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      // Mock data - replace with actual API call
      return {
        overview: {
          total_analyses: 1247,
          total_reports: 1089,
          accuracy_rate: 0.96,
          avg_processing_time: 2.5,
        },
        dailyVolume: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          }),
          analyses: Math.floor(40 + Math.random() * 20 + i * 0.5),
          reports: Math.floor(35 + Math.random() * 15 + i * 0.4),
        })),
        pathologyDistribution: [
          { name: 'Normal', value: 1234, color: '#10b981' },
          { name: 'Pneumonia', value: 387, color: '#3b82f6' },
          { name: 'Fracture', value: 234, color: '#f59e0b' },
          { name: 'Mass', value: 156, color: '#ef4444' },
          { name: 'Hemorrhage', value: 76, color: '#8b5cf6' },
          { name: 'Others', value: 334, color: '#6b7280' },
        ],
        modalityUsage: [
          { modality: 'X-Ray', count: 687, percentage: 55 },
          { modality: 'CT', count: 342, percentage: 27 },
          { modality: 'MRI', count: 156, percentage: 13 },
          { modality: 'Ultrasound', count: 62, percentage: 5 },
        ],
        performanceMetrics: {
          accuracy: 96,
          sensitivity: 94,
          specificity: 92,
          precision: 93,
          f1Score: 93.5,
          auc: 96,
        },
        turnaroundTime: [
          { range: '0-5 min', count: 234 },
          { range: '5-10 min', count: 456 },
          { range: '10-15 min', count: 342 },
          { range: '15-20 min', count: 156 },
          { range: '20+ min', count: 59 },
        ],
        topPathologies: [
          { name: 'Pneumonia', detected: 387, accuracy: 97 },
          { name: 'Fracture', detected: 234, accuracy: 93 },
          { name: 'Mass/Nodule', detected: 156, accuracy: 91 },
          { name: 'Pleural Effusion', detected: 145, accuracy: 94 },
          { name: 'Cardiomegaly', detected: 123, accuracy: 92 },
        ],
      }
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <div className="p-3 bg-purple-600 rounded-xl">
                <Activity className="w-8 h-8" />
              </div>
              Advanced Analytics
            </h1>
            <p className="text-gray-300 text-lg">
              Comprehensive insights and performance metrics
            </p>
          </div>

          <select className="px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white">
            <option>Last 30 Days</option>
            <option>Last 90 Days</option>
            <option>Last Year</option>
            <option>All Time</option>
          </select>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            title="Total Analyses"
            value={analytics?.overview.total_analyses.toLocaleString()}
            change="+12.5%"
            trend="up"
            icon={<Brain className="w-6 h-6" />}
            color="blue"
          />
          <KPICard
            title="Total Reports"
            value={analytics?.overview.total_reports.toLocaleString()}
            change="+8.3%"
            trend="up"
            icon={<FileText className="w-6 h-6" />}
            color="green"
          />
          <KPICard
            title="AI Accuracy"
            value={`${(analytics?.overview.accuracy_rate * 100).toFixed(1)}%`}
            change="+2.1%"
            trend="up"
            icon={<Target className="w-6 h-6" />}
            color="purple"
          />
          <KPICard
            title="Avg Processing Time"
            value={`${analytics?.overview.avg_processing_time}s`}
            change="-15%"
            trend="down"
            icon={<Clock className="w-6 h-6" />}
            color="orange"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily Volume Trend */}
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Daily Analysis Volume</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={analytics?.dailyVolume}>
                <defs>
                  <linearGradient id="colorAnalyses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorReports" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="analyses"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#colorAnalyses)"
                />
                <Area
                  type="monotone"
                  dataKey="reports"
                  stroke="#10b981"
                  fillOpacity={1}
                  fill="url(#colorReports)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Pathology Distribution */}
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Pathology Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analytics?.pathologyDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderCustomLabel}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {analytics?.pathologyDistribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 gap-2">
              {analytics?.pathologyDistribution.map((item: any) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm text-gray-300">{item.name}</span>
                  <span className="text-sm text-gray-500">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Modality Usage */}
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Modality Usage</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics?.modalityUsage}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="modality" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* AI Performance Radar */}
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">AI Performance Metrics</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart
                cx="50%"
                cy="50%"
                outerRadius="80%"
                data={[
                  { subject: 'Accuracy', value: analytics?.performanceMetrics.accuracy },
                  { subject: 'Sensitivity', value: analytics?.performanceMetrics.sensitivity },
                  { subject: 'Specificity', value: analytics?.performanceMetrics.specificity },
                  { subject: 'Precision', value: analytics?.performanceMetrics.precision },
                  { subject: 'F1 Score', value: analytics?.performanceMetrics.f1Score },
                  { subject: 'AUC', value: analytics?.performanceMetrics.auc },
                ]}
              >
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={12} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#94a3b8" fontSize={10} />
                <Radar
                  name="Performance"
                  dataKey="value"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.6}
                />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Turnaround Time Distribution */}
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Turnaround Time Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics?.turnaroundTime} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#94a3b8" fontSize={12} />
                <YAxis type="category" dataKey="range" stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="count" fill="#10b981" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Top Pathologies Table */}
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Top Detected Pathologies</h3>
            <div className="space-y-4">
              {analytics?.topPathologies.map((pathology: any, index: number) => (
                <div key={pathology.name} className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between mb-1">
                      <span className="text-white font-medium">{pathology.name}</span>
                      <span className="text-gray-400 text-sm">{pathology.detected} cases</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                          style={{ width: `${pathology.accuracy}%` }}
                        />
                      </div>
                      <span className="text-sm text-blue-400 font-medium">{pathology.accuracy}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Performance Breakdown */}
        <div className="glass-card rounded-2xl p-6">
          <h3 className="text-2xl font-semibold text-white mb-6">Detailed Performance Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            <MetricCard label="Accuracy" value={`${analytics?.performanceMetrics.accuracy}%`} />
            <MetricCard label="Sensitivity" value={`${analytics?.performanceMetrics.sensitivity}%`} />
            <MetricCard label="Specificity" value={`${analytics?.performanceMetrics.specificity}%`} />
            <MetricCard label="Precision" value={`${analytics?.performanceMetrics.precision}%`} />
            <MetricCard label="F1 Score" value={`${analytics?.performanceMetrics.f1Score}%`} />
            <MetricCard label="AUC" value={`${analytics?.performanceMetrics.auc}%`} />
          </div>
        </div>
      </div>
    </div>
  )
}

function KPICard({ title, value, change, trend, icon, color }: any) {
  const colors = {
    blue: 'bg-blue-500/10 text-blue-500',
    green: 'bg-green-500/10 text-green-500',
    purple: 'bg-purple-500/10 text-purple-500',
    orange: 'bg-orange-500/10 text-orange-500',
  }

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colors[color as keyof typeof colors]}`}>{icon}</div>
        <div
          className={`flex items-center gap-1 text-sm font-medium ${
            trend === 'up' ? 'text-green-400' : 'text-orange-400'
          }`}
        >
          {trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          {change}
        </div>
      </div>
      <h3 className="text-gray-400 text-sm font-medium mb-1">{title}</h3>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-4 bg-slate-800/50 rounded-lg">
      <p className="text-gray-400 text-sm mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  )
}

function renderCustomLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * (Math.PI / 180))
  const y = cy + radius * Math.sin(-midAngle * (Math.PI / 180))

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
      fontSize={12}
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}
