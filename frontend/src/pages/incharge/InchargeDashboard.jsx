import React, { useState, useEffect } from 'react'
import {
  FlaskConical,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Wrench,
  Layers,
  Calendar,
  UserCheck,
  Building,
  RefreshCw,
  Search,
  Filter,
  Check,
  X,
  FileText
} from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '@/store/authStore'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { dashboardApi } from '@/api/dashboard.api'

export default function InchargeDashboard() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  // Demo dynamic booking approval queue
  const [pendingBookings, setPendingBookings] = useState([
    {
      id: 101,
      studentName: 'Priya Sharma',
      rollNumber: 'CS2021001',
      equipment: 'NVIDIA RTX A6000 GPU Workstation #04',
      date: 'Tomorrow, 10:00 AM - 01:00 PM',
      purpose: 'Deep Learning Model Training (Final Year Project)',
      lab: 'Advanced Robotics & AI Lab',
      status: 'pending'
    },
    {
      id: 102,
      studentName: 'Rahul Verma',
      rollNumber: 'EE2021045',
      equipment: 'Keysight Digital Storage Oscilloscope (100MHz)',
      date: 'Nov 12, 02:00 PM - 04:30 PM',
      purpose: 'Power Electronics Inverter Harmonics Lab',
      lab: 'Advanced Robotics & AI Lab',
      status: 'pending'
    }
  ])

  // Equipment status items
  const [equipmentList, setEquipmentList] = useState([
    { id: 1, name: 'GPU Deep Learning Cluster #01-08', serial: 'GPU-SRV-2024', status: 'Operational', units: 8, condition: 'Excellent' },
    { id: 2, name: 'Keysight 4-Channel Oscilloscopes', serial: 'DSO-KYS-400', status: 'Operational', units: 12, condition: 'Good' },
    { id: 3, name: 'Creality Ender-3 Pro 3D Printers', serial: 'PRN-3D-09', status: 'In Use', units: 4, condition: 'Good' },
    { id: 4, name: 'Rohde & Schwarz Spectrum Analyzer', serial: 'RF-SPEC-902', status: 'Under Maintenance', units: 1, condition: 'Calibrating' },
    { id: 5, name: 'Precision Soldering Workstations', serial: 'SLD-STN-15', status: 'Operational', units: 10, condition: 'Good' },
    { id: 6, name: 'ABB Industrial Robotic Arm Trainer', serial: 'ROB-ABB-01', status: 'Needs Inspection', units: 1, condition: 'Firmware Update' }
  ])

  // Damage reports queue
  const [damageReports, setDamageReports] = useState([
    {
      id: 'DMG-882',
      equipment: 'Oscilloscope Probe Channel 2',
      reportedBy: 'Priya Sharma (CS2021001)',
      date: 'Yesterday at 4:15 PM',
      severity: 'Medium',
      description: 'BNC connector pin slightly bent; intermittent signal contact on channel 2.',
      status: 'Under Review'
    },
    {
      id: 'DMG-879',
      equipment: '3D Printer Heated Bed Glass',
      reportedBy: 'Lab Technician',
      date: 'Nov 04, 2026',
      severity: 'Low',
      description: 'Minor filament adhesion scratch on surface glass plate. Still usable with Kapton tape.',
      status: 'Resolved'
    }
  ])

  // Maintenance tasks
  const [maintenanceTasks, setMaintenanceTasks] = useState([
    { id: 'MT-101', title: 'Bi-annual Oscilloscope Calibration', due: 'Nov 15, 2026', assignee: 'Keysight Certified Tech', priority: 'High', completed: false },
    { id: 'MT-102', title: 'GPU Server Heat Sink Dust Purge', due: 'Nov 18, 2026', assignee: 'Internal Staff', priority: 'Medium', completed: false },
    { id: 'MT-103', title: 'Chemical & ESD Safety Grounding Audit', due: 'Nov 20, 2026', assignee: 'Campus Safety Cell', priority: 'High', completed: true },
    { id: 'MT-104', title: 'Firmware Update for Robotic Arm Controller', due: 'Nov 25, 2026', assignee: 'ABB Systems Eng.', priority: 'Low', completed: false }
  ])

  const navItems = [
    { id: 'overview', label: 'Overview', icon: FlaskConical },
    { id: 'labs', label: 'My Assigned Labs', icon: Building, badge: stats?.assigned_labs_count || 1 },
    { id: 'approvals', label: 'Pending Bookings', icon: Clock, badge: pendingBookings.filter(b => b.status === 'pending').length },
    { id: 'equipment', label: 'Equipment Inventory', icon: Layers, badge: equipmentList.length },
    { id: 'damages', label: 'Damage Reports', icon: AlertTriangle, badge: damageReports.filter(d => d.status !== 'Resolved').length },
    { id: 'maintenance', label: 'Maintenance Tasks', icon: Wrench, badge: maintenanceTasks.filter(t => !t.completed).length },
  ]

  const loadData = async () => {
    setLoading(true)
    try {
      const [summaryRes, bookingsRes, equipRes, damageRes, maintRes] = await Promise.allSettled([
        dashboardApi.getSummary(),
        dashboardApi.getBookings(),
        dashboardApi.getEquipment(),
        dashboardApi.getDamageReports(),
        dashboardApi.getMaintenance(),
      ])

      if (summaryRes.status === 'fulfilled' && summaryRes.value.data?.data) {
        setStats(summaryRes.value.data.data)
      }
      if (bookingsRes.status === 'fulfilled' && bookingsRes.value.data?.data) {
        const raw = bookingsRes.value.data.data
        if (Array.isArray(raw) && raw.length > 0) {
          setPendingBookings(
            raw.map((b) => ({
              id: b.id,
              studentName: b.user?.full_name || b.student_name || 'Student',
              rollNumber: b.user?.roll_number || b.user?.email?.split('@')[0] || 'N/A',
              equipment: b.equipment?.name || 'Lab Instrument',
              date: `${b.start_time?.slice(0, 10) || ''} ${b.start_time?.slice(11, 16) || ''} - ${b.end_time?.slice(11, 16) || ''}`,
              purpose: b.purpose || 'Academic laboratory experiment',
              lab: b.equipment?.lab?.name || 'University Lab',
              status: b.status,
            }))
          )
        }
      }
      if (equipRes.status === 'fulfilled' && equipRes.value.data?.data) {
        const raw = equipRes.value.data.data
        if (Array.isArray(raw) && raw.length > 0) {
          setEquipmentList(
            raw.map((e) => ({
              id: e.id,
              name: e.name,
              serial: e.serial_number || e.model_number || `EQ-${e.id}`,
              status: e.status === 'available' ? 'Operational' : e.status === 'in_use' ? 'In Use' : 'Under Maintenance',
              units: e.total_quantity || 1,
              condition: e.condition || 'Good',
            }))
          )
        }
      }
      if (damageRes.status === 'fulfilled' && damageRes.value.data?.data) {
        const raw = damageRes.value.data.data
        if (Array.isArray(raw) && raw.length > 0) {
          setDamageReports(
            raw.map((d) => ({
              id: `DMG-${d.id}`,
              equipment: d.equipment?.name || 'Equipment',
              reportedBy: d.reported_by?.full_name || 'Student',
              date: d.created_at?.slice(0, 10) || 'Recently',
              severity: d.severity || 'Medium',
              description: d.description || '',
              status: d.status === 'resolved' ? 'Resolved' : 'Under Review',
            }))
          )
        }
      }
      if (maintRes.status === 'fulfilled' && maintRes.value.data?.data) {
        const raw = maintRes.value.data.data
        if (Array.isArray(raw) && raw.length > 0) {
          setMaintenanceTasks(
            raw.map((m) => ({
              id: `MT-${m.id}`,
              title: m.title || `Maintenance on ${m.equipment?.name || 'Asset'}`,
              due: m.scheduled_date?.slice(0, 10) || 'Upcoming',
              assignee: m.performed_by?.full_name || 'Lab Technician',
              priority: m.priority || 'Medium',
              completed: m.status === 'completed',
            }))
          )
        }
      }
    } catch (err) {
      console.error('Error fetching incharge summary:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleApprove = async (id) => {
    try {
      await dashboardApi.approveBooking(id)
      setPendingBookings((prev) =>
        prev.map((b) => (b.id === id ? { ...b, status: 'approved' } : b))
      )
      toast.success(`Booking #${id} approved! Notification dispatched to student.`)
    } catch (err) {
      toast.error(err.response?.data?.message || `Failed to approve booking #${id}`)
    }
  }

  const handleReject = async (id) => {
    try {
      await dashboardApi.rejectBooking(id, 'Declined by lab in-charge')
      setPendingBookings((prev) =>
        prev.map((b) => (b.id === id ? { ...b, status: 'rejected' } : b))
      )
      toast.error(`Booking #${id} declined. Student has been notified.`)
    } catch (err) {
      toast.error(err.response?.data?.message || `Failed to decline booking #${id}`)
    }
  }

  const handleResolveDamage = (id) => {
    setDamageReports((prev) =>
      prev.map((d) => (d.id === id ? { ...d, status: 'Resolved' } : d))
    )
    toast.success(`Damage report ${id} marked as resolved.`)
  }

  const handleToggleTask = (id) => {
    setMaintenanceTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    )
  }

  const assignedLab = stats?.assigned_labs?.[0] || {
    name: 'Advanced Robotics & AI Lab',
    code: 'LAB-RAI-01',
    location: 'Tech Block 204',
    capacity: 35,
    department: { name: 'Electrical & Electronics Engineering', code: 'EEE' }
  }

  return (
    <DashboardLayout
      badgeText="Lab In-charge Portal"
      badgeColor="bg-emerald-100 text-emerald-800"
      navItems={navItems}
      activeTab={activeTab}
      onTabChange={setActiveTab}
    >
      <div className="space-y-6">
        {/* Banner */}
        <div className="bg-gradient-to-r from-emerald-700 via-teal-700 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-xl shadow-emerald-900/10">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <span className="text-xs font-bold tracking-wider uppercase text-emerald-300">
                Laboratory Operations & Inventory Console
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold mt-1">
                {assignedLab.name}
              </h1>
              <p className="text-emerald-100 text-sm mt-1.5 max-w-xl">
                Location: {assignedLab.location} • Faculty In-charge: {user?.full_name} • Capacity: {assignedLab.capacity} student stations
              </p>
            </div>
            <button
              onClick={loadData}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/20 text-white backdrop-blur-sm transition-all border border-white/15 w-fit"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Sync Status
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
                    Assigned Labs
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <Building className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-3xl font-black text-slate-900">
                  {stats?.assigned_labs_count || 1}
                </p>
                <p className="text-xs text-slate-500 mt-2 font-medium">
                  {assignedLab.code} ({assignedLab.location})
                </p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Pending Bookings
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                    <Clock className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-3xl font-black text-amber-600">
                  {pendingBookings.filter(b => b.status === 'pending').length}
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  Awaiting in-charge approval
                </p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Equipment Units
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                    <Layers className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-3xl font-black text-slate-900">
                  {equipmentList.reduce((acc, curr) => acc + curr.units, 0)}
                </p>
                <p className="text-xs text-emerald-600 font-semibold mt-2">
                  92% operational condition
                </p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Damage Reports
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-red-50 text-red-600 flex items-center justify-center">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-3xl font-black text-red-600">
                  {damageReports.filter(d => d.status !== 'Resolved').length}
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  Open issues requiring attention
                </p>
              </div>
            </div>

            {/* Quick Actions Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Immediate Bookings Queue */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">Pending Student Bookings</h3>
                    <p className="text-xs text-slate-500">Review slot reservations</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('approvals')}
                    className="text-xs font-bold text-emerald-600 hover:text-emerald-700"
                  >
                    View Queue
                  </button>
                </div>

                <div className="space-y-3">
                  {pendingBookings.slice(0, 2).map((booking) => (
                    <div key={booking.id} className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 flex flex-col justify-between gap-3">
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 text-sm">{booking.studentName}</span>
                          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
                            {booking.rollNumber}
                          </span>
                        </div>
                        <p className="text-xs text-slate-700 font-semibold mt-1">{booking.equipment}</p>
                        <p className="text-[11px] text-slate-500 flex items-center mt-1">
                          <Calendar className="w-3 h-3 mr-1 text-slate-400" /> {booking.date}
                        </p>
                      </div>

                      {booking.status === 'pending' ? (
                        <div className="flex items-center space-x-2 pt-2 border-t border-slate-200">
                          <button
                            onClick={() => handleApprove(booking.id)}
                            className="flex-1 py-1.5 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold flex items-center justify-center transition-colors"
                          >
                            <Check className="w-3.5 h-3.5 mr-1" /> Approve
                          </button>
                          <button
                            onClick={() => handleReject(booking.id)}
                            className="flex-1 py-1.5 px-3 border border-red-200 text-red-600 hover:bg-red-50 rounded-lg text-xs font-bold flex items-center justify-center transition-colors"
                          >
                            <X className="w-3.5 h-3.5 mr-1" /> Reject
                          </button>
                        </div>
                      ) : (
                        <span className={`text-xs font-bold px-3 py-1 rounded-lg text-center ${
                          booking.status === 'approved' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {booking.status.toUpperCase()}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Maintenance & Damage Summary */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">Maintenance & Calibration Schedule</h3>
                    <p className="text-xs text-slate-500">Scheduled checks for active instrumentation</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('maintenance')}
                    className="text-xs font-bold text-emerald-600 hover:text-emerald-700"
                  >
                    View All
                  </button>
                </div>

                <div className="space-y-2.5">
                  {maintenanceTasks.slice(0, 3).map((task) => (
                    <div
                      key={task.id}
                      onClick={() => handleToggleTask(task.id)}
                      className="p-3 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between cursor-pointer hover:bg-slate-100/70 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={task.completed}
                          onChange={() => handleToggleTask(task.id)}
                          className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
                        />
                        <div>
                          <p className={`text-xs font-bold ${task.completed ? 'line-through text-slate-400' : 'text-slate-800'}`}>
                            {task.title}
                          </p>
                          <p className="text-[11px] text-slate-500">Due: {task.due} • {task.assignee}</p>
                        </div>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        task.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-slate-200 text-slate-700'
                      }`}>
                        {task.priority}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Assigned Labs Tab */}
        {activeTab === 'labs' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Assigned Physical Facilities</h2>
              <p className="text-xs text-slate-500">Laboratories delegated under your oversight</p>
            </div>

            <div className="p-6 rounded-2xl border-2 border-emerald-200 bg-emerald-50/20 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>
                  <span className="text-xs font-black px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800">
                    {assignedLab.code}
                  </span>
                  <h3 className="text-xl font-extrabold text-slate-900 mt-2">{assignedLab.name}</h3>
                  <p className="text-xs text-slate-600 mt-1">Department: <strong>Electrical & Electronics Engineering (EEE)</strong></p>
                </div>
                <div className="text-right sm:border-l sm:border-slate-200 sm:pl-6">
                  <span className="text-xs text-slate-500 block uppercase font-bold">Total Capacity</span>
                  <span className="text-2xl font-black text-emerald-700">{assignedLab.capacity} Seats</span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-emerald-100 text-xs">
                <div className="bg-white p-3 rounded-xl border border-emerald-100">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Location</span>
                  <span className="font-bold text-slate-800">{assignedLab.location}</span>
                </div>
                <div className="bg-white p-3 rounded-xl border border-emerald-100">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Operating Hours</span>
                  <span className="font-bold text-slate-800">08:30 AM – 06:00 PM</span>
                </div>
                <div className="bg-white p-3 rounded-xl border border-emerald-100">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Check-in Mode</span>
                  <span className="font-bold text-emerald-600">Dynamic QR + RFID Active</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pending Approvals Tab */}
        {activeTab === 'approvals' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Student Booking Approvals</h2>
              <p className="text-xs text-slate-500">Authorize or decline equipment slot requests from students</p>
            </div>

            <div className="space-y-3">
              {pendingBookings.map((b) => (
                <div key={b.id} className="p-4 rounded-xl border border-slate-200 bg-white flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">{b.studentName}</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700 font-semibold">{b.rollNumber}</span>
                      <span className="text-xs text-slate-400">• {b.lab}</span>
                    </div>
                    <p className="text-xs font-bold text-slate-800">{b.equipment}</p>
                    <p className="text-xs text-slate-500"><strong>Session:</strong> {b.date}</p>
                    <p className="text-xs text-slate-600 italic">" {b.purpose} "</p>
                  </div>

                  <div className="flex items-center space-x-2 flex-shrink-0">
                    {b.status === 'pending' ? (
                      <>
                        <button
                          onClick={() => handleApprove(b.id)}
                          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center shadow-sm"
                        >
                          <Check className="w-3.5 h-3.5 mr-1" /> Approve
                        </button>
                        <button
                          onClick={() => handleReject(b.id)}
                          className="px-4 py-2 border border-red-200 text-red-600 hover:bg-red-50 rounded-xl text-xs font-bold flex items-center"
                        >
                          <X className="w-3.5 h-3.5 mr-1" /> Decline
                        </button>
                      </>
                    ) : (
                      <span className={`text-xs font-bold px-3 py-1.5 rounded-xl ${
                        b.status === 'approved' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {b.status.toUpperCase()}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Equipment Inventory Tab */}
        {activeTab === 'equipment' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Lab Equipment & Instruments</h2>
                <p className="text-xs text-slate-500">Inventory status, calibration health, and availability</p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-y border-slate-100 text-slate-500 uppercase tracking-wider font-semibold">
                  <tr>
                    <th className="py-3 px-4">Equipment Name</th>
                    <th className="py-3 px-4">Asset Code</th>
                    <th className="py-3 px-4">Quantity</th>
                    <th className="py-3 px-4">Operating Status</th>
                    <th className="py-3 px-4">Condition</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {equipmentList.map((eq) => (
                    <tr key={eq.id} className="hover:bg-slate-50/50">
                      <td className="py-3 px-4 font-bold text-slate-800">{eq.name}</td>
                      <td className="py-3 px-4 font-mono text-slate-500">{eq.serial}</td>
                      <td className="py-3 px-4 font-semibold text-slate-700">{eq.units} Units</td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-0.5 rounded-full font-bold text-[10px] ${
                          eq.status === 'Operational'
                            ? 'bg-emerald-100 text-emerald-800'
                            : eq.status === 'In Use'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}>
                          {eq.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600">{eq.condition}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Damage Reports Tab */}
        {activeTab === 'damages' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Damage Incident Reports</h2>
              <p className="text-xs text-slate-500">Student and technician reported hardware abnormalities</p>
            </div>

            <div className="space-y-3">
              {damageReports.map((report) => (
                <div key={report.id} className="p-4 rounded-xl border border-slate-200 bg-white flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-extrabold text-slate-900 text-sm">{report.equipment}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        report.severity === 'High' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                      }`}>
                        {report.severity} Severity
                      </span>
                    </div>
                    <p className="text-xs text-slate-500">Ticket: <strong>{report.id}</strong> • Reporter: {report.reportedBy} • {report.date}</p>
                    <p className="text-xs text-slate-700 mt-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                      {report.description}
                    </p>
                  </div>

                  <div className="flex-shrink-0">
                    {report.status !== 'Resolved' ? (
                      <button
                        onClick={() => handleResolveDamage(report.id)}
                        className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm"
                      >
                        Mark as Resolved
                      </button>
                    ) : (
                      <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-lg">
                        Resolved
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Maintenance Tasks Tab */}
        {activeTab === 'maintenance' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Preventive Maintenance Tasks</h2>
              <p className="text-xs text-slate-500">Scheduled servicing and hardware calibration checklist</p>
            </div>

            <div className="space-y-2.5">
              {maintenanceTasks.map((task) => (
                <div
                  key={task.id}
                  onClick={() => handleToggleTask(task.id)}
                  className="p-4 rounded-xl border border-slate-200 bg-white flex items-center justify-between cursor-pointer hover:border-emerald-300 transition-all"
                >
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => handleToggleTask(task.id)}
                      className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500 cursor-pointer"
                    />
                    <div>
                      <p className={`text-sm font-bold ${task.completed ? 'line-through text-slate-400' : 'text-slate-900'}`}>
                        {task.title}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5">Assigned: {task.assignee} • Target: {task.due}</p>
                    </div>
                  </div>
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-lg ${
                    task.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700'
                  }`}>
                    {task.priority} Priority
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
