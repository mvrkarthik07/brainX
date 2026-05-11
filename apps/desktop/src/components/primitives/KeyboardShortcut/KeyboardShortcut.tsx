import styles from "@/components/primitives/KeyboardShortcut/KeyboardShortcut.module.css";

export function KeyboardShortcut({ keys, label }: { keys: string[]; label?: string }) {
  return (
    <span className={styles.shortcut}>
      {keys.map((key) => (
        <kbd key={key} className={styles.key}>
          {key}
        </kbd>
      ))}
      {label ? <span className={styles.label}>{label}</span> : null}
    </span>
  );
}
