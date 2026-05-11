import type { InputHTMLAttributes } from "react";

import { cn } from "@/utils/cn";
import styles from "@/components/primitives/Input/Input.module.css";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn(styles.input, props.className)} {...props} />;
}
