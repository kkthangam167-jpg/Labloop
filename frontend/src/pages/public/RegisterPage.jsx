import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  GraduationCap,
  Mail,
  Lock,
  Eye,
  EyeOff,
  User,
  Calendar,
  Building,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
  KeyRound,
  RotateCw,
  ArrowLeft,
  AlertTriangle
} from 'lucide-react'
import toast from 'react-hot-toast'
import AuthLayout from '@/components/layout/AuthLayout'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { authApi } from '@/api/auth.api'

const INSTITUTIONAL_DOMAIN = 'francisxavier.ac.in'
const STUDENT_EMAIL_REGEX = /^[a-z0-9]+(?:\.[a-z0-9]+)*\.ug\.\d{2}\.[a-z]{2,}@francisxavier\.ac\.in$/

const DEPARTMENTS = [
  { code: 'CS', name: 'Computer Science & Engineering' },
  { code: 'EC', name: 'Electronics & Communication Engineering' },
  { code: 'AI', name: 'Artificial Intelligence & Data Science' },
  { code: 'IT', name: 'Information Technology' },
  { code: 'ME', name: 'Mechanical Engineering' },
  { code: 'EE', name: 'Electrical & Electronics Engineering' },
  { code: 'CE', name: 'Civil Engineering' },
]

const ADMISSION_YEARS = ['23', '24', '25', '26', '27']

const studentRegisterSchema = z
  .object({
    full_name: z
      .string()
      .min(2, 'Full name must be at least 2 characters')
      .max(100, 'Full name is too long'),
    admission_year: z
      .string()
      .regex(/^\d{2}$/, 'Admission year must be a 2-digit code (e.g. 25, 26)'),
    department_code: z
      .string()
      .min(2, 'Select your department'),
    email: z
      .string()
      .min(1, 'Institutional email is required')
      .toLowerCase()
      .refine(
        (val) => STUDENT_EMAIL_REGEX.test(val),
        'Must follow format: studentname.ug.YY.DD@francisxavier.ac.in'
      ),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Za-z]/, 'Password must contain at least one letter')
      .regex(/\d/, 'Password must contain at least one number'),
    confirm_password: z.string().min(1, 'Confirm your password'),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

export default function RegisterPage() {
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [autoEmailEnabled, setAutoEmailEnabled] = useState(true)

  // Registration step: 'form' | 'otp'
  const [step, setStep] = useState('form')
  const [registeredEmail, setRegisteredEmail] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [isSubmittingForm, setIsSubmittingForm] = useState(false)
  const [isVerifyingOtp, setIsVerifyingOtp] = useState(false)
  const [isResendingOtp, setIsResendingOtp] = useState(false)
  const [smtpConfigured, setSmtpConfigured] = useState(true)
  const [smtpErrorMessage, setSmtpErrorMessage] = useState('')
  const [devOtp, setDevOtp] = useState('')

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(studentRegisterSchema),
    defaultValues: {
      full_name: '',
      admission_year: '25',
      department_code: 'CS',
      email: '',
      password: '',
      confirm_password: '',
    },
  })

  const fullName = watch('full_name')
  const admissionYear = watch('admission_year')
  const deptCode = watch('department_code')
  const currentEmail = watch('email')

  // Auto-generate dynamic institutional email when Name, Year, or Department changes
  useEffect(() => {
    if (autoEmailEnabled && fullName && admissionYear && deptCode) {
      const cleanName = fullName
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, '')
        .split(/\s+/)
        .slice(0, 2)
        .join('.')

      if (cleanName) {
        const generatedEmail = `${cleanName}.ug.${admissionYear}.${deptCode.toLowerCase()}@${INSTITUTIONAL_DOMAIN}`
        setValue('email', generatedEmail, { shouldValidate: true })
      }
    }
  }, [fullName, admissionYear, deptCode, autoEmailEnabled, setValue])

  const onRegisterSubmit = async (data) => {
    setIsSubmittingForm(true)
    setSmtpErrorMessage('')
    try {
      const payload = {
        full_name: data.full_name,
        admission_year: data.admission_year,
        department_code: data.department_code,
        email: data.email.toLowerCase().trim(),
        password: data.password,
        confirm_password: data.confirm_password,
      }

      const res = await authApi.register(payload)
      setRegisteredEmail(data.email.toLowerCase().trim())
      setSmtpConfigured(res.data?.data?.smtp_configured ?? true)
      if (res.data?.data?.dev_otp) setDevOtp(res.data.data.dev_otp)
      setStep('otp')
      toast.success(res.data?.message || 'Verification OTP code dispatched!')
    } catch (err) {
      const errData = err.response?.data
      // If user was created but SMTP delivery failed (status 503)
      if (err.response?.status === 503 || errData?.requires_otp || errData?.data?.requires_otp) {
        setRegisteredEmail(data.email.toLowerCase().trim())
        setSmtpConfigured(false)
        setSmtpErrorMessage(errData?.message || 'SMTP is not configured in backend/.env.')
        const foundOtp = errData?.dev_otp || errData?.data?.dev_otp
        if (foundOtp) setDevOtp(foundOtp)
        setStep('otp')
        toast.error('Account saved, but SMTP email delivery is unconfigured on the server.')
      } else {
        toast.error(errData?.message || 'Registration failed. Please check the form.')
      }
    } finally {
      setIsSubmittingForm(false)
    }
  }

  const handleVerifyOtp = async (e) => {
    e.preventDefault()
    if (!otpCode || otpCode.trim().length < 6) {
      toast.error('Please enter the complete 6-digit OTP code.')
      return
    }

    setIsVerifyingOtp(true)
    try {
      const res = await authApi.verifyOtp({
        email: registeredEmail,
        otp: otpCode.trim(),
      })

      if (res.data?.success) {
        toast.success('Institutional email verified! Account activated.')
        navigate('/login')
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Invalid or expired OTP code.')
    } finally {
      setIsVerifyingOtp(false)
    }
  }

  const handleResendOtp = async () => {
    setIsResendingOtp(true)
    try {
      const res = await authApi.resendOtp(registeredEmail)
      if (res.data?.success) {
        toast.success('A fresh verification code has been dispatched to your inbox.')
        setSmtpConfigured(true)
        setSmtpErrorMessage('')
        if (res.data?.data?.dev_otp) setDevOtp(res.data.data.dev_otp)
      }
    } catch (err) {
      const errData = err.response?.data
      const msg = errData?.message || 'Failed to resend verification code.'
      toast.error(msg)
      if (err.response?.status === 503) {
        setSmtpConfigured(false)
        setSmtpErrorMessage(msg)
        const foundOtp = errData?.dev_otp || errData?.data?.dev_otp
        if (foundOtp) setDevOtp(foundOtp)
      }
    } finally {
      setIsResendingOtp(false)
    }
  }

  const isEmailValid = STUDENT_EMAIL_REGEX.test(currentEmail || '')

  return (
    <AuthLayout
      title={step === 'form' ? 'Student Registration' : 'Email OTP Verification'}
      subtitle={
        step === 'form'
          ? 'Create your institutional account for academic laboratory access.'
          : 'Verify email ownership to activate your laboratory access.'
      }
    >
      {step === 'form' ? (
        <form onSubmit={handleSubmit(onRegisterSubmit)} className="space-y-4" noValidate>
          {/* Full Name */}
          <Input
            label="Student Full Name"
            type="text"
            placeholder="e.g. Priya Sharma"
            required
            leftIcon={<User className="w-4 h-4" />}
            error={errors.full_name?.message}
            {...register('full_name')}
          />

          {/* Admission Year & Department Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Admission Year <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Calendar className="w-4 h-4 absolute left-3 top-3 text-slate-400 pointer-events-none" />
                <select
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-300 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  {...register('admission_year')}
                >
                  {ADMISSION_YEARS.map((yr) => (
                    <option key={yr} value={yr}>
                      20{yr} (Batch '{yr}')
                    </option>
                  ))}
                </select>
              </div>
              {errors.admission_year && (
                <p className="text-[11px] text-red-500 mt-1">{errors.admission_year.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Department <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Building className="w-4 h-4 absolute left-3 top-3 text-slate-400 pointer-events-none" />
                <select
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-300 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  {...register('department_code')}
                >
                  {DEPARTMENTS.map((d) => (
                    <option key={d.code} value={d.code}>
                      {d.code} – {d.name}
                    </option>
                  ))}
                </select>
              </div>
              {errors.department_code && (
                <p className="text-[11px] text-red-500 mt-1">{errors.department_code.message}</p>
              )}
            </div>
          </div>

          {/* Institutional Email */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold text-slate-700">
                Institutional Email <span className="text-red-500">*</span>
              </label>
              <button
                type="button"
                onClick={() => setAutoEmailEnabled((v) => !v)}
                className="text-[10px] text-primary-600 hover:text-primary-700 font-semibold cursor-pointer"
              >
                {autoEmailEnabled ? 'Edit manually' : 'Auto-format'}
              </button>
            </div>

            <Input
              type="email"
              placeholder="studentname.ug.YY.DD@francisxavier.ac.in"
              required
              leftIcon={<Mail className="w-4 h-4" />}
              error={errors.email?.message}
              {...register('email')}
            />

            {/* Real-time Email Format Helper */}
            <div className="mt-1.5 flex items-center gap-1.5 text-[11px]">
              {isEmailValid ? (
                <span className="inline-flex items-center text-emerald-600 font-semibold gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Valid institutional format
                </span>
              ) : (
                <span className="inline-flex items-center text-slate-500 gap-1 font-mono text-[10px]">
                  <AlertCircle className="w-3 h-3 text-slate-400 shrink-0" />
                  Format: <strong>name.ug.YY.DD@francisxavier.ac.in</strong>
                </span>
              )}
            </div>
          </div>

          {/* Password */}
          <div>
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Min. 8 characters with letters & numbers"
              required
              leftIcon={<Lock className="w-4 h-4" />}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="cursor-pointer hover:text-slate-600 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              }
              error={errors.password?.message}
              {...register('password')}
            />
          </div>

          {/* Confirm Password */}
          <div>
            <Input
              label="Confirm Password"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Re-enter password"
              required
              leftIcon={<Lock className="w-4 h-4" />}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword((v) => !v)}
                  className="cursor-pointer hover:text-slate-600 transition-colors"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              }
              error={errors.confirm_password?.message}
              {...register('confirm_password')}
            />
          </div>

          {/* Verification Policy Notice */}
          <div className="p-3 bg-blue-50/70 rounded-xl border border-blue-100 flex items-start gap-2 text-[11px] text-blue-900 leading-relaxed">
            <ShieldCheck className="w-4 h-4 text-primary-600 shrink-0 mt-0.5" />
            <span>
              <strong>Email Ownership Verification:</strong> A 6-digit OTP will be sent to your institutional inbox. Accounts remain inactive until OTP verification is completed.
            </span>
          </div>

          {/* Submit */}
          <Button type="submit" fullWidth size="lg" loading={isSubmittingForm}>
            {isSubmittingForm ? 'Validating & Sending Code…' : 'Proceed to Email Verification'}
          </Button>
        </form>
      ) : (
        /* ── STEP 2: OTP Verification Screen ── */
        <form onSubmit={handleVerifyOtp} className="space-y-5" noValidate>
          <div className="text-center space-y-2">
            <div className="w-14 h-14 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center mx-auto">
              <KeyRound className="w-7 h-7" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Enter Verification Code</h3>
            <p className="text-xs text-slate-600">
              We sent a 6-digit OTP to your institutional email:
            </p>
            <p className="text-xs font-mono font-bold text-primary-700 bg-primary-50 py-1.5 px-3 rounded-lg border border-primary-200 inline-block">
              {registeredEmail}
            </p>
          </div>

          {/* SMTP Unconfigured Warning Banner */}
          {!smtpConfigured && (
            <div className="p-4 bg-amber-50/90 rounded-2xl border border-amber-200 text-left space-y-2.5">
              <div className="flex items-center gap-2 text-amber-900 font-bold text-xs">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>SMTP Mail Server Configuration Required</span>
              </div>
              <p className="text-[11px] text-amber-800 leading-relaxed">
                The student account was created, but real email delivery requires SMTP credentials configured in{' '}
                <strong className="font-mono">backend/.env</strong>. Per institutional security policy, OTP verification cannot be simulated.
              </p>
              <div className="p-2.5 bg-white/80 rounded-xl border border-amber-200 font-mono text-[10px] text-slate-700 space-y-0.5">
                <p># Add to backend/.env:</p>
                <p>MAIL_SERVER=smtp.gmail.com</p>
                <p>MAIL_PORT=587</p>
                <p>MAIL_USE_TLS=true</p>
                <p>MAIL_USERNAME=your-email@gmail.com</p>
                <p>MAIL_PASSWORD=your-app-password</p>
              </div>
              <p className="text-[10px] text-amber-700 italic">
                Once configured, click "Resend Code" to deliver the OTP to the student inbox.
              </p>
            </div>
          )}

          {/* Local Development Test OTP Auto-Fill Helper */}
          {devOtp && (
            <div className="p-3 bg-blue-50/90 border border-blue-200 rounded-2xl flex items-center justify-between text-xs shadow-xs">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 block">
                  Local Dev OTP Code:
                </span>
                <span className="font-mono font-black text-blue-900 text-sm tracking-widest">
                  {devOtp}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setOtpCode(devOtp)}
                className="px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-bold text-xs shadow-xs transition-colors cursor-pointer"
              >
                Auto-Fill Code
              </button>
            </div>
          )}

          {/* OTP Input */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider text-center mb-2">
              6-Digit One-Time Password
            </label>
            <input
              type="text"
              maxLength={6}
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
              placeholder="••••••"
              autoFocus
              className="w-full text-center tracking-[12px] text-2xl font-mono font-black py-3 px-4 rounded-xl border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-xs"
            />
            <p className="text-[11px] text-slate-400 text-center mt-1.5">
              Code expires in 15 minutes
            </p>
          </div>

          {/* Submit OTP */}
          <Button type="submit" fullWidth size="lg" loading={isVerifyingOtp}>
            {isVerifyingOtp ? 'Verifying OTP…' : 'Verify & Activate Account'}
          </Button>

          {/* Resend & Back buttons */}
          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={() => setStep('form')}
              className="text-xs text-slate-500 hover:text-slate-800 font-semibold inline-flex items-center gap-1 cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Edit Registration Details
            </button>

            <button
              type="button"
              onClick={handleResendOtp}
              disabled={isResendingOtp}
              className="text-xs text-primary-600 hover:text-primary-700 font-bold inline-flex items-center gap-1 cursor-pointer disabled:text-slate-400"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isResendingOtp ? 'animate-spin' : ''}`} />
              {isResendingOtp ? 'Resending…' : 'Resend Code'}
            </button>
          </div>
        </form>
      )}

      {/* Footer link to sign in */}
      <div className="mt-5 pt-4 border-t border-slate-200 text-center">
        <p className="text-xs text-slate-600">
          Already have an institutional account?{' '}
          <Link to="/login" className="font-bold text-primary-600 hover:text-primary-700 underline">
            Sign In
          </Link>
        </p>
      </div>
    </AuthLayout>
  )
}
