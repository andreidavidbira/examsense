/*
ExamSense+ - Navbar Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste bara principala de navigatie a aplicatiei
- afiseaza linkurile importante in functie de autentificare si rol
- permite logout cu confirmare explicita
- gestioneaza meniul mobil pentru ecranele mici
*/

import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  BookOpenCheck,
  BrainCircuit,
  FileText,
  History,
  LogOut,
  Menu,
  Shield,
  Sparkles,
  UserCircle2,
  X,
} from 'lucide-react'

import ConfirmDialog from '../common/ConfirmDialog'
import MobileMenu from './MobileMenu'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import { secondaryButtonClass } from '../../utils/buttonClasses'

// bara de navigatie principala afiseaza meniul potrivit pentru utilizatorul curent
export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()

  const [mobileOpen, setMobileOpen] = useState(false)
  const [confirmLogoutOpen, setConfirmLogoutOpen] = useState(false)

  // definim linkurile principale afisate in meniu
  const navItems = [
    { to: '/documents', label: 'Documente', icon: FileText },
    { to: '/dashboard', label: 'Progres', icon: BrainCircuit },
    { to: '/quiz-history', label: 'Istoric', icon: History },
    { to: '/recommendations', label: 'Recomandări', icon: Sparkles },
    { to: '/profile', label: 'Profil', icon: UserCircle2 },
  ]

  // daca utilizatorul este admin, afisam si accesul catre panoul special
  if (user?.is_staff) {
    navItems.push({ to: '/admin-panel', label: 'Admin', icon: Shield })
  }

  // confirmam logout-ul si inchidem meniurile deschise
  async function handleLogoutConfirmed() {
    await logout()
    setMobileOpen(false)
    setConfirmLogoutOpen(false)
    showToast('Te-ai deconectat cu succes.', 'success')
    navigate('/login')
  }

  return (
    <>
      <ConfirmDialog
        open={confirmLogoutOpen}
        title="Deconectare"
        description="Sigur vrei să te deconectezi din cont?"
        confirmText="Logout"
        cancelText="Rămân conectat"
        onConfirm={handleLogoutConfirmed}
        onCancel={() => setConfirmLogoutOpen(false)}
        variant="primary"
      />

      <header className="sticky top-0 z-50 border-b border-white/60 bg-white/70 backdrop-blur-2xl">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <motion.div
              whileHover={{ scale: 1.04 }}
              className="flex h-11 w-11 items-center justify-center rounded-2xl bg-linear-to-br from-brand-500 via-violet-500 to-sky-500 text-white shadow-lg"
            >
              <BookOpenCheck size={22} />
            </motion.div>

            <div>
              <p className="text-base font-semibold tracking-tight text-slate-950">ExamSense+</p>
              <p className="text-xs text-slate-500">Smart exam preparation</p>
            </div>
          </Link>

          {isAuthenticated && (
            <nav className="hidden items-center gap-2 xl:flex">
              {navItems.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `inline-flex items-center gap-2 rounded-2xl px-4 py-2.5 text-sm font-medium transition ${
                      isActive
                        ? 'bg-slate-900 text-white shadow-sm'
                        : 'text-slate-600 hover:bg-brand-50 hover:text-brand-700'
                    }`
                  }
                >
                  <Icon size={16} />
                  {label}
                </NavLink>
              ))}
            </nav>
          )}

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <div className="hidden text-right sm:block">
                  <p className="text-sm font-medium text-slate-900">{user?.username}</p>
                  <p className="text-xs text-slate-500">
                    {[user?.first_name, user?.last_name].filter(Boolean).join(' ') || 'Profil utilizator'}
                  </p>
                </div>

                <button
                  onClick={() => setConfirmLogoutOpen(true)}
                  className={`hidden xl:inline-flex xl:items-center xl:gap-2 ${secondaryButtonClass}`}
                >
                  <LogOut size={16} />
                  Logout
                </button>

                {/* pe mobil deschidem sau inchidem meniul lateral */}
                <button
                  onClick={() => setMobileOpen((prev) => !prev)}
                  className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-700 transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700 xl:hidden"
                >
                  {mobileOpen ? <X size={18} /> : <Menu size={18} />}
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="rounded-2xl border border-slate-950 bg-slate-950 px-4 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:border-brand-600 hover:bg-brand-600 hover:shadow-lg active:scale-[0.98]"
              >
                Login
              </Link>
            )}
          </div>
        </div>

        {isAuthenticated && (
          <MobileMenu
            open={mobileOpen}
            items={navItems}
            onClose={() => setMobileOpen(false)}
            onLogout={() => setConfirmLogoutOpen(true)}
            user={user}
          />
        )}
      </header>
    </>
  )
}