import { getCurrentWindow } from "@tauri-apps/api/window";
import type { MouseEvent } from "react";

import styles from "@/components/layout/TopBar/TopBar.module.css";

async function safeWindowAction(action: "close" | "minimize" | "toggleMaximize") {
  try {
    const currentWindow = getCurrentWindow();
    await currentWindow[action]();
  } catch {
    // Browser dev mode is allowed to no-op here.
  }
}

function isInteractiveTarget(target: EventTarget | null) {
  return target instanceof HTMLElement && Boolean(target.closest("button, a, input, textarea, select"));
}

async function handleTitlebarMouseDown(event: MouseEvent<HTMLDivElement>) {
  if (event.button !== 0 || isInteractiveTarget(event.target)) {
    return;
  }

  try {
    await getCurrentWindow().startDragging();
  } catch {
    // Browser dev mode is allowed to no-op here.
  }
}

async function handleTitlebarDoubleClick(event: MouseEvent<HTMLDivElement>) {
  if (isInteractiveTarget(event.target)) {
    return;
  }

  await safeWindowAction("toggleMaximize");
}

export function TitleBar() {
  return (
    <div className={styles.titlebar}>
      <div className={styles.windowControls}>
        <button
          className={`${styles.control} ${styles.close}`}
          onClick={() => void safeWindowAction("close")}
          aria-label="Close window"
        />
        <button
          className={`${styles.control} ${styles.minimize}`}
          onClick={() => void safeWindowAction("minimize")}
          aria-label="Minimize window"
        />
        <button
          className={`${styles.control} ${styles.maximize}`}
          onClick={() => void safeWindowAction("toggleMaximize")}
          aria-label="Maximize window"
        />
      </div>

      <div
        className={styles.center}
        data-tauri-drag-region
        onMouseDown={(event) => void handleTitlebarMouseDown(event)}
        onDoubleClick={(event) => void handleTitlebarDoubleClick(event)}
      >
        <span className={styles.logo}>brainX</span>
      </div>

      <div
        className={styles.right}
        data-tauri-drag-region
        onMouseDown={(event) => void handleTitlebarMouseDown(event)}
        onDoubleClick={(event) => void handleTitlebarDoubleClick(event)}
      />
    </div>
  );
}
