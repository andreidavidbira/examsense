/*
ExamSense+ - Section Card Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste componenta reutilizabila pentru sectiunile mari din interfata
- afiseaza optional titlu, subtitlu si zona de actiuni in partea dreapta
- standardizeaza aspectul cardurilor principale folosite in pagini
*/

export default function SectionCard({
  title,
  subtitle,
  rightSlot,
  children,
  className = '',
  contentClassName = '',
}) {
  return (
    <section
      className={`overflow-hidden rounded-[30px] border border-slate-200/80 bg-white/95 shadow-sm backdrop-blur ${className}`}
    >
      {(title || subtitle || rightSlot) && (
        <div className="border-b border-slate-100 bg-linear-to-r from-white via-slate-50/70 to-white px-5 py-5 sm:px-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0">
              {title && (
                <h2 className="text-xl font-semibold tracking-tight text-slate-950 sm:text-2xl">
                  {title}
                </h2>
              )}

              {subtitle && (
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                  {subtitle}
                </p>
              )}
            </div>

            {rightSlot && (
              <div className="flex shrink-0 flex-wrap gap-2 lg:justify-end">
                {rightSlot}
              </div>
            )}
          </div>
        </div>
      )}

      <div className={`px-5 py-5 sm:px-6 ${contentClassName}`}>{children}</div>
    </section>
  )
}