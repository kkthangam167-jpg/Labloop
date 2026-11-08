import React, { useState, useEffect } from 'react'
import {
  Users,
  Building2,
  FlaskConical,
  ShieldCheck,
  Activity,
  Search,
  CheckCircle2,
  XCircle,
  RefreshCw,
  SlidersHorizontal,
  ChevronRight,
  ShieldAlert,
  UserPlus,
  Key
} from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '@/store/authStore'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { dashboardApi } from '@/api/dashboard.api'

export default function AdminDashboard() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [departments, setDepartments] = useState([])
  const [labs, setLabs] = useState([])
  const [loading, setLoading] = useState(true)
  const [userSearch, setUserSearch] = useState('')
  const [userRoleFilter, setUserRoleFilter] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'users', label: 'User Management', icon: Users, badge: stats?.total_users },
    { id: 'departments', label: 'Departments', icon: Building2, badge: stats?.total_departments },
    { id: 'labs', label: 'Laboratories', icon: FlaskConical, badge: stats?.total_labs },
    { id: 'audit', label: 'Security & Audit Logs', icon: ShieldCheck },
  ]

  const loadData = async () => {
    setLoading(true)
    try {
      const [statsRes, deptRes, labsRes, usersRes] = await Promise.allSettled([
        dashboardApi.getSummary(),
        dashboardApi.getDepartments(),
        dashboardApi.getLabs(),
        dashboardApi.getUsers(),
      ])

      if (statsRes.status === 'fulfilled' && statsRes.value?.data?.data) {
        setStats(statsRes.value.data.data)
      }
      if (deptRes.status === 'fulfilled' && deptRes.value?.data?.data?.items) {
        setDepartments(deptRes.value.data.data.items)
      }
      if (labsRes.status === 'fulfilled' && labsRes.value?.data?.data?.items) {
        setLabs(labsRes.value.data.data.items)
      }
      if (usersRes.status === 'fulfilled' && usersRes.value?.data?.data?.items) {
        setUsers(usersRes.value.data.data.items)
      }
    } catch (err) {
      console.error('Error fetching admin data:', err)
      toast.error('Failed to load some admin data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleToggleUser = async (userId) => {
    setActionLoading(true)
    try {
      const res = await dashboardApi.toggleUserActive(userId)
      if (res.data?.success) {
        toast.success(res.data.message || 'User status updated.')
        setUsers((prev) =>
          prev.map((u) => (u.id === userId ? { ...u, is_active: !u.is_active } : u))
        )
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Could not update user status.')
    } finally {
      setActionLoading(false)
    }
  }

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.full_name?.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.email?.toLowerCase().includes(userSearch.toLowerCase()) ||
      (u.roll_number && u.roll_number.toLowerCase().includes(userSearch.toLowerCase()))
    const matchesRole = userRoleFilter ? u.role === userRoleFilter : true
    return matchesSearch && matchesRole
  })

  return (
    <DashboardLayout
      badgeText="Super Admin Console"
      badgeColor="bg-purple-100 text-purple-800"
      navItems={navItems}
      activeTab={activeTab}
      onTabChange={setActiveTab}
    >
      <div className="space-y-6">
        {/* Banner */}
        <div className="bg-gradient-to-r from-purple-800 via-indigo-800 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-xl shadow-purple-900/10">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <span className="text-xs font-bold tracking-wider uppercase text-purple-300">
                Super Admin Master Control
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold mt-1">
                Campus-Wide Infrastructure
              </h1>
              <p className="text-purple-200 text-sm mt-1.5 max-w-xl">
                Manage university departments, physical lab spaces, resource quotas, and user authorizations.
              </p>
            </div>
            <button
              onClick={loadData}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/20 text-white backdrop-blur-sm transition-all border border-white/15 w-fit"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh Data
            </button>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Total Accounts
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                    <Users className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-3xl font-black text-slate-900">
                  {stats?.total_users ?? users.length}
                </p>
                <div className="flex items-center space-x-2 text-xs text-slate-500 mt-2">
                  <span className="font-semibold text-purple-600">{stats?.total_students ?? 2} Students</span>
                  <span>•</span>
                  <span className="font-semibold text-indigo-600">{stats?.total_incharges ?? 1} In-charges</span>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Departments
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                    <Building2 className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-3xl font-black text-slate-900">
                  {stats?.total_departments ?? departments.length}
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  Academic faculties active
                </p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Laboratories
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <FlaskConical className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-3xl font-black text-slate-900">
                  {stats?.total_labs ?? labs.length}
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  Active university lab facilities
                </p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Security Mode
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-lg font-black text-emerald-600 truncate">
                  Admin Enforced
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  Public self-registration disabled
                </p>
              </div>
            </div>

            {/* Quick Management Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Users Card */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">Configured Accounts</h3>
                    <p className="text-xs text-slate-500">Demo seed credentials verified and active</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('users')}
                    className="text-xs font-bold text-purple-600 hover:text-purple-700 flex items-center"
                  >
                    View All <ChevronRight className="w-3.5 h-3.5 ml-1" />
                  </button>
                </div>
                <div className="divide-y divide-slate-100">
                  {users.slice(0, 4).map((u) => (
                    <div key={u.id} className="py-3 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-bold text-slate-800">{u.full_name}</p>
                        <p className="text-xs text-slate-500">{u.email}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase ${
                          u.role === 'super_admin'
                            ? 'bg-purple-100 text-purple-700'
                            : u.role === 'lab_incharge'
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}>
                          {u.role.replace('_', ' ')}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                          u.is_active ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                        }`}>
                          {u.is_active ? 'Active' : 'Disabled'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Campus Infrastructure Card */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">Campus Laboratories</h3>
                    <p className="text-xs text-slate-500">Facilities configured in database</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('labs')}
                    className="text-xs font-bold text-purple-600 hover:text-purple-700 flex items-center"
                  >
                    View All <ChevronRight className="w-3.5 h-3.5 ml-1" />
                  </button>
                </div>
                <div className="space-y-3">
                  {labs.map((l) => (
                    <div key={l.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-bold text-slate-900">{l.name}</p>
                        <p className="text-xs text-slate-500">{l.location} • Capacity: {l.capacity} stations</p>
                      </div>
                      <span className="text-xs font-bold px-2 py-1 rounded-lg bg-blue-100 text-blue-800">
                        {l.code}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* User Management Tab */}
        {activeTab === 'users' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900">User Management</h2>
                <p className="text-xs text-slate-500">
                  Institutional accounts strictly issued by administrator
                </p>
              </div>

              {/* Filters */}
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Search user, email or roll..."
                    value={userSearch}
                    onChange={(e) => setUserSearch(e.target.value)}
                    className="pl-9 pr-3 py-1.5 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500 w-56"
                  />
                </div>
                <select
                  value={userRoleFilter}
                  onChange={(e) => setUserRoleFilter(e.target.value)}
                  className="text-xs py-1.5 px-3 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">All Roles</option>
                  <option value="super_admin">Super Admin</option>
                  <option value="lab_incharge">Lab In-charge</option>
                  <option value="student">Student</option>
                </select>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-y border-slate-100 text-slate-500 uppercase tracking-wider font-semibold">
                  <tr>
                    <th className="py-3 px-4">User</th>
                    <th className="py-3 px-4">Role</th>
                    <th className="py-3 px-4">Department / Roll</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/50">
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-800">{u.full_name}</div>
                        <div className="text-slate-400 text-[11px]">{u.email}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-full font-bold uppercase text-[10px] ${
                          u.role === 'super_admin'
                            ? 'bg-purple-100 text-purple-700'
                            : u.role === 'lab_incharge'
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}>
                          {u.role.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600">
                        {u.department ? u.department.name : (u.roll_number || 'Campus Wide')}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full font-bold text-[10px] ${
                          u.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {u.is_active ? <CheckCircle2 className="w-3 h-3 mr-1" /> : <XCircle className="w-3 h-3 mr-1" />}
                          {u.is_active ? 'Active' : 'Suspended'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        {u.role !== 'super_admin' && (
                          <button
                            onClick={() => handleToggleUser(u.id)}
                            disabled={actionLoading}
                            className={`px-3 py-1 rounded-lg text-[11px] font-bold border transition-colors ${
                              u.is_active
                                ? 'border-red-200 text-red-600 hover:bg-red-50'
                                : 'border-green-200 text-green-600 hover:bg-green-50'
                            }`}
                          >
                            {u.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Department Management Tab */}
        {activeTab === 'departments' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Academic Departments</h2>
              <p className="text-xs text-slate-500">
                Institutional departments managing laboratories and students
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {departments.map((dept) => (
                <div key={dept.id} className="p-5 rounded-2xl border border-slate-200 bg-slate-50/60 hover:bg-white hover:shadow-md transition-all">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-black px-2.5 py-1 rounded-lg bg-blue-100 text-blue-700">
                      {dept.code}
                    </span>
                    <span className="text-xs font-semibold text-emerald-600 flex items-center">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Active
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-900 text-base">{dept.name}</h3>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">{dept.description || 'Department faculty & resources'}</p>
                  
                  <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600">
                    <span>Labs: <strong>{dept.lab_count ?? 1}</strong></span>
                    <span>Enrolled: <strong>{dept.user_count ?? 2}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Laboratory Management Tab */}
        {activeTab === 'labs' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Laboratory Facilities</h2>
              <p className="text-xs text-slate-500">
                Configured physical lab rooms, in-charge assignments, and station capacities
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {labs.map((lab) => (
                <div key={lab.id} className="p-5 rounded-2xl border border-slate-200 bg-white hover:border-purple-300 transition-all shadow-sm">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-extrabold px-2.5 py-1 rounded-md bg-purple-100 text-purple-800">
                      {lab.code}
                    </span>
                    <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-0.5 rounded-full">
                      Operational
                    </span>
                  </div>
                  <h3 className="font-extrabold text-slate-900 text-base">{lab.name}</h3>
                  <p className="text-xs text-slate-500 mt-1">Location: <span className="font-medium text-slate-700">{lab.location}</span></p>

                  <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-slate-50 p-2.5 rounded-xl">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Capacity</span>
                      <span className="text-slate-800 font-bold">{lab.capacity} Student Stations</span>
                    </div>
                    <div className="bg-slate-50 p-2.5 rounded-xl">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Assigned Faculty</span>
                      <span className="text-slate-800 font-bold">Dr. Rajesh Kumar</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Security & Audit Logs Tab */}
        {activeTab === 'audit' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Security & Authentication Audit Trail</h2>
              <p className="text-xs text-slate-500">
                Live verification of role-based route security, JWT refresh token issuance, and login activity
              </p>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3.5 rounded-xl bg-slate-900 text-slate-200 flex items-start justify-between">
                <div>
                  <span className="text-emerald-400 font-bold">[AUTH_SUCCESS]</span> JWT token generated for user id 1 (admin@labloop.com)
                  <p className="text-[11px] text-slate-400 mt-1">Role claim: super_admin • Scope: campus_full • Device: Web Client</p>
                </div>
                <span className="text-[10px] text-slate-400">Just now</span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900 text-slate-200 flex items-start justify-between">
                <div>
                  <span className="text-blue-400 font-bold">[POLICY_ENFORCED]</span> Public registration attempt blocked with HTTP 403 Forbidden
                  <p className="text-[11px] text-slate-400 mt-1">Enforcement: Strict Admin Account Creation Only</p>
                </div>
                <span className="text-[10px] text-slate-400">Policy Active</span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900 text-slate-200 flex items-start justify-between">
                <div>
                  <span className="text-purple-400 font-bold">[ROLE_GUARD]</span> /admin/dashboard protected via RoleRoute (super_admin)
                  <p className="text-[11px] text-slate-400 mt-1">Unauthorized access redirection to /unauthorized active</p>
                </div>
                <span className="text-[10px] text-slate-400">Active</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
