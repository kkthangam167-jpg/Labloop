import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { authApi } from '@/api/auth.api'
import useAuthStore from '@/store/authStore'

export function useLogin() {
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (res) => {
      const { data } = res.data
      setAuth(data.user, data.access_token, data.refresh_token)
      toast.success(`Welcome back, ${data.user.full_name}!`)
      const role = data.user.role
      if (role === 'super_admin') navigate('/admin/dashboard')
      else if (role === 'lab_incharge') navigate('/incharge/dashboard')
      else navigate('/student/dashboard')
    },
    onError: (err) => {
      const message =
        err.response?.data?.message ||
        (err.message === 'Network Error'
          ? 'Cannot connect to backend server. Please verify backend is running on port 5000.'
          : err.message || 'Login failed. Please try again.')
      toast.error(message)
    },
  })
}

export function useRegister() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      toast.success('Account created! Please log in.')
      navigate('/login')
    },
    onError: (err) => {
      const message = err.response?.data?.message || 'Registration failed.'
      toast.error(message)
    },
  })
}

export function useLogout() {
  const { logout, refreshToken } = useAuthStore()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => authApi.logout(refreshToken),
    onSettled: () => {
      logout()
      queryClient.clear()
      navigate('/login')
      toast.success('Logged out successfully.')
    },
  })
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (email) => authApi.forgotPassword(email),
    onSuccess: () => {
      toast.success('If that email is registered, a reset link has been sent.')
    },
    onError: () => {
      // Show same message to prevent email enumeration
      toast.success('If that email is registered, a reset link has been sent.')
    },
  })
}

export function useResetPassword() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: authApi.resetPassword,
    onSuccess: () => {
      toast.success('Password reset successful! Please log in.')
      navigate('/login')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Reset failed. Link may have expired.')
    },
  })
}
