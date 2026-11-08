import axiosClient from './axiosClient'

export const dashboardApi = {
  // Common summary endpoint that responds according to the caller's role
  getSummary: () => axiosClient.get('/users/stats/summary'),

  // Super Admin Endpoints
  getUsers: (params) => axiosClient.get('/users', { params }),
  toggleUserActive: (userId) => axiosClient.patch(`/users/${userId}/toggle-active`),
  getDepartments: (params) => axiosClient.get('/departments', { params }),
  getLabs: (params) => axiosClient.get('/labs', { params }),

  // Equipment Endpoints
  getEquipment: (params) => axiosClient.get('/equipment', { params }),
  getEquipmentDetail: (id) => axiosClient.get(`/equipment/${id}`),
  getCategories: () => axiosClient.get('/equipment/categories'),
  createEquipment: (data) => axiosClient.post('/equipment', data),
  updateEquipmentStatus: (id, status) => axiosClient.patch(`/equipment/${id}/status`, { status }),

  // Bookings & QR Endpoints
  getBookings: (params) => axiosClient.get('/bookings', { params }),
  createBooking: (data) => axiosClient.post('/bookings', data),
  approveBooking: (id) => axiosClient.patch(`/bookings/${id}/approve`),
  rejectBooking: (id, reason) => axiosClient.patch(`/bookings/${id}/reject`, { reason }),
  cancelBooking: (id) => axiosClient.patch(`/bookings/${id}/cancel`),
  checkinBooking: (id, qrToken) => axiosClient.post(`/bookings/${id}/checkin`, { qr_token: qrToken }),
  checkoutBooking: (id) => axiosClient.post(`/bookings/${id}/checkout`),

  // Damage Reports Endpoints
  getDamageReports: (params) => axiosClient.get('/damage-reports', { params }),
  createDamageReport: (data) => axiosClient.post('/damage-reports', data),
  resolveDamageReport: (id, data) => axiosClient.patch(`/damage-reports/${id}/resolve`, data),

  // Maintenance Tasks Endpoints
  getMaintenance: (params) => axiosClient.get('/maintenance', { params }),
  createMaintenance: (data) => axiosClient.post('/maintenance', data),
  updateMaintenanceStatus: (id, status, notes) => axiosClient.patch(`/maintenance/${id}/status`, { status, notes }),
}

