import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Users,
  Plus,
  Search,
  Edit,
  Trash2,
  Eye,
  FileText,
  Calendar,
  Phone,
  Mail,
  MapPin,
  Activity,
  Filter,
  Download,
  Upload,
} from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'
import clsx from 'clsx'

interface Patient {
  id: string
  patient_id: string
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  phone: string
  email: string
  address: string
  total_studies: number
  last_visit: string
}

export default function PatientsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)
  const [filterGender, setFilterGender] = useState<string>('all')

  const queryClient = useQueryClient()

  // Mock data - replace with actual API
  const { data: patients, isLoading } = useQuery({
    queryKey: ['patients', searchQuery, filterGender],
    queryFn: async () => {
      // Mock patients
      return [
        {
          id: '1',
          patient_id: 'MRN-001234',
          first_name: 'John',
          last_name: 'Doe',
          date_of_birth: '1980-05-15',
          gender: 'M',
          phone: '+1-555-0100',
          email: 'john.doe@email.com',
          address: '123 Main St, New York, NY 10001',
          total_studies: 12,
          last_visit: '2024-11-15',
        },
        {
          id: '2',
          patient_id: 'MRN-001235',
          first_name: 'Jane',
          last_name: 'Smith',
          date_of_birth: '1975-08-22',
          gender: 'F',
          phone: '+1-555-0101',
          email: 'jane.smith@email.com',
          address: '456 Oak Ave, Los Angeles, CA 90001',
          total_studies: 8,
          last_visit: '2024-11-18',
        },
        {
          id: '3',
          patient_id: 'MRN-001236',
          first_name: 'Robert',
          last_name: 'Johnson',
          date_of_birth: '1990-03-10',
          gender: 'M',
          phone: '+1-555-0102',
          email: 'robert.j@email.com',
          address: '789 Pine Rd, Chicago, IL 60601',
          total_studies: 5,
          last_visit: '2024-11-10',
        },
      ].filter((p) => {
        const matchesSearch =
          searchQuery === '' ||
          p.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.patient_id.toLowerCase().includes(searchQuery.toLowerCase())
        const matchesGender = filterGender === 'all' || p.gender === filterGender
        return matchesSearch && matchesGender
      })
    },
  })

  const deletePatient = useMutation({
    mutationFn: async (patientId: string) => {
      // Mock delete
      await new Promise((resolve) => setTimeout(resolve, 500))
      return patientId
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] })
      toast.success('Patient deleted successfully')
    },
  })

  const calculateAge = (dob: string) => {
    const birthDate = new Date(dob)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    return age
  }

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
              <div className="p-3 bg-green-600 rounded-xl">
                <Users className="w-8 h-8" />
              </div>
              Patient Management
            </h1>
            <p className="text-gray-300 text-lg">Manage patient records and medical history</p>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold rounded-lg transition-all btn-hover-lift"
          >
            <Plus className="w-5 h-5" />
            Add Patient
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatsCard
            title="Total Patients"
            value={patients?.length || 0}
            icon={<Users className="w-6 h-6" />}
            color="blue"
          />
          <StatsCard
            title="Active Today"
            value="12"
            icon={<Activity className="w-6 h-6" />}
            color="green"
          />
          <StatsCard
            title="Pending Studies"
            value="8"
            icon={<FileText className="w-6 h-6" />}
            color="orange"
          />
          <StatsCard
            title="This Month"
            value="47"
            icon={<Calendar className="w-6 h-6" />}
            color="purple"
          />
        </div>

        {/* Search and Filters */}
        <div className="glass-card rounded-2xl p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name or MRN..."
                className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <select
              value={filterGender}
              onChange={(e) => setFilterGender(e.target.value)}
              className="px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Genders</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        {/* Patients Table */}
        <div className="glass-card rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-800/50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">MRN</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Patient Name</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Age/Gender</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Contact</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Studies</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Last Visit</th>
                  <th className="px-6 py-4 text-right text-sm font-semibold text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {patients?.map((patient) => (
                  <tr
                    key={patient.id}
                    className="hover:bg-slate-800/30 transition-colors cursor-pointer"
                    onClick={() => setSelectedPatient(patient)}
                  >
                    <td className="px-6 py-4">
                      <span className="text-blue-400 font-mono text-sm">{patient.patient_id}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                          {patient.first_name[0]}
                          {patient.last_name[0]}
                        </div>
                        <div>
                          <p className="text-white font-medium">
                            {patient.first_name} {patient.last_name}
                          </p>
                          <p className="text-sm text-gray-400">{patient.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-white">
                        {calculateAge(patient.date_of_birth)} years
                        <span className="ml-2 text-gray-400">({patient.gender})</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                          <Phone className="w-4 h-4" />
                          {patient.phone}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                          <Mail className="w-4 h-4" />
                          {patient.email}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm font-medium">
                        {patient.total_studies} studies
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-gray-300">
                        <Calendar className="w-4 h-4" />
                        {new Date(patient.last_visit).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedPatient(patient)
                          }}
                          className="p-2 hover:bg-blue-500/20 text-blue-400 rounded-lg transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setShowAddModal(true)
                            setSelectedPatient(patient)
                          }}
                          className="p-2 hover:bg-green-500/20 text-green-400 rounded-lg transition-colors"
                          title="Edit"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            if (confirm('Are you sure you want to delete this patient?')) {
                              deletePatient.mutate(patient.id)
                            }
                          }}
                          className="p-2 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {patients?.length === 0 && (
            <div className="text-center py-12">
              <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No patients found</p>
              <p className="text-gray-500 text-sm">Try adjusting your search criteria</p>
            </div>
          )}
        </div>

        {/* Patient Details Modal */}
        {selectedPatient && !showAddModal && (
          <PatientDetailsModal patient={selectedPatient} onClose={() => setSelectedPatient(null)} />
        )}

        {/* Add/Edit Patient Modal */}
        {showAddModal && (
          <AddPatientModal
            patient={selectedPatient}
            onClose={() => {
              setShowAddModal(false)
              setSelectedPatient(null)
            }}
          />
        )}
      </div>
    </div>
  )
}

function StatsCard({ title, value, icon, color }: any) {
  const colors = {
    blue: 'bg-blue-500/10 text-blue-500',
    green: 'bg-green-500/10 text-green-500',
    orange: 'bg-orange-500/10 text-orange-500',
    purple: 'bg-purple-500/10 text-purple-500',
  }

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-lg ${colors[color as keyof typeof colors]}`}>{icon}</div>
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
        </div>
      </div>
    </div>
  )
}

function PatientDetailsModal({ patient, onClose }: { patient: Patient; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-card rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">Patient Details</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Patient Info */}
          <div className="grid grid-cols-2 gap-6">
            <InfoField label="MRN" value={patient.patient_id} />
            <InfoField label="Full Name" value={`${patient.first_name} ${patient.last_name}`} />
            <InfoField label="Date of Birth" value={patient.date_of_birth} />
            <InfoField label="Gender" value={patient.gender === 'M' ? 'Male' : 'Female'} />
            <InfoField label="Phone" value={patient.phone} />
            <InfoField label="Email" value={patient.email} />
            <InfoField label="Address" value={patient.address} className="col-span-2" />
          </div>

          {/* Studies Section */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Recent Studies</h3>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 bg-slate-800/50 rounded-lg flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">Chest X-Ray</p>
                    <p className="text-sm text-gray-400">2024-11-{15 - i}</p>
                  </div>
                  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                    View Results
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function AddPatientModal({ patient, onClose }: { patient: Patient | null; onClose: () => void }) {
  const [formData, setFormData] = useState({
    first_name: patient?.first_name || '',
    last_name: patient?.last_name || '',
    date_of_birth: patient?.date_of_birth || '',
    gender: patient?.gender || 'M',
    phone: patient?.phone || '',
    email: patient?.email || '',
    address: patient?.address || '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    toast.success(patient ? 'Patient updated successfully' : 'Patient added successfully')
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-card rounded-2xl max-w-2xl w-full">
        <div className="p-6 border-b border-slate-700">
          <h2 className="text-2xl font-bold text-white">
            {patient ? 'Edit Patient' : 'Add New Patient'}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">First Name</label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Last Name</label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Date of Birth</label>
              <input
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Gender</label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white"
              >
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Phone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white"
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Address</label>
            <textarea
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white"
              rows={3}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              className="flex-1 py-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold rounded-lg transition-all"
            >
              {patient ? 'Update Patient' : 'Add Patient'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-all"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function InfoField({ label, value, className = '' }: { label: string; value: string; className?: string }) {
  return (
    <div className={className}>
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className="text-white font-medium">{value}</p>
    </div>
  )
}
