import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  FlaskConical,
  Menu,
  X,
  ArrowRight,
  ChevronRight,
  Cpu,
  CalendarCheck2,
  QrCode,
  AlertTriangle,
  BarChart3,
  Bell,
  CheckCircle,
  Users,
  BookOpen,
  Zap,
  GraduationCap,
  ShieldCheck
} from 'lucide-react'

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Student Access', href: '#student-access' },
]

const stats = [
  { value: '500+', label: 'Labs Managed', icon: <FlaskConical className="w-5 h-5" /> },
  { value: '10,000+', label: 'Monthly Bookings', icon: <CalendarCheck2 className="w-5 h-5" /> },
  { value: '50+', label: 'Universities', icon: <BookOpen className="w-5 h-5" /> },
  { value: '99.9%', label: 'Uptime', icon: <Zap className="w-5 h-5" /> },
]

const features = [
  {
    icon: <Cpu className="w-6 h-6" />,
    title: 'Equipment Management',
    description:
      'Maintain a comprehensive inventory of all lab equipment with real-time availability status, maintenance history, and condition tracking.',
    color: 'bg-blue-50 text-blue-600',
  },
  {
    icon: <CalendarCheck2 className="w-6 h-6" />,
    title: 'Smart Booking System',
    description:
      'Students can browse available equipment and book time slots instantly. Automated conflict detection ensures fair resource allocation.',
    color: 'bg-indigo-50 text-indigo-600',
  },
  {
    icon: <QrCode className="w-6 h-6" />,
    title: 'QR Check-in Tracking',
    description:
      'Secure QR-based check-in and check-out for every session. Real-time attendance tracking with configurable grace period windows.',
    color: 'bg-violet-50 text-violet-600',
  },
  {
    icon: <AlertTriangle className="w-6 h-6" />,
    title: 'Damage Reporting',
    description:
      'Streamlined damage reporting with photo evidence, severity classification, and automatic routing to lab in-charges for quick resolution.',
    color: 'bg-amber-50 text-amber-600',
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: 'Analytics Dashboard',
    description:
      'Deep insights into lab utilization, peak hours, equipment performance, and student engagement through interactive charts and reports.',
    color: 'bg-emerald-50 text-emerald-600',
  },
  {
    icon: <Bell className="w-6 h-6" />,
    title: 'Maintenance Alerts',
    description:
      'Proactive maintenance scheduling with automated reminders. Never miss a service date and keep equipment in top condition.',
    color: 'bg-rose-50 text-rose-600',
  },
]

const steps = [
  {
    num: '01',
    title: 'Register & Set Up',
    description:
      'Register with your institutional email (studentname.ug.YY.DD@francisxavier.ac.in) for immediate academic access.',
    icon: <Users className="w-6 h-6 text-primary-600" />,
  },
  {
    num: '02',
    title: 'Book & Schedule',
    description:
      'Browse available equipment, check time slots, and book in seconds. Instant confirmation with calendar integration.',
    icon: <CalendarCheck2 className="w-6 h-6 text-primary-600" />,
  },
  {
    num: '03',
    title: 'Check-in & Track',
    description:
      'Scan your session QR code at the lab bench. Real-time session tracking begins automatically — begin your experiment!',
    icon: <QrCode className="w-6 h-6 text-primary-600" />,
  },
]

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div className="min-h-screen bg-white">
      {/* ── Navbar ──────────────────────────────────────────── */}
      <header
        className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-slate-100'
            : 'bg-transparent'
        }`}
      >
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="bg-primary-600 p-1.5 rounded-lg group-hover:bg-primary-700 transition-colors">
              <FlaskConical className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-slate-900">LabLoop</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map((l) => (
              <a
                key={l.label}
                href={l.href}
                className="text-sm font-medium text-slate-600 hover:text-primary-600 transition-colors"
              >
                {l.label}
              </a>
            ))}
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              to="/login"
              className="text-sm font-semibold text-slate-700 hover:text-primary-600 px-3 py-2 transition-colors"
            >
              Student Login
            </Link>
            <Link
              to="/register"
              className="text-sm font-medium bg-primary-600 text-white px-5 py-2.5 rounded-lg hover:bg-primary-700 transition-colors shadow-sm"
            >
              Register
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </nav>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden bg-white border-t border-slate-100 px-4 py-4 space-y-2 shadow-lg">
            {navLinks.map((l) => (
              <a
                key={l.label}
                href={l.href}
                className="block py-2 text-sm font-medium text-slate-700 hover:text-primary-600"
                onClick={() => setMenuOpen(false)}
              >
                {l.label}
              </a>
            ))}
            <div className="pt-2 border-t border-slate-100 flex flex-col gap-2">
              <Link
                to="/login"
                className="text-center py-2.5 text-sm font-medium border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50"
              >
                Student Login
              </Link>
              <Link
                to="/register"
                className="text-center py-2.5 text-sm font-medium bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Student Registration
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* ── Hero ────────────────────────────────────────────── */}
      <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-28 overflow-hidden">
        {/* Background gradient blobs */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-100 rounded-full blur-3xl opacity-60" />
          <div className="absolute top-20 right-10 w-80 h-80 bg-indigo-100 rounded-full blur-3xl opacity-50" />
          <div className="absolute bottom-0 left-10 w-64 h-64 bg-violet-100 rounded-full blur-3xl opacity-40" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-primary-50 border border-primary-200 text-primary-700 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
              <Zap className="w-3.5 h-3.5" />
              <span>Smart Laboratory Management Platform</span>
            </div>

            {/* Heading */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-slate-900 leading-tight mb-6">
              Smart Lab Management{' '}
              <span className="bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">
                for Modern Universities
              </span>
            </h1>

            <p className="text-xl text-slate-600 leading-relaxed mb-10 max-w-2xl mx-auto">
              LabLoop streamlines equipment bookings, QR check-ins, damage reporting, and laboratory utilization
              — giving academic institutions efficiency and transparency.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
              <Link
                to="/login"
                className="inline-flex items-center justify-center gap-2 bg-primary-600 text-white font-semibold px-8 py-4 rounded-xl hover:bg-primary-700 transition-all shadow-lg shadow-primary-200 hover:shadow-xl hover:shadow-primary-200 hover:-translate-y-0.5"
              >
                Student Portal (Sign In)
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 bg-white text-slate-700 font-semibold px-8 py-4 rounded-xl hover:bg-slate-50 transition-all border border-slate-200 shadow-sm"
              >
                Student Registration
                <ChevronRight className="w-5 h-5" />
              </Link>
            </div>

            <p className="text-xs text-slate-500">
              Institutional Email Format: <span className="font-mono text-slate-700">studentname.ug.YY.DD@francisxavier.ac.in</span>
            </p>
          </div>

          {/* Interactive Lab Status Preview */}
          <div className="mt-14 max-w-3xl mx-auto">
            <div className="bg-white rounded-2xl shadow-xl border border-slate-100 p-6 sm:p-8">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
                <div>
                  <h3 className="font-bold text-slate-900 text-lg">Academic Laboratory Status</h3>
                  <p className="text-slate-400 text-xs">Live Resource Allocation</p>
                </div>
                <span className="inline-flex items-center gap-1.5 bg-emerald-50 text-emerald-700 text-xs font-semibold px-3 py-1 rounded-full border border-emerald-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Live System
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-50 rounded-xl p-3.5 text-center">
                  <p className="text-2xl font-extrabold text-slate-900">12</p>
                  <p className="text-xs text-slate-500 mt-0.5">Active Sessions</p>
                </div>
                <div className="bg-slate-50 rounded-xl p-3.5 text-center">
                  <p className="text-2xl font-extrabold text-primary-600">8</p>
                  <p className="text-xs text-slate-500 mt-0.5">Available Now</p>
                </div>
                <div className="bg-slate-50 rounded-xl p-3.5 text-center">
                  <p className="text-2xl font-extrabold text-indigo-600">34</p>
                  <p className="text-xs text-slate-500 mt-0.5">Today's Bookings</p>
                </div>
                <div className="bg-slate-50 rounded-xl p-3.5 text-center">
                  <p className="text-2xl font-extrabold text-slate-900">2.4h</p>
                  <p className="text-xs text-slate-500 mt-0.5">Avg Session</p>
                </div>
              </div>

              {/* Progress bars */}
              <div className="space-y-3">
                {[
                  { name: 'GPU Workstations (AI & Robotics)', percent: 85, color: 'bg-primary-600' },
                  { name: 'Digital Oscilloscopes (Signal Lab)', percent: 60, color: 'bg-indigo-600' },
                  { name: '3D Prototyping Printers (CAD Lab)', percent: 40, color: 'bg-emerald-500' },
                ].map((item) => (
                  <div key={item.name}>
                    <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                      <span>{item.name}</span>
                      <span>{item.percent}% Booked</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div
                        className={`${item.color} h-2 rounded-full transition-all duration-500`}
                        style={{ width: `${item.percent}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats Strip ─────────────────────────────────────── */}
      <section className="bg-primary-600 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
            {stats.map((s) => (
              <div key={s.label} className="flex flex-col items-center">
                <div className="mb-2 p-2 bg-primary-700 rounded-lg">{s.icon}</div>
                <p className="text-3xl sm:text-4xl font-extrabold">{s.value}</p>
                <p className="text-primary-100 text-sm mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features Grid ───────────────────────────────────── */}
      <section id="features" className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 text-primary-600 text-sm font-semibold uppercase tracking-widest mb-4">
              <div className="w-8 h-px bg-primary-600" />
              Features
              <div className="w-8 h-px bg-primary-600" />
            </div>
            <h2 className="text-4xl font-extrabold text-slate-900 mb-4">
              Everything your lab needs
            </h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto">
              A complete platform designed for academic labs, from single equipment rooms to
              multi-department research facilities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((f) => (
              <div
                key={f.title}
                className="bg-white rounded-2xl p-7 border border-slate-100 shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-1"
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-5 ${f.color}`}>
                  {f.icon}
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{f.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ────────────────────────────────────── */}
      <section id="how-it-works" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 text-primary-600 text-sm font-semibold uppercase tracking-widest mb-4">
              <div className="w-8 h-px bg-primary-600" />
              How it works
              <div className="w-8 h-px bg-primary-600" />
            </div>
            <h2 className="text-4xl font-extrabold text-slate-900 mb-4">
              Up and running in minutes
            </h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto">
              Three simple steps to transform how your institution manages laboratory resources.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {steps.map((step) => (
              <div key={step.num} className="text-center flex flex-col items-center">
                <div className="relative mb-6">
                  <div className="w-16 h-16 rounded-2xl bg-primary-50 border-2 border-primary-200 flex items-center justify-center">
                    {step.icon}
                  </div>
                  <span className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-primary-600 text-white text-xs font-bold flex items-center justify-center">
                    {step.num}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{step.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed max-w-xs">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Student Access & Portal Showcase ────────────────── */}
      <section id="student-access" className="py-24 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 text-primary-600 text-sm font-semibold uppercase tracking-widest mb-4">
              <div className="w-8 h-px bg-primary-600" />
              Student Laboratory Access
              <div className="w-8 h-px bg-primary-600" />
            </div>
            <h2 className="text-4xl font-extrabold text-slate-900 mb-4">
              Designed for Academic Excellence
            </h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto">
              Students register and authenticate with their institutional email address:
              <br />
              <span className="font-mono text-primary-700 font-semibold text-sm">
                studentname.ug.YY.DD@francisxavier.ac.in
              </span>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-2xl p-7 border border-primary-200 bg-white shadow-sm hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
                <GraduationCap className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Resource Browsing</h3>
              <p className="text-sm text-slate-600 leading-relaxed mb-4">
                Explore real-time equipment availability across GPU computing, electronic oscilloscopes, and 3D fabrication clusters.
              </p>
              <ul className="text-xs text-slate-500 space-y-2">
                <li className="flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-primary-500" /> Live bench availability
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-primary-500" /> Detailed hardware specifications
                </li>
              </ul>
            </div>

            <div className="rounded-2xl p-7 border border-primary-200 bg-white shadow-sm hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
                <CalendarCheck2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Slot Reservations</h3>
              <p className="text-sm text-slate-600 leading-relaxed mb-4">
                Book lab stations for capstone projects, lab practicals, and guided research with automated conflict resolution.
              </p>
              <ul className="text-xs text-slate-500 space-y-2">
                <li className="flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-primary-500" /> Automatic approval queues
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-primary-500" /> Instant booking status notifications
                </li>
              </ul>
            </div>

            <div className="rounded-2xl p-7 border border-primary-200 bg-white shadow-sm hover:shadow-md transition-all">
              <div className="w-12 h-12 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center mb-4">
                <QrCode className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Desk QR Check-in</h3>
              <p className="text-sm text-slate-600 leading-relaxed mb-4">
                Cryptographically verify attendance directly at your workstation using tamper-proof QR code tracking.
              </p>
              <ul className="text-xs text-slate-500 space-y-2">
                <li className="flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-primary-500" /> Automated session timer
                </li>
                <li className="flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-primary-500" /> Instant damage incident reporting
                </li>
              </ul>
            </div>
          </div>

          <div className="mt-12 text-center flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/login"
              className="py-3.5 px-8 bg-primary-600 hover:bg-primary-700 text-white font-bold text-sm rounded-xl shadow-md transition-all flex items-center gap-2"
            >
              <span>Student Portal Sign In</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/register"
              className="py-3.5 px-8 bg-white hover:bg-slate-50 text-slate-800 font-bold text-sm rounded-xl border border-slate-200 shadow-sm transition-all"
            >
              Register with Institutional Email
            </Link>
          </div>

          {/* Institutional note */}
          <div className="mt-8 text-center">
            <p className="text-xs text-slate-400 inline-flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-slate-400" />
              Faculty In-charge and System Administrator portals are strictly protected and require authorized institutional credentials.
            </p>
          </div>
        </div>
      </section>

      {/* ── CTA Banner ──────────────────────────────────────── */}
      <section className="py-20 bg-gradient-to-r from-primary-700 to-indigo-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-extrabold text-white mb-4">
            Ready to access your laboratory?
          </h2>
          <p className="text-xl text-primary-100 mb-10">
            Sign in with your institutional credentials to browse available equipment and reserve your workstation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 bg-white text-primary-700 font-bold px-8 py-4 rounded-xl hover:bg-primary-50 transition-all shadow-lg"
            >
              Register Student Account
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 bg-white/10 text-white font-semibold px-8 py-4 rounded-xl hover:bg-white/20 transition-all border border-white/30"
            >
              Sign In to Portal
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────── */}
      <footer className="bg-slate-900 text-slate-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2.5">
              <div className="bg-primary-600 p-1.5 rounded-lg">
                <FlaskConical className="w-4 h-4 text-white" />
              </div>
              <span className="text-white font-bold text-lg">LabLoop</span>
            </div>

            <div className="flex items-center gap-6 text-sm">
              {navLinks.map((l) => (
                <a
                  key={l.label}
                  href={l.href}
                  className="hover:text-white transition-colors"
                >
                  {l.label}
                </a>
              ))}
              <Link to="/login" className="hover:text-white transition-colors">
                Student Login
              </Link>
              <Link to="/register" className="hover:text-white transition-colors">
                Student Registration
              </Link>
            </div>

            <p className="text-sm">
              © {new Date().getFullYear()} LabLoop. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
