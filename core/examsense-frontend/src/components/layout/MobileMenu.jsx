import { NavLink } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { LogOut } from 'lucide-react'
import { secondaryButtonClass } from '../../utils/buttonClasses'

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