import { FlaskConical, CheckCircle2, BarChart3, Zap } from 'lucide-react'

const features = [
  {
    icon: <CheckCircle2 className="w-5 h-5 text-blue-300" />,
    text: 'Smart equipment booking & scheduling',
  },
  {
    icon: <BarChart3 className="w-5 h-5 text-blue-300" />,
    text: 'Real-time analytics & usage reports',
  },
  {
    icon: <Zap className="w-5 h-5 text-blue-300" />,
    text: 'QR-based check-in & tracking',
  },
]

export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="min-h-screen flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-700 via-primary-600 to-indigo-700 relative overflow-hidden flex-col justify-between p-12">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 rounded-full bg-white -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-80 h-80 rounded-full bg-white translate-x-1/3 translate-y-1/3" />
          <div className="absolute top-1/2 right-10 w-48 h-48 rounded-full bg-indigo-300" />
        </div>

        {/* Logo */}
        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 backdrop-blur-sm p-2.5 rounded-xl">
              <FlaskConical className="w-7 h-7 text-white" />
            </div>
            <span className="text-2xl font-bold text-white tracking-tight">LabLoop</span>
          </div>
        </div>

        {/* Center content */}
        <div className="relative space-y-8">
          <div>
            <h2 className="text-4xl font-bold text-white leading-tight mb-4">
              Smart Lab Management for Modern Universities
            </h2>
            <p className="text-blue-100 text-lg leading-relaxed">
              Streamline equipment bookings, track usage in real-time, and keep your labs running efficiently.
            </p>
          </div>

          <div className="space-y-4">
            {features.map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="bg-white/15 rounded-lg p-2 shrink-0">{f.icon}</div>
                <span className="text-blue-50 font-medium">{f.text}</span>
              </div>
            ))}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/20">
            {[
              { value: '500+', label: 'Labs' },
              { value: '10K+', label: 'Bookings' },
              { value: '50+', label: 'Universities' },
            ].map((s) => (
              <div key={s.label} className="text-center">
                <div className="text-2xl font-bold text-white">{s.value}</div>
                <div className="text-blue-200 text-sm">{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="relative">
          <p className="text-blue-200 text-sm">
            © {new Date().getFullYear()} LabLoop. All rights reserved.
          </p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex flex-col justify-center items-center p-6 sm:p-10 lg:p-16 bg-white lg:overflow-y-auto">
        {/* Mobile logo */}
        <div className="lg:hidden mb-8 flex items-center gap-2">
          <div className="bg-primary-600 p-2 rounded-lg">
            <FlaskConical className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold text-slate-900">LabLoop</span>
        </div>

        <div className="w-full max-w-md animate-slide-up">
          {/* Header text */}
          {(title || subtitle) && (
            <div className="mb-8">
              {title && (
                <h1 className="text-2xl font-bold text-slate-900 mb-2">{title}</h1>
              )}
              {subtitle && (
                <p className="text-slate-500 text-sm leading-relaxed">{subtitle}</p>
              )}
            </div>
          )}

          {children}
        </div>
      </div>
    </div>
  )
}
