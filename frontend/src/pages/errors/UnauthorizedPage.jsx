import React from 'react'
import { Link } from 'react-router-dom'
import { ShieldAlert, Home, LogIn } from 'lucide-react'
import Button from '@/components/ui/Button'
import useAuthStore from '@/store/authStore'

export default function UnauthorizedPage() {
  const { isAuthenticated, user } = useAuthStore()

  const getDashboardLink = () => {
    if (!user) return '/login'
    if (user.role === 'super_admin') return '/admin/dashboard'
    if (user.role === 'lab_incharge') return '/incharge/dashboard'
    return '/student/dashboard'
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="w-16 h-16 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center mx-auto mb-6 shadow-sm">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <span className="text-sm font-semibold tracking-wider text-amber-600 uppercase">403 Access Denied</span>
        <h1 className="text-3xl font-bold text-slate-900 mt-2 mb-3">Unauthorized Access</h1>
        <p className="text-slate-600 text-sm leading-relaxed mb-6">
          You do not have permission to view this section of LabLoop. Please sign in with an account that has appropriate administrative privileges.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link to="/">
            <Button variant="outline" leftIcon={<Home className="w-4 h-4" />}>
              Home
            </Button>
          </Link>
          <Link to={getDashboardLink()}>
            <Button variant="primary" leftIcon={<LogIn className="w-4 h-4" />}>
              {isAuthenticated ? 'My Dashboard' : 'Sign In'}
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}

