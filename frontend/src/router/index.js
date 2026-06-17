import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue') },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue') },
  {
    path: '/group/apply',
    name: 'group-apply',
    component: () => import('../views/group/GroupApply.vue'),
  },
  {
    path: '/group/query',
    name: 'group-query',
    component: () => import('../views/group/GroupQuery.vue'),
  },
  {
    path: '/user',
    component: () => import('../views/user/UserLayout.vue'),
    meta: { requiresAuth: true, role: 'user' },
    children: [
      { path: '', redirect: '/user/center' },
      { path: 'center', name: 'user-center', component: () => import('../views/user/Center.vue') },
      { path: 'profile', name: 'user-profile', component: () => import('../views/user/Profile.vue') },
      { path: 'appointment', name: 'user-appointment', component: () => import('../views/user/AppointmentCreate.vue') },
      { path: 'appointments', name: 'user-appointments', component: () => import('../views/user/MyAppointments.vue') },
      { path: 'health-survey', name: 'user-health', component: () => import('../views/user/HealthSurvey.vue') },
      { path: 'feedback', name: 'user-feedback', component: () => import('../views/user/Feedback.vue') },
      { path: 'evaluation', name: 'user-evaluation', component: () => import('../views/user/Evaluation.vue') },
    ],
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('../views/admin/AdminLogin.vue'),
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, staff: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'admin-dashboard', component: () => import('../views/admin/Dashboard.vue') },
      { path: 'appointments', name: 'admin-appointments', component: () => import('../views/admin/AppointmentManage.vue') },
      { path: 'health', name: 'admin-health', component: () => import('../views/admin/HealthManage.vue') },
      { path: 'groups', name: 'admin-groups', component: () => import('../views/admin/GroupManage.vue') },
      { path: 'feedbacks', name: 'admin-feedbacks', component: () => import('../views/admin/FeedbackManage.vue') },
      { path: 'evaluations', name: 'admin-evaluations', component: () => import('../views/admin/EvaluationManage.vue') },
      { path: 'external', name: 'admin-external', component: () => import('../views/admin/ExternalDemo.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const STAFF_ROLES = ['recruiter', 'collector', 'admin']

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  if (to.meta.requiresAuth) {
    if (!token) {
      return to.meta.staff ? '/admin/login' : '/login'
    }
    if (to.meta.staff && !STAFF_ROLES.includes(role)) {
      return '/user/center'
    }
    if (to.meta.role && role !== to.meta.role) {
      return STAFF_ROLES.includes(role) ? '/admin/dashboard' : '/user/center'
    }
  }
  return true
})

export default router
