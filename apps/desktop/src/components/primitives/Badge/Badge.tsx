import type { PropsWithChildren } from "react";

import { cn } from "@/utils/cn";
import styles from "@/components/primitives/Badge/Badge.module.css";

export function Badge({
  children,
  accent = false,
  className,
}: PropsWithChildren<{ accent?: boolean; className?: string }>) {
  return <span className={cn(styles.badge, accent && styles.accent, className)}>{children}</span>;
}
