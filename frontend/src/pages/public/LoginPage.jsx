import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  GraduationCap,
  ArrowRight,
  ShieldCheck
} from 'lucide-react'
import AuthLayout from '@/components/layout/AuthLayout'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { useLogin } from '@/hooks/useAuth'

const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const { mutate: login, isPending } = useLogin()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  const onSubmit = (data) => {
    login({
      email: data.email.trim().toLowerCase(),
      password: data.password,
    })
  }

  return (
    <AuthLayout
      title="Institutional Portal Sign In"
      subtitle="Access your dedicated laboratory management dashboard."
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {/* Email */}
        <div>
          <Input
            label="Institutional or Authorized Email"
            type="email"
            placeholder="e.g. priya.ug.25.cs@francisxavier.ac.in"
            required
            leftIcon={<Mail className="w-4 h-4" />}
            error={errors.email?.message}
            {...register('email')}
          />
          <p className="text-[11px] text-slate-500 mt-1">
            Students: <span className="font-mono text-slate-700">studentname.ug.YY.DD@francisxavier.ac.in</span>
          </p>
        </div>

        {/* Password */}
        <div>
          <Input
            label="Password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Enter your account password"
            required
            leftIcon={<Lock className="w-4 h-4" />}
            rightIcon={
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="cursor-pointer hover:text-slate-600 transition-colors"
                tabIndex={-1}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            }
            error={errors.password?.message}
            {...register('password')}
          />
          <div className="flex justify-end mt-1.5">
            <Link
              to="/forgot-password"
              className="text-xs text-primary-600 hover:text-primary-700 font-medium transition-colors"
            >
              Forgot password?
            </Link>
          </div>
        </div>

        {/* Submit */}
        <Button type="submit" fullWidth size="lg" loading={isPending}>
          {isPending ? 'Authenticating…' : 'Sign In to Portal'}
        </Button>
      </form>

      {/* Institutional Student Registration Link */}
      <div className="mt-5 pt-4 border-t border-slate-200">
        <div className="p-3 bg-blue-50/70 rounded-xl border border-blue-100 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <GraduationCap className="w-5 h-5 text-primary-600" />
            <div>
              <p className="text-xs font-bold text-slate-900">New Student?</p>
              <p className="text-[11px] text-slate-500">Register with your institutional email</p>
            </div>
          </div>
          <Link
            to="/register"
            className="px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white text-xs font-bold rounded-lg shadow-sm transition-all flex items-center gap-1"
          >
            <span>Register</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      </div>

      {/* Security notice */}
      <div className="mt-4 text-center">
        <p className="text-[10px] text-slate-400 inline-flex items-center gap-1">
          <ShieldCheck className="w-3 h-3 text-slate-400" />
          Role authorization is cryptographically verified by JWT upon sign in.
        </p>
      </div>
    </AuthLayout>
  )
}
