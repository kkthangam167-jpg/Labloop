import axiosClient from './axiosClient'

export const authApi = {
  register: (data) => axiosClient.post('/auth/register', data),
  verifyOtp: (data) => axiosClient.post('/auth/verify-otp', data),
  resendOtp: (email) => axiosClient.post('/auth/resend-otp', { email }),
  getSmtpStatus: () => axiosClient.get('/auth/smtp-status'),
  login: (data) => axiosClient.post('/auth/login', data),
  logout: (refreshToken) => axiosClient.post('/auth/logout', { refresh_token: refreshToken }),
  refreshToken: () => axiosClient.post('/auth/refresh'),
  getMe: () => axiosClient.get('/auth/me'),
  updateProfile: (data) => axiosClient.patch('/auth/me', data),
  changePassword: (data) => axiosClient.patch('/auth/me/password', data),
  forgotPassword: (email) => axiosClient.post('/auth/forgot-password', { email }),
  resetPassword: (data) => axiosClient.post('/auth/reset-password', data),
}
