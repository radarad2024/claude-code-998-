import { useQuery } from '@tanstack/react-query'
import { Activity, Users, FileText, TrendingUp, Brain, Heart, Bone } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      // Mock data - replace with actual API call
      return {
        overview: {
          total_analyses: 1247,
          total_reports: 1089,
          total_patients: 856,
          analyses_today: 47,
        },
        recentAnalyses: [
          { date: '2024-01', count: 340 },
          { date: '2024-02', count: 398 },
          { date: '2024-03', count: 423 },
          { date: '2024-04', count: 509 },
        ],
        pathologyDistribution: [
          { name: 'Normal', value: 1234 },
          { name: 'Pneumonia', value: 387 },
          { name: 'Fracture', value: 234 },
          { name: 'Mass', value: 156 },
          { name: 'Others', value: 410 },
        ],
        modalityUsage: [
          { modality: 'X-Ray', count: 687 },
          { modality: 'CT', count: 342 },
          { modality: 'MRI', count: 156 },
          { modality: 'US', count: 62 },
        ],
      }
    },
  })

  const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6']

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">AI Radiologist Assistant Overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Analyses"
          value={stats?.overview.total_analyses}
          icon={<Activity className="w-6 h-6" />}
          color="blue"
          trend="+12%"
        />
        <StatsCard
          title="Total Reports"
          value={stats?.overview.total_reports}
          icon={<FileText className="w-6 h-6" />}
          color="green"
          trend="+8%"
        />
        <StatsCard
          title="Patients"
          value={stats?.overview.total_patients}
          icon={<Users className="w-6 h-6" />}
          color="purple"
          trend="+15%"
        />
        <StatsCard
          title="Today's Analyses"
          value={stats?.overview.analyses_today}
          icon={<TrendingUp className="w-6 h-6" />}
          color="orange"
          trend="Real-time"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Analysis Trend */}
        <div className="glass-card rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Analysis Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats?.recentAnalyses}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Pathology Distribution */}
        <div className="glass-card rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Pathology Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stats?.pathologyDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => entry.name}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {stats?.pathologyDistribution.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Modality Usage */}
        <div className="glass-card rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Modality Usage</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats?.modalityUsage}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="modality" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Quick Actions */}
        <div className="glass-card rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <QuickActionButton
              icon={<Brain className="w-5 h-5" />}
              title="New Analysis"
              description="Upload and analyze medical images"
              onClick={() => {}}
            />
            <QuickActionButton
              icon={<FileText className="w-5 h-5" />}
              title="Generate Report"
              description="Create AI-assisted reports"
              onClick={() => {}}
            />
            <QuickActionButton
              icon={<Users className="w-5 h-5" />}
              title="Manage Patients"
              description="View and manage patient records"
              onClick={() => {}}
            />
            <QuickActionButton
              icon={<TrendingUp className="w-5 h-5" />}
              title="View Analytics"
              description="Detailed statistics and insights"
              onClick={() => {}}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function StatsCard({ title, value, icon, color, trend }: any) {
  const colorClasses = {
    blue: 'bg-blue-500/10 text-blue-500',
    green: 'bg-green-500/10 text-green-500',
    purple: 'bg-purple-500/10 text-purple-500',
    orange: 'bg-orange-500/10 text-orange-500',
  }

  return (
    <div className="glass-card rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
        <span className="text-sm text-green-500">{trend}</span>
      </div>
      <h3 className="text-gray-400 text-sm font-medium mb-1">{title}</h3>
      <p className="text-2xl font-bold text-white">{value?.toLocaleString()}</p>
    </div>
  )
}

function QuickActionButton({ icon, title, description, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-start gap-3 p-4 rounded-lg bg-slate-700/30 hover:bg-slate-700/50 transition-colors text-left"
    >
      <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
        {icon}
      </div>
      <div className="flex-1">
        <h4 className="text-white font-medium mb-1">{title}</h4>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
    </button>
  )
}
