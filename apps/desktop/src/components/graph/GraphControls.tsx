import { Minus, Plus, RotateCcw } from "lucide-react";

import { Button } from "@/components/primitives/Button/Button";
import styles from "@/components/graph/GraphControls.module.css";

export function GraphControls({
  hops,
  onChangeHops,
  onReset,
}: {
  hops: number;
  onChangeHops: (hops: number) => void;
  onReset: () => void;
}) {
  return (
    <div className={styles.controls}>
      <Button variant="ghost" onClick={() => onChangeHops(Math.max(1, hops - 1))}>
        <Minus size={14} />
        Depth
      </Button>
      <Button variant="ghost" onClick={() => onChangeHops(Math.min(5, hops + 1))}>
        <Plus size={14} />
        Depth
      </Button>
      <Button variant="ghost" onClick={onReset}>
        <RotateCcw size={14} />
        Reset
      </Button>
    </div>
  );
}
