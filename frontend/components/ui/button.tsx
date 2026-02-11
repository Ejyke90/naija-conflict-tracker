import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-tactical-e-ink disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 typography-label",
  {
    variants: {
      variant: {
        default:
          "bg-tactical-slate-medium text-tactical-e-ink shadow-lg hover:bg-tactical-slate-light border border-tactical-slate-light/20",
        destructive:
          "signal-critical text-white shadow hover:opacity-90",
        outline:
          "border border-tactical-slate-light bg-transparent text-tactical-e-ink shadow hover:bg-tactical-slate-medium/20",
        secondary:
          "bg-tactical-slate-dark/50 text-tactical-e-ink/80 border border-tactical-slate-light/30 shadow hover:bg-tactical-slate-dark/70",
        ghost: "hover:bg-tactical-slate-medium/20 text-tactical-e-ink/80 hover:text-tactical-e-ink",
        link: "text-tactical-e-ink underline-offset-4 hover:underline",
        tactical_primary:
          "bg-tactical-navy text-tactical-e-ink shadow-lg border border-tactical-slate-light/30 hover:bg-tactical-charcoal",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
