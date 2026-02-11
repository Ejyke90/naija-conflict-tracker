import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 typography-label",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-tactical-slate-medium text-tactical-e-ink shadow hover:bg-tactical-slate-light",
        secondary:
          "border-tactical-slate-light bg-tactical-slate-dark/50 text-tactical-e-ink/80 hover:bg-tactical-slate-dark/70",
        destructive:
          "border-transparent signal-critical text-white shadow hover:opacity-80",
        outline: "border-tactical-slate-light text-tactical-e-ink bg-transparent",
        signal_critical:
          "border-transparent signal-critical text-white shadow hover:opacity-80",
        signal_high:
          "border-transparent signal-high text-white shadow hover:opacity-80",
        signal_medium:
          "border-transparent signal-medium text-white shadow hover:opacity-80",
        signal_low:
          "border-transparent signal-low text-white shadow hover:opacity-80",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
