import styles from "@/components/primitives/StatusDot/StatusDot.module.css";

export function StatusDot({ status }: { status: "active" | "loading" | "error" }) {
  return <span className={styles.statusDot} data-status={status} aria-hidden="true" />;
}
