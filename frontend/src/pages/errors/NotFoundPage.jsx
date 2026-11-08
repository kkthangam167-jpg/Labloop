import React from 'react'
import { Link } from 'react-router-dom'
import { FileQuestion, Home } from 'lucide-react'
import Button from '@/components/ui/Button'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="w-16 h-16 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center mx-auto mb-6 shadow-sm">
          <FileQuestion className="w-8 h-8" />
        </div>
        <span className="text-sm font-semibold tracking-wider text-primary-600 uppercase">404 Error</span>
        <h1 className="text-3xl font-bold text-slate-900 mt-2 mb-3">Page Not Found</h1>
        <p className="text-slate-600 text-sm leading-relaxed mb-6">
          The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
        </p>
        <Link to="/">
          <Button variant="primary" leftIcon={<Home className="w-4 h-4" />}>
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  )
}

