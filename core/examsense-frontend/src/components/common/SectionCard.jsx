import { motion } from 'framer-motion'

export default function SectionCard({ title, subtitle, rightSlot, children }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="rounded-[28px] border border-white/70 bg-white/80 p-5 shadow-[var(--shadow-soft)] backdrop-blur-xl sm:p-6 lg:p-8"
    >
      {(title || subtitle || rightSlot) && (
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            {title && <h2 className="text-2xl font-semibold tracking-tight text-slate-950">{title}</h2>}
            {subtitle && <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{subtitle}</p>}
          </div>
          {rightSlot}
        </div>
      )}

      {children}
    </motion.section>
  )
}