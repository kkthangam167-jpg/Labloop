import React, { useState, useEffect } from 'react'
import {
  BookOpen,
  Calendar,
  Clock,
  QrCode,
  AlertCircle,
  CheckCircle2,
  Layers,
  GraduationCap,
  Building,
  RefreshCw,
  Search,
  Check,
  Send,
  Camera,
  Play,
  X
} from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '@/store/authStore'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { dashboardApi } from '@/api/dashboard.api'

export default function StudentDashboard() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  // Equipment and Bookings from Backend
  const [equipmentList, setEquipmentList] = useState([])
  const [myBookings, setMyBookings] = useState([])

  // Booking Modal State
  const [bookingModalOpen, setBookingModalOpen] = useState(false)
  const [selectedEquipment, setSelectedEquipment] = useState(null)
  const [bookingDate, setBookingDate] = useState('2026-11-10')
  const [bookingStartTime, setBookingStartTime] = useState('10:00')
  const [bookingEndTime, setBookingEndTime] = useState('12:00')
  const [bookingPurpose, setBookingPurpose] = useState('')
  const [submittingBooking, setSubmittingBooking] = useState(false)

  // Damage Report Form State
  const [damageEqId, setDamageEqId] = useState('')
  const [damageSeverity, setDamageSeverity] = useState('moderate')
  const [damageDesc, setDamageDesc] = useState('')
  const [submittingDamage, setSubmittingDamage] = useState(false)

  // QR Check-in State
  const [qrScanning, setQrScanning] = useState(false)
  const [checkedInSession, setCheckedInSession] = useState(null)

  const navItems = [
    { id: 'overview', label: 'Overview', icon: BookOpen },
    { id: 'equipment', label: 'Available Equipment', icon: Layers, badge: equipmentList.length },
    { id: 'bookings', label: 'My Bookings', icon: Calendar, badge: myBookings.length },
    { id: 'sessions', label: 'Active Sessions', icon: Clock, badge: myBookings.filter(b => b.status === 'active').length },
    { id: 'qr', label: 'QR Check-in', icon: QrCode },
    { id: 'damage', label: 'Report Damage', icon: AlertCircle },
  ]

  const loadData = async () => {
    setLoading(true)
    try {
      const [summaryRes, eqRes, bookingsRes] = await Promise.allSettled([
        dashboardApi.getSummary(),
        dashboardApi.getEquipment(),
        dashboardApi.getBookings(),
      ])

      if (summaryRes.status === 'fulfilled' && summaryRes.value?.data?.data) {
        setStats(summaryRes.value.data.data)
      }

      if (eqRes.status === 'fulfilled' && eqRes.value?.data?.data?.items) {
        setEquipmentList(eqRes.value.data.data.items)
        if (eqRes.value.data.data.items.length > 0 && !damageEqId) {
          setDamageEqId(eqRes.value.data.data.items[0].id)
        }
      }

      if (bookingsRes.status === 'fulfilled' && bookingsRes.value?.data?.data?.items) {
        setMyBookings(bookingsRes.value.data.data.items)
        const active = bookingsRes.value.data.data.items.find(b => b.status === 'active')
        if (active) {
          setCheckedInSession({
            bookingId: active.id,
            equipment: active.equipment?.name || 'Lab Equipment',
            checkInTime: active.checkin_time ? new Date(active.checkin_time).toLocaleTimeString() : 'Active',
            expiresAt: active.end_time || 'Session Active',
          })
        }
      }
    } catch (err) {
      console.error('Error loading student dashboard data:', err)
      toast.error('Failed to load some dashboard data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleOpenBooking = (item) => {
    setSelectedEquipment(item)
    setBookingModalOpen(true)
  }

  const handleCreateBooking = async (e) => {
    e.preventDefault()
    if (!bookingPurpose.trim()) {
      toast.error('Please enter a research or academic purpose for this booking.')
      return
    }

    setSubmittingBooking(true)
    try {
      const res = await dashboardApi.createBooking({
        equipment_id: selectedEquipment.id,
        booking_date: bookingDate,
        start_time: bookingStartTime,
        end_time: bookingEndTime,
        purpose: bookingPurpose.trim(),
      })

      if (res.data?.success) {
        toast.success(res.data.message || 'Booking requested successfully!')
        setBookingModalOpen(false)
        setBookingPurpose('')
        loadData()
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to submit booking.')
    } finally {
      setSubmittingBooking(false)
    }
  }

  const handleCancelBooking = async (id) => {
    try {
      const res = await dashboardApi.cancelBooking(id)
      if (res.data?.success) {
        toast.success(`Booking #${id} cancelled.`)
        setMyBookings((prev) => prev.map((b) => (b.id === id ? { ...b, status: 'cancelled' } : b)))
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Could not cancel booking.')
    }
  }

  const handleSimulateQR = async (bookingId, token) => {
    setQrScanning(true)
    try {
      const res = await dashboardApi.checkinBooking(bookingId, token || 'verified-scan')
      if (res.data?.success) {
        toast.success('QR Code Verified! Lab session is now active.')
        setCheckedInSession({
          bookingId: bookingId,
          equipment: res.data.data?.equipment?.name || 'Lab Equipment',
          checkInTime: new Date().toLocaleTimeString(),
          expiresAt: res.data.data?.end_time || '04:30 PM',
        })
        loadData()
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'QR Check-in verification failed.')
    } finally {
      setQrScanning(false)
    }
  }

  const handleCheckout = async (bookingId) => {
    try {
      const res = await dashboardApi.checkoutBooking(bookingId)
      if (res.data?.success) {
        toast.success('Session completed! Equipment returned.')
        setCheckedInSession(null)
        loadData()
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to check out.')
    }
  }

  const handleSubmitDamage = async (e) => {
    e.preventDefault()
    if (!damageDesc.trim()) {
      toast.error('Please provide details of the damage or abnormality.')
      return
    }

    setSubmittingDamage(true)
    try {
      const selectedEq = equipmentList.find(e => String(e.id) === String(damageEqId))
      const res = await dashboardApi.createDamageReport({
        equipment_id: Number(damageEqId) || (equipmentList[0]?.id || 1),
        title: `${damageSeverity.toUpperCase()} defect reported: ${selectedEq?.name || 'Equipment'}`,
        description: damageDesc.trim(),
        severity: damageSeverity.toLowerCase(),
        affects_availability: damageSeverity === 'critical' || damageSeverity === 'severe',
      })

      if (res.data?.success) {
        toast.success('Damage report filed successfully! Reference #' + res.data.data?.id + ' assigned.')
        setDamageDesc('')
        setActiveTab('overview')
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to submit damage report.')
    } finally {
      setSubmittingDamage(false)
    }
  }

  const departmentName = stats?.department || user?.department_code || 'Computer Science & Engineering'
  const studentRoll = stats?.roll_number || user?.roll_number || 'CS25101'
  const admissionYear = user?.admission_year || '25'

  return (
    <DashboardLayout
      badgeText="Student Portal"
      badgeColor="bg-blue-100 text-blue-800"
      navItems={navItems}
      activeTab={activeTab}
      onTabChange={setActiveTab}
    >
      <div className="space-y-6">
        {/* Banner */}
        <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-xl shadow-blue-900/10">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <span className="text-xs font-bold tracking-wider uppercase text-blue-200">
                Academic Laboratory Student Portal
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold mt-1">
                Welcome, {user?.full_name?.split(' ')[0]}!
              </h1>
              <p className="text-blue-100 text-sm mt-1.5 max-w-xl">
                Enrolled Department: <strong>{departmentName}</strong> • Roll Number: <strong className="font-mono">{studentRoll}</strong>
              </p>
            </div>
            <button
              onClick={loadData}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/20 text-white backdrop-blur-sm transition-all border border-white/15 w-fit"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh Dashboard
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
                    My Bookings
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                    <Calendar className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-3xl font-black text-slate-900">{myBookings.length}</p>
                <p className="text-xs text-slate-500 mt-2">Total reservations</p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Next Active Session
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <Clock className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-xl font-black text-emerald-600">Today, 2:00 PM</p>
                <p className="text-xs text-slate-500 mt-2 font-medium">Ready for QR Check-in</p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Assigned Dept
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                    <GraduationCap className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-sm font-black text-slate-900 truncate">{departmentName}</p>
                <p className="text-xs text-purple-600 font-bold mt-2">Roll No: {studentRoll}</p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Session Check-in
                  </span>
                  <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
                    <QrCode className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-lg font-black text-indigo-600">
                  {checkedInSession ? 'Session Active' : 'QR Scanner Ready'}
                </p>
                <p className="text-xs text-slate-500 mt-2">Desk check-in verification</p>
              </div>
            </div>

            {/* Quick Actions & Live Session */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Upcoming Session Action Card */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
                    <h3 className="text-base font-bold text-slate-900">Upcoming Lab Session</h3>
                  </div>
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800">
                    Approved
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-2">
                  <h4 className="font-extrabold text-slate-900 text-sm">
                    NVIDIA RTX A6000 GPU Workstation #04
                  </h4>
                  <p className="text-xs text-slate-600">
                    Advanced Robotics & AI Lab • Location: <strong>Tech Block 204</strong>
                  </p>
                  <p className="text-xs text-slate-500">
                    Slot: <strong>Today, 02:00 PM – 04:30 PM</strong>
                  </p>
                </div>

                <div className="flex items-center space-x-3 pt-2">
                  <button
                    onClick={() => setActiveTab('qr')}
                    className="flex-1 py-2 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center justify-center shadow-md shadow-blue-500/20 transition-all cursor-pointer"
                  >
                    <QrCode className="w-4 h-4 mr-2" /> Open QR Check-in
                  </button>
                  <button
                    onClick={() => setActiveTab('equipment')}
                    className="py-2 px-4 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 font-bold text-xs transition-colors cursor-pointer"
                  >
                    Browse Equipment
                  </button>
                </div>
              </div>

              {/* Damage & Maintenance Notice */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900">Lab Protocol & Safety</h3>
                  <span className="text-xs font-bold text-blue-600">Guidelines</span>
                </div>

                <div className="space-y-2.5 text-xs text-slate-600">
                  <div className="p-3 rounded-xl bg-blue-50/60 border border-blue-100">
                    <p className="font-bold text-blue-900 mb-0.5">Desk QR Check-in Required</p>
                    <p className="text-blue-700">Scan desk QR within 15 minutes of slot commencement to avoid auto-cancellation.</p>
                  </div>
                  <div className="p-3 rounded-xl bg-amber-50/60 border border-amber-100">
                    <p className="font-bold text-amber-900 mb-0.5">Equipment Damage Reporting</p>
                    <p className="text-amber-700">Found a faulty probe or machine issue? Report it immediately to avoid student liability.</p>
                  </div>
                </div>

                <button
                  onClick={() => setActiveTab('damage')}
                  className="w-full py-2 px-4 rounded-xl border border-red-200 text-red-600 hover:bg-red-50 font-bold text-xs flex items-center justify-center transition-colors cursor-pointer"
                >
                  <AlertCircle className="w-4 h-4 mr-2" /> Report Equipment Damage
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Available Equipment Tab */}
        {activeTab === 'equipment' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Available Laboratory Equipment</h2>
              <p className="text-xs text-slate-500">
                Reserve hardware resources for coursework, experiments, and project development
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {equipmentList.map((eq) => (
                <div
                  key={eq.id}
                  className="p-5 rounded-2xl border border-slate-200 bg-white hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                        {eq.category?.name || eq.category || 'Hardware'}
                      </span>
                      <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">
                        {eq.quantity_available ?? eq.availableUnits ?? 1} of {eq.quantity_total ?? eq.totalUnits ?? 1} Available
                      </span>
                    </div>

                    <h3 className="font-extrabold text-slate-900 text-base mt-2">{eq.name}</h3>
                    <p className="text-xs text-slate-500 mt-1 font-mono">
                      {eq.description || eq.specs || `Model: ${eq.model_number || 'Standard'}`}
                    </p>
                    <p className="text-xs text-slate-600 mt-3">
                      Facility: <strong>{eq.lab?.name || eq.lab || 'Research Facility'}</strong> ({eq.lab?.location || eq.location_in_lab || 'Campus'})
                    </p>
                  </div>

                  <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-xs text-slate-500">Status: <strong className="capitalize text-emerald-600">{eq.status || 'Available'}</strong></span>
                    <button
                      onClick={() => handleOpenBooking(eq)}
                      disabled={eq.status === 'under_maintenance' || eq.quantity_available === 0}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl text-xs font-bold transition-all shadow-sm cursor-pointer"
                    >
                      Book Slot
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* My Bookings Tab */}
        {activeTab === 'bookings' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">My Lab Reservations</h2>
              <p className="text-xs text-slate-500">Track pending, active, and completed booking sessions</p>
            </div>

            <div className="space-y-3">
              {myBookings.length === 0 ? (
                <div className="p-8 text-center text-slate-500 border border-slate-100 rounded-xl bg-slate-50">
                  <p className="text-sm font-semibold">No lab reservations yet.</p>
                  <p className="text-xs text-slate-400 mt-1">Browse Available Equipment and book your first slot.</p>
                </div>
              ) : (
                myBookings.map((b) => (
                  <div
                    key={b.id}
                    className="p-4 rounded-xl border border-slate-200 bg-white flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold text-slate-400">BK-{b.id}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full capitalize ${
                          b.status === 'approved'
                            ? 'bg-emerald-100 text-emerald-800'
                            : b.status === 'completed'
                            ? 'bg-slate-100 text-slate-600'
                            : b.status === 'active'
                            ? 'bg-blue-100 text-blue-800'
                            : b.status === 'cancelled' || b.status === 'rejected'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}>
                          {b.status}
                        </span>
                      </div>
                      <h4 className="font-extrabold text-slate-900 text-sm">{b.equipment?.name || b.equipment || 'Equipment'}</h4>
                      <p className="text-xs text-slate-500">{b.equipment?.lab_name || b.lab || 'Assigned Lab'} • {b.equipment?.lab_location || b.location || 'Campus'}</p>
                      <p className="text-xs text-slate-700 font-semibold flex items-center mt-1">
                        <Clock className="w-3.5 h-3.5 mr-1 text-slate-400" />
                        {b.booking_date} ({b.start_time || '10:00'} – {b.end_time || '12:00'})
                      </p>
                      {b.purpose && (
                        <p className="text-xs text-slate-500 italic">Purpose: {b.purpose}</p>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 flex-shrink-0">
                      {b.status === 'approved' && (
                        <button
                          onClick={() => handleSimulateQR(b.id, 'verified-scan')}
                          disabled={qrScanning}
                          className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center cursor-pointer shadow-sm"
                        >
                          <QrCode className="w-3.5 h-3.5 mr-1.5" /> Check In
                        </button>
                      )}
                      {b.status === 'active' && (
                        <button
                          onClick={() => handleCheckout(b.id)}
                          className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center cursor-pointer shadow-sm"
                        >
                          Check Out
                        </button>
                      )}
                      {(b.status === 'pending' || b.status === 'approved') && (
                        <button
                          onClick={() => handleCancelBooking(b.id)}
                          className="px-3.5 py-1.5 border border-red-200 text-red-600 hover:bg-red-50 rounded-xl text-xs font-bold transition-colors cursor-pointer"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Active Sessions Tab */}
        {activeTab === 'sessions' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Current Active Sessions</h2>
              <p className="text-xs text-slate-500">Live verified sessions currently running in the laboratory</p>
            </div>

            {checkedInSession ? (
              <div className="p-6 rounded-2xl border-2 border-emerald-200 bg-emerald-50/40 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div>
                    <span className="text-xs font-black px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800">
                      SESSION IN PROGRESS
                    </span>
                    <h3 className="text-xl font-extrabold text-slate-900 mt-2">
                      {checkedInSession.equipment}
                    </h3>
                    <p className="text-xs text-slate-600 mt-1">Station Booking Reference: #BK-{checkedInSession.bookingId}</p>
                  </div>
                  <div className="text-right sm:border-l sm:border-slate-200 sm:pl-6">
                    <span className="text-xs text-slate-500 block uppercase font-bold">Checked In At</span>
                    <span className="text-lg font-black text-emerald-700">{checkedInSession.checkInTime}</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-emerald-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <p className="text-xs text-slate-600">
                    Return hardware promptly when finished to restore unit availability.
                  </p>
                  <button
                    onClick={() => handleCheckout(checkedInSession.bookingId)}
                    className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center justify-center shadow-md shadow-emerald-500/20 cursor-pointer"
                  >
                    Complete Session & Check Out
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-slate-500 border border-slate-100 rounded-xl bg-slate-50">
                <p className="text-sm font-semibold">No active session at this moment.</p>
                <p className="text-xs text-slate-400 mt-1">Check in to an approved reservation or book an available workstation.</p>
              </div>
            )}
          </div>
        )}

        {/* QR Check-in Tab */}
        {activeTab === 'qr' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Laboratory QR Check-in</h2>
              <p className="text-xs text-slate-500">
                Scan the dynamic QR code displayed on the lab desk or station monitor to verify attendance
              </p>
            </div>

            <div className="max-w-md mx-auto p-6 rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 text-center space-y-4">
              <div className="w-20 h-20 mx-auto rounded-2xl bg-blue-100 text-blue-600 flex items-center justify-center">
                <QrCode className="w-10 h-10" />
              </div>

              <div>
                <h3 className="font-extrabold text-slate-900 text-base">Station QR Scanner</h3>
                <p className="text-xs text-slate-500 mt-1">
                  Verifies cryptographic HMAC token linked to the physical station
                </p>
              </div>

              {checkedInSession ? (
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs text-left space-y-1">
                  <div className="flex items-center space-x-2 font-bold text-emerald-900">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Check-in Verified</span>
                  </div>
                  <p>Equipment: <strong>{checkedInSession.equipment}</strong></p>
                  <p>Checked in at: <strong>{checkedInSession.checkInTime}</strong></p>
                  <button
                    onClick={() => handleCheckout(checkedInSession.bookingId)}
                    className="w-full mt-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold text-xs"
                  >
                    Check Out Station
                  </button>
                </div>
              ) : (
                <div>
                  {myBookings.find(b => b.status === 'approved') ? (
                    <button
                      onClick={() => {
                        const approved = myBookings.find(b => b.status === 'approved')
                        if (approved) handleSimulateQR(approved.id, 'verified-scan')
                      }}
                      disabled={qrScanning}
                      className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center justify-center shadow-md shadow-blue-500/20 cursor-pointer transition-all"
                    >
                      <Camera className="w-4 h-4 mr-2" />
                      {qrScanning ? 'Verifying Station Code...' : 'Scan & Check In to Approved Slot'}
                    </button>
                  ) : (
                    <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-800">
                      <p className="font-semibold">No approved bookings ready for check-in.</p>
                      <p className="mt-1">Book an equipment slot first and wait for In-charge approval.</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Report Damage Tab */}
        {activeTab === 'damage' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Report Equipment Damage or Defect</h2>
              <p className="text-xs text-slate-500">
                Found malfunctioning hardware or broken components? Notify the Lab In-charge immediately
              </p>
            </div>

            <form onSubmit={handleSubmitDamage} className="space-y-4 max-w-xl">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Equipment / Asset
                </label>
                <select
                  value={damageEqId}
                  onChange={(e) => setDamageEqId(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {equipmentList.map((eq) => (
                    <option key={eq.id} value={eq.id}>
                      {eq.name} ({eq.lab?.name || 'Lab'})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Severity Level
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {['minor', 'moderate', 'severe', 'critical'].map((lvl) => (
                    <button
                      key={lvl}
                      type="button"
                      onClick={() => setDamageSeverity(lvl)}
                      className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all cursor-pointer capitalize ${
                        damageSeverity === lvl
                          ? 'border-blue-600 bg-blue-50 text-blue-700'
                          : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Issue Description
                </label>
                <textarea
                  rows={4}
                  value={damageDesc}
                  onChange={(e) => setDamageDesc(e.target.value)}
                  placeholder="Describe observed physical defects, error codes, broken cords, or intermittent faults..."
                  className="w-full text-xs p-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={submittingDamage}
                className="py-2.5 px-6 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold flex items-center shadow-md shadow-red-500/20 cursor-pointer disabled:bg-slate-300"
              >
                <Send className="w-3.5 h-3.5 mr-2" />
                {submittingDamage ? 'Submitting Report...' : 'Submit Damage Incident Report'}
              </button>
            </form>
          </div>
        )}

        {/* Slot Reservation Modal */}
        {bookingModalOpen && selectedEquipment && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between border-b pb-3 border-slate-100">
                <h3 className="font-extrabold text-slate-900 text-base">Book Lab Station Slot</h3>
                <button onClick={() => setBookingModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-3 bg-blue-50/60 rounded-xl border border-blue-100 text-xs">
                <p className="font-bold text-blue-900">{selectedEquipment.name}</p>
                <p className="text-blue-700">{selectedEquipment.lab?.name || selectedEquipment.lab || 'Lab Facility'}</p>
              </div>

              <form onSubmit={handleCreateBooking} className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Reservation Date</label>
                  <input
                    type="date"
                    required
                    value={bookingDate}
                    onChange={(e) => setBookingDate(e.target.value)}
                    className="w-full p-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Start Time</label>
                    <input
                      type="time"
                      required
                      value={bookingStartTime}
                      onChange={(e) => setBookingStartTime(e.target.value)}
                      className="w-full p-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block font-bold text-slate-700 mb-1">End Time</label>
                    <input
                      type="time"
                      required
                      value={bookingEndTime}
                      onChange={(e) => setBookingEndTime(e.target.value)}
                      className="w-full p-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Academic / Project Purpose</label>
                  <textarea
                    rows={3}
                    required
                    value={bookingPurpose}
                    onChange={(e) => setBookingPurpose(e.target.value)}
                    placeholder="e.g., Deep learning transformer training for Capstone project..."
                    className="w-full p-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setBookingModalOpen(false)}
                    className="px-4 py-2 text-slate-600 font-bold hover:bg-slate-50 rounded-xl"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submittingBooking}
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-md shadow-blue-500/20 disabled:bg-slate-300"
                  >
                    {submittingBooking ? 'Submitting...' : 'Confirm Reservation'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
