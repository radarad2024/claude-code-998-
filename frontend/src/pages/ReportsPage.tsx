import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileText, Plus, Search, Download, Eye, Edit, Trash2, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import clsx from 'clsx'

interface Report {
  id: string
  patient_name: string
  patient_mrn: string
  study_type: string
  study_date: string
  status: 'draft' | 'finalized' | 'pending'
  findings: string
  created_at: string
  radiologist: string
}

export default function ReportsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)

  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports', searchQuery, filterStatus],
    queryFn: async () => {
      // Mock data
      return [
        {
          id: '1',
          patient_name: 'John Doe',
          patient_mrn: 'MRN-001234',
          study_type: 'Chest X-Ray',
          study_date: '2024-11-18',
          status: 'finalized' as const,
          findings: 'Clear lung fields. Normal cardiac silhouette. No acute abnormalities.',
          created_at: '2024-11-18T10:30:00',
          radiologist: 'Dr. Smith',
        },
        {
          id: '2',
          patient_name: 'Jane Smith',
          patient_mrn: 'MRN-001235',
          study_type: 'Brain CT',
          study_date: '2024-11-17',
          status: 'draft' as const,
          findings: 'No acute intracranial abnormality. Normal brain parenchyma.',
          created_at: '2024-11-17T14:20:00',
          radiologist: 'Dr. Johnson',
        },
        {
          id: '3',
          patient_name: 'Robert Johnson',
          patient_mrn: 'MRN-001236',
          study_type: 'Spine X-Ray',
          study_date: '2024-11-16',
          status: 'pending' as const,
          findings: 'AI analysis in progress...',
          created_at: '2024-11-16T09:15:00',
          radiologist: 'Dr. Williams',
        },
      ].filter((r) => {
        const matchesSearch =
          searchQuery === '' ||
          r.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.patient_mrn.toLowerCase().includes(searchQuery.toLowerCase())
        const matchesStatus = filterStatus === 'all' || r.status === filterStatus
        return matchesSearch && matchesStatus
      })
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
              <div className="p-3 bg-orange-600 rounded-xl">
                <FileText className="w-8 h-8" />
              </div>
              Radiology Reports
            </h1>
            <p className="text-gray-300 text-lg">AI-assisted report generation and management</p>
          </div>

          <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white font-semibold rounded-lg transition-all btn-hover-lift">
            <Plus className="w-5 h-5" />
            New Report
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-blue-500/10 text-blue-500">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Total Reports</p>
                <p className="text-3xl font-bold text-white">{reports?.length || 0}</p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-green-500/10 text-green-500">
                <CheckCircle className="w-6 h-6" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Finalized</p>
                <p className="text-3xl font-bold text-white">
                  {reports?.filter((r) => r.status === 'finalized').length || 0}
                </p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-yellow-500/10 text-yellow-500">
                <Edit className="w-6 h-6" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Drafts</p>
                <p className="text-3xl font-bold text-white">
                  {reports?.filter((r) => r.status === 'draft').length || 0}
                </p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-orange-500/10 text-orange-500">
                <Clock className="w-6 h-6" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Pending</p>
                <p className="text-3xl font-bold text-white">
                  {reports?.filter((r) => r.status === 'pending').length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="glass-card rounded-2xl p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by patient name or MRN..."
                className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="draft">Draft</option>
              <option value="finalized">Finalized</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>

        {/* Reports List */}
        <div className="grid grid-cols-1 gap-4">
          {reports?.map((report) => (
            <div key={report.id} className="glass-card rounded-2xl p-6 hover:bg-slate-800/30 transition-all cursor-pointer"
                 onClick={() => setSelectedReport(report)}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-white">{report.patient_name}</h3>
                    <span className="text-sm text-gray-400">({report.patient_mrn})</span>
                    <StatusBadge status={report.status} />
                  </div>

                  <div className="flex items-center gap-6 text-sm text-gray-400 mb-3">
                    <span>{report.study_type}</span>
                    <span>{new Date(report.study_date).toLocaleDateString()}</span>
                    <span>{report.radiologist}</span>
                  </div>

                  <p className="text-gray-300 line-clamp-2">{report.findings}</p>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  <button className="p-2 hover:bg-blue-500/20 text-blue-400 rounded-lg transition-colors" title="View">
                    <Eye className="w-5 h-5" />
                  </button>
                  <button className="p-2 hover:bg-green-500/20 text-green-400 rounded-lg transition-colors" title="Edit">
                    <Edit className="w-5 h-5" />
                  </button>
                  <button className="p-2 hover:bg-purple-500/20 text-purple-400 rounded-lg transition-colors" title="Download">
                    <Download className="w-5 h-5" />
                  </button>
                  <button className="p-2 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors" title="Delete">
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {reports?.length === 0 && (
          <div className="glass-card rounded-2xl p-12 text-center">
            <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No reports found</p>
            <p className="text-gray-500 text-sm">Try adjusting your search criteria</p>
          </div>
        )}
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const styles = {
    draft: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    finalized: 'bg-green-500/20 text-green-400 border-green-500/50',
    pending: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
  }

  const icons = {
    draft: Edit,
    finalized: CheckCircle,
    pending: Clock,
  }

  const Icon = icons[status as keyof typeof icons]

  return (
    <span className={clsx('flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border', styles[status as keyof typeof styles])}>
      <Icon className="w-3 h-3" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}
