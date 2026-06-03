/*
ExamSense+ - Button Style Helpers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste stilurile reutilizabile pentru butoanele din frontend
- centralizeaza clasele Tailwind pentru variantele principale, secundare si danger
- pastreaza consistenta vizuala a actiunilor din intreaga interfata
*/

// stilul principal folosit pentru actiunile importante din interfata
export const primaryButtonClass = [
  'rounded-2xl',
  'border',
  'border-slate-950',
  'bg-slate-950',
  'px-5',
  'py-3',
  'text-sm',
  'font-medium',
  'text-white',
  'shadow-sm',
  'transition-all',
  'duration-200',
  'hover:border-brand-600',
  'hover:bg-brand-600',
  'hover:text-white',
  'hover:shadow-lg',
  'active:scale-[0.98]',
  'active:border-brand-700',
  'active:bg-brand-700',
  'disabled:cursor-not-allowed',
  'disabled:opacity-60',
  'disabled:hover:border-slate-950',
  'disabled:hover:bg-slate-950',
].join(' ')

// stilul secundar folosit pentru actiuni neutre sau complementare
export const secondaryButtonClass = [
  'rounded-2xl',
  'border',
  'border-slate-200',
  'bg-white',
  'px-5',
  'py-3',
  'text-sm',
  'font-medium',
  'text-slate-700',
  'shadow-sm',
  'transition-all',
  'duration-200',
  'hover:border-brand-300',
  'hover:bg-brand-50',
  'hover:text-brand-700',
  'hover:shadow-md',
  'active:scale-[0.98]',
  'active:border-brand-400',
  'active:bg-brand-100',
].join(' ')

// stilul danger folosit pentru actiuni destructive sau sensibile
export const dangerButtonClass = [
  'rounded-2xl',
  'border',
  'border-rose-200',
  'bg-rose-50',
  'px-5',
  'py-3',
  'text-sm',
  'font-medium',
  'text-rose-700',
  'shadow-sm',
  'transition-all',
  'duration-200',
  'hover:border-rose-600',
  'hover:bg-rose-600',
  'hover:text-white',
  'hover:shadow-md',
  'active:scale-[0.98]',
  'active:bg-rose-700',
].join(' ')