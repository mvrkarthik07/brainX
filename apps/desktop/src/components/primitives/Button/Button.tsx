import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

import { cn } from "@/utils/cn";
import styles from "@/components/primitives/Button/Button.module.css";

type Variant = "primary" | "ghost" | "danger" | "icon";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export function Button({
  variant = "ghost",
  className,
  children,
  ...props
}: PropsWithChildren<ButtonProps>) {
  return (
    <button className={cn(styles.button, styles[variant], className)} {...props}>
      {children}
    </button>
  );
}
