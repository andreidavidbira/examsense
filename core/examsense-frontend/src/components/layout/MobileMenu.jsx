/*
ExamSense+ - Mobile Menu Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste meniul mobil folosit in zona de navigatie a aplicatiei
- afiseaza linkurile principale pe ecranele mici
- permite acces rapid la logout si la datele de baza ale utilizatorului
- anima aparitia si disparitia meniului pentru o experienta mai placuta
*/

import { AnimatePresence, motion } from 'framer-motion'
import { LogOut } from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { secondaryButtonClass } from '../../utils/buttonClasses'

// afisam meniul mobil atunci cand navbar-ul este deschis pe ecrane mici
export default function MobileMenu({ open, items, onClose, onLogout, user }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          className="border-t border-white/60 bg-white/90 px-4 py-4 backdrop-blur-2xl xl:hidden"
        >
          <div className="mb-4 rounded-2xl bg-slate-50 px-4 py-3">
            <p className="text-sm font-medium text-slate-900">{user?.username}</p>
            <p className="text-xs text-slate-500">
              {[user?.first_name, user?.last_name].filter(Boolean).join(' ') || 'Profil utilizator'}
            </p>
          </div>

          {/* afisam pe mobil aceleasi linkuri principale ca in navbarul mare */}
          <nav className="flex flex-col gap-2">
            {items.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                onClick={onClose}
                className={({ isActive }) =>
                  `inline-flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                    isActive
                      ? 'bg-slate-900 text-white'
                      : 'text-slate-700 hover:bg-brand-50 hover:text-brand-700'
                  }`
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}

            {/* butonul de logout ramane disponibil si in meniul mobil */}
            <button
              onClick={onLogout}
              className={`mt-2 inline-flex items-center justify-center gap-2 ${secondaryButtonClass}`}
            >
              <LogOut size={16} />
              Logout
            </button>
          </nav>
        </motion.div>
      )}
    </AnimatePresence>
  )
}