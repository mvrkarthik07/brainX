import { useMemo, useState } from "react";

import { GraphCanvas } from "@/components/graph/GraphCanvas";
import { GraphControls } from "@/components/graph/GraphControls";
import { GraphLegend } from "@/components/graph/GraphLegend";
import { NodeTooltip } from "@/components/graph/NodeTooltip";
import { Button } from "@/components/primitives/Button/Button";
import { Input } from "@/components/primitives/Input/Input";
import { useGraph } from "@/hooks/useGraph";
import { useGraphStore } from "@/store";
import styles from "@/views/GraphView/GraphView.module.css";

export function GraphView() {
  const [centerInput, setCenterInput] = useState("user:default");
  const centerNodeId = useGraphStore((state) => state.centerNodeId);
  const setCenterNodeId = useGraphStore((state) => state.setCenterNodeId);
  const selectedNodeId = useGraphStore((state) => state.selectedNodeId);
  const nodes = useGraphStore((state) => state.nodes);
  const focusDepth = useGraphStore((state) => state.focusDepth);
  const setFocusDepth = useGraphStore((state) => state.setFocusDepth);
  const query = useGraph(centerNodeId, focusDepth, 120);

  const selectedNode = useMemo(
    () => nodes.find((node) => node.id === selectedNodeId) ?? null,
    [nodes, selectedNodeId],
  );

  return (
    <div className={styles.view}>
      <div className={styles.topbar}>
        <div>
          <div className={styles.subtitle}>Neural map</div>
          <div className={styles.title}>Graph Explorer</div>
        </div>
        <div className={styles.inputRow}>
          <Input value={centerInput} onChange={(event) => setCenterInput(event.target.value)} placeholder="user:default or node id" />
          <Button variant="primary" onClick={() => setCenterNodeId(centerInput.trim() || "user:default")}>
            Focus
          </Button>
        </div>
      </div>
      <div className={styles.body}>
        <div className={styles.canvasWrap}>
          <div className={styles.canvasCard}>
            <GraphCanvas />
            {query.isLoading ? (
              <div className={styles.canvasLoading}>
                <div className={styles.canvasLoadingCard}>
                  <div className={styles.canvasLoadingTitle}>Loading neighborhood</div>
                  <div>Fetching the local graph neighborhood and stabilizing the map.</div>
                </div>
              </div>
            ) : null}
            {!query.isLoading && nodes.length === 0 ? (
              <div className={styles.canvasEmpty}>
                <div className={styles.canvasEmptyCard}>
                  <div className={styles.canvasEmptyTitle}>Ingest documents to build your graph</div>
                  <div>The graph explorer shows real local neighborhood data once BrainX has indexed documents and concepts.</div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
        <aside className={styles.details}>
          <div className={styles.detailsHeading}>Node detail</div>
          <NodeTooltip node={selectedNode} />
        </aside>
      </div>
      <div className={styles.footer}>
        <GraphLegend />
        <GraphControls hops={focusDepth} onChangeHops={setFocusDepth} onReset={() => setCenterNodeId("user:default")} />
        <div>{query.isLoading ? "Loading neighborhood..." : `${nodes.length} nodes loaded`}</div>
      </div>
    </div>
  );
}
