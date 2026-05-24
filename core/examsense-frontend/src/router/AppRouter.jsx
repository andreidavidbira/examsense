import { Routes, Route } from 'react-router-dom'
import AppShell from '../components/layout/AppShell'
import ProtectedRoute from '../components/layout/ProtectedRoute'
import ProtectedAdminRoute from '../components/layout/ProtectedAdminRoute'

import HomePage from '../pages/HomePage'
import NotFoundPage from '../pages/NotFoundPage'

import LoginPage from '../pages/auth/LoginPage'
import RegisterPage from '../pages/auth/RegisterPage'
import ProfilePage from '../pages/auth/ProfilePage'
import ChangePasswordPage from '../pages/auth/ChangePasswordPage'
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '../pages/auth/ResetPasswordPage'

import DocumentsPage from '../pages/documents/DocumentsPage'
import UploadPage from '../pages/documents/UploadPage'
import DocumentDetailPage from '../pages/documents/DocumentDetailPage'

import DashboardPage from '../pages/learning/DashboardPage'
import WeakConceptsPage from '../pages/learning/WeakConceptsPage'
import RecommendationsPage from '../pages/learning/RecommendationsPage'
import RetryQuizPage from '../pages/learning/RetryQuizPage'

import QuizPlayPage from '../pages/quiz/QuizPlayPage'
import QuizResultPage from '../pages/quiz/QuizResultPage'
import QuizHistoryPage from '../pages/quiz/QuizHistoryPage'
import QuizAttemptDetailPage from '../pages/quiz/QuizAttemptDetailPage'

import AdminDashboardPage from '../pages/admin/AdminDashboardPage'

export default function AppRouter() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<HomePage />} />

        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/change-password"
          element={
            <ProtectedRoute>
              <ChangePasswordPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/documents"
          element={
            <ProtectedRoute>
              <DocumentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents/upload"
          element={
            <ProtectedRoute>
              <UploadPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents/:id"
          element={
            <ProtectedRoute>
              <DocumentDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents/:id/quiz"
          element={
            <ProtectedRoute>
              <QuizPlayPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/weak-concepts"
          element={
            <ProtectedRoute>
              <WeakConceptsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recommendations"
          element={
            <ProtectedRoute>
              <RecommendationsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/retry-quiz"
          element={
            <ProtectedRoute>
              <RetryQuizPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/quiz-result"
          element={
            <ProtectedRoute>
              <QuizResultPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/quiz-history"
          element={
            <ProtectedRoute>
              <QuizHistoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/quiz-history/:attemptId"
          element={
            <ProtectedRoute>
              <QuizAttemptDetailPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin-panel"
          element={
            <ProtectedAdminRoute>
              <AdminDashboardPage />
            </ProtectedAdminRoute>
          }
        />

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AppShell>
  )
}