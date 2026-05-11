import { Link, useRouterState } from "@tanstack/react-router";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/utils/cn";
import styles from "@/components/layout/Sidebar/SidebarNavItem.module.css";

export function SidebarNavItem({
  to,
  icon: Icon,
  label,
  collapsed = false,
}: {
  to: string;
  icon: LucideIcon;
  label: string;
  collapsed?: boolean;
}) {
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const active = pathname === to || (to !== "/" && pathname.startsWith(to));

  return (
    <Link to={to} className={cn(styles.item, active && styles.active, collapsed && styles.collapsed)} title={label}>
      <Icon size={16} className={styles.icon} />
      <span className={cn(styles.label, collapsed && styles.labelHidden)}>{label}</span>
    </Link>
  );
}
