import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LogOut,
  Menu,
  X,
  ChevronRight,
  Shield,
  FlaskConical,
  GraduationCap
} from 'lucide-react'
import useAuthStore from '@/store/authStore'
import { useLogout } from '@/hooks/useAuth'

export default function DashboardLayout({
  title,
  subtitle,
  badgeText,
  badgeColor = 'bg-blue-100 text-blue-800',
  navItems = [],
  activeTab,
  onTabChange,
  children,
}) {
  const { user } = useAuthStore()
  const { mutate: logout, isPending } = useLogout()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  const getRoleIcon = () => {
    if (user?.role === 'super_admin') return <Shield className="w-5 h-5 text-purple-600" />
    if (user?.role === 'lab_incharge') return <FlaskConical className="w-5 h-5 text-emerald-600" />
    return <GraduationCap className="w-5 h-5 text-blue-600" />
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-black bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                LabLoop
              </span>
              <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${badgeColor}`}>
                {badgeText}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <div className="flex items-center justify-end space-x-1.5">
                {getRoleIcon()}
                <p className="text-sm font-bold text-slate-800">{user?.full_name}</p>
              </div>
              <p className="text-xs text-slate-500">{user?.email}</p>
            </div>
            <button
              onClick={() => logout()}
              disabled={isPending}
              className="inline-flex items-center px-3 py-1.5 border border-slate-200 text-xs font-semibold rounded-lg text-slate-700 bg-white hover:bg-slate-50 hover:text-red-600 transition-colors shadow-sm disabled:opacity-50 cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5 mr-1.5" />
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Body with Sidebar and Main Area */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 flex gap-6">
        {/* Desktop Sidebar Navigation */}
        <aside className="w-64 flex-shrink-0 hidden md:block">
          <div className="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-sm sticky top-24 space-y-1">
            <div className="px-3 py-2 text-xs font-bold uppercase tracking-wider text-slate-400">
              Workspace Menu
            </div>
            {navItems.map((item, idx) => {
              const isSelected = activeTab
                ? activeTab === item.id
                : item.href === location.pathname
              const Icon = item.icon
              const content = (
                <>
                  <div className="flex items-center space-x-3">
                    {Icon && <Icon className={`w-4 h-4 ${isSelected ? 'text-primary-600' : 'text-slate-400'}`} />}
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== undefined && (
                    <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                      isSelected ? 'bg-primary-100 text-primary-700' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </>
              )

              if (onTabChange && item.id) {
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => onTabChange(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all text-left cursor-pointer ${
                      isSelected
                        ? 'bg-blue-50 text-blue-700 font-bold shadow-sm'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`}
                  >
                    {content}
                  </button>
                )
              }

              return (
                <Link
                  key={idx}
                  to={item.href || '#'}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                    isSelected
                      ? 'bg-blue-50 text-blue-700 font-bold shadow-sm'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  {content}
                </Link>
              )
            })}
          </div>
        </aside>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm flex">
            <div className="w-72 bg-white h-full p-5 space-y-4 shadow-xl flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b pb-3 border-slate-100">
                  <span className="font-bold text-slate-900 text-sm">Navigation</span>
                  <button onClick={() => setMobileMenuOpen(false)} className="text-slate-400">
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <div className="space-y-1">
                  {navItems.map((item, idx) => {
                    const isSelected = activeTab
                      ? activeTab === item.id
                      : item.href === location.pathname
                    const Icon = item.icon
                    const handleClick = () => {
                      setMobileMenuOpen(false)
                      if (onTabChange && item.id) onTabChange(item.id)
                    }

                    if (onTabChange && item.id) {
                      return (
                        <button
                          key={idx}
                          type="button"
                          onClick={handleClick}
                          className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold text-left ${
                            isSelected ? 'bg-blue-50 text-blue-700 font-bold' : 'text-slate-600'
                          }`}
                        >
                          {Icon && <Icon className="w-4 h-4 text-slate-400" />}
                          <span>{item.label}</span>
                        </button>
                      )
                    }

                    return (
                      <Link
                        key={idx}
                        to={item.href || '#'}
                        onClick={handleClick}
                        className={`flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold ${
                          isSelected ? 'bg-blue-50 text-blue-700 font-bold' : 'text-slate-600'
                        }`}
                      >
                        {Icon && <Icon className="w-4 h-4 text-slate-400" />}
                        <span>{item.label}</span>
                      </Link>
                    )
                  })}
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100">
                <p className="text-xs font-semibold text-slate-700">{user?.full_name}</p>
                <p className="text-xs text-slate-400 mb-3">{user?.email}</p>
                <button
                  onClick={() => logout()}
                  className="w-full flex items-center justify-center space-x-2 py-2 text-xs font-bold text-red-600 bg-red-50 rounded-xl"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Log out</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Dynamic Role Page Content */}
        <main className="flex-1 min-w-0">
          {children}
        </main>
      </div>
    </div>
  )
}
