/*
ExamSense+ - Frontend Application Router
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste toate rutele principale ale aplicatiei frontend
- leaga paginile publice, protejate si administrative
- aplica componentele de protectie pentru utilizatorii autentificati si admini
- centralizeaza navigarea aplicatiei intr-un singur punct
*/

import { Route, Routes } from 'react-router-dom'

import AppShell from '../components/layout/AppShell'
import ProtectedAdminRoute from '../components/layout/ProtectedAdminRoute'
import ProtectedRoute from '../components/layout/ProtectedRoute'

import AdminDashboardPage from '../pages/admin/AdminDashboardPage'
import HomePage from '../pages/HomePage'
import NotFoundPage from '../pages/NotFoundPage'

import ChangePasswordPage from '../pages/auth/ChangePasswordPage'
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage'
import LoginPage from '../pages/auth/LoginPage'
import ProfilePage from '../pages/auth/ProfilePage'
import RegisterPage from '../pages/auth/RegisterPage'
import ResetPasswordPage from '../pages/auth/ResetPasswordPage'

import DocumentDetailPage from '../pages/documents/DocumentDetailPage'
import DocumentsPage from '../pages/documents/DocumentsPage'
import UploadPage from '../pages/documents/UploadPage'

import DashboardPage from '../pages/learning/DashboardPage'
import RecommendationsPage from '../pages/learning/RecommendationsPage'
import RetryQuizPage from '../pages/learning/RetryQuizPage'
import WeakConceptsPage from '../pages/learning/WeakConceptsPage'

import QuizAttemptDetailPage from '../pages/quiz/QuizAttemptDetailPage'
import QuizHistoryPage from '../pages/quiz/QuizHistoryPage'
import QuizPlayPage from '../pages/quiz/QuizPlayPage'
import QuizResultPage from '../pages/quiz/QuizResultPage'

// router-ul principal defineste intreaga structura de navigare a aplicatiei
export default function AppRouter() {
  return (
    <AppShell>
      <Routes>
        {/* rute publice */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        {/* rute pentru contul utilizatorului autentificat */}
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

        {/* rute pentru documente */}
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

        {/* ruta pentru rezolvarea efectiva a unui quiz */}
        <Route
          path="/quiz/:questionSetId"
          element={
            <ProtectedRoute>
              <QuizPlayPage />
            </ProtectedRoute>
          }
        />

        {/* rute pentru dashboard-ul de invatare */}
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

        {/* rute pentru istoric si rezultat quiz */}
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

        {/* ruta administrativa, accesibila doar pentru admin */}
        <Route
          path="/admin-panel"
          element={
            <ProtectedAdminRoute>
              <AdminDashboardPage />
            </ProtectedAdminRoute>
          }
        />

        {/* fallback pentru rutele inexistente */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AppShell>
  )
}