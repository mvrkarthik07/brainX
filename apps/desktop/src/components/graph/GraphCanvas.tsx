import * as d3 from "d3";
import { useEffect, useRef } from "react";

import { useGraphStore } from "@/store";
import type { GraphEdge, GraphNode } from "@/types/graph";
import { buildGraphData, getEdgeColor, getNodeColor, getNodeRadius } from "@/utils/graph";
import { truncate } from "@/utils/format";
import styles from "@/components/graph/GraphCanvas.module.css";

type SimulationNode = GraphNode & d3.SimulationNodeDatum;
type SimulationEdge = GraphEdge & d3.SimulationLinkDatum<SimulationNode>;

export function GraphCanvas() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const nodes = useGraphStore((state) => state.nodes);
  const edges = useGraphStore((state) => state.edges);
  const selectedNodeId = useGraphStore((state) => state.selectedNodeId);
  const selectNode = useGraphStore((state) => state.selectNode);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) {
      return;
    }

    const svg = d3.select(svgRef.current);
    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;
    svg.selectAll("*").remove();

    svg.append("rect").attr("width", width).attr("height", height).attr("fill", "var(--graph-bg)");

    const { nodes: visibleNodes, edges: visibleEdges } = buildGraphData(nodes, edges, selectedNodeId);
    const simulationNodes = visibleNodes.map((node) => ({ ...node })) as SimulationNode[];
    const simulationEdges = visibleEdges.map((edge) => ({ ...edge })) as SimulationEdge[];

    const container = svg.append("g").attr("class", "graph-container");
    svg.call(
      d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.2, 4]).on("zoom", (event) => {
        container.attr("transform", event.transform.toString());
      }),
    );

    const simulation = d3
      .forceSimulation<SimulationNode>(simulationNodes)
      .force(
        "link",
        d3
          .forceLink<SimulationNode, SimulationEdge>(simulationEdges)
          .id((node) => node.id)
          .distance((edge) => 90 / (edge.weight + 0.1))
          .strength((edge) => Math.min(edge.weight * 0.45, 0.85)),
      )
      .force("charge", d3.forceManyBody<SimulationNode>().strength((node) => (node.type === "metanode" ? -300 : -120)))
      .force("collision", d3.forceCollide<SimulationNode>().radius((node) => getNodeRadius(node) + 10))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .alphaDecay(0.04)
      .velocityDecay(0.4);

    const edgeElements = container
      .append("g")
      .selectAll("line")
      .data(simulationEdges)
      .enter()
      .append("line")
      .attr("stroke", (edge) => getEdgeColor(edge.weight))
      .attr("stroke-width", (edge) => Math.max(0.5, edge.weight * 2))
      .attr("stroke-opacity", (edge) => Math.min(0.8, 0.15 + edge.weight * 0.6));

    const nodeElements = container
      .append("g")
      .selectAll("g")
      .data(simulationNodes)
      .enter()
      .append("g")
      .attr("class", "node")
      .call(
        d3
          .drag<SVGGElement, SimulationNode>()
          .on("start", (event, node) => {
            if (!event.active) {
              simulation.alphaTarget(0.3).restart();
            }
            node.fx = node.x;
            node.fy = node.y;
          })
          .on("drag", (event, node) => {
            node.fx = event.x;
            node.fy = event.y;
          })
          .on("end", (event, node) => {
            if (!event.active) {
              simulation.alphaTarget(0);
            }
            node.fx = null;
            node.fy = null;
          }),
      )
      .on("click", (event, node) => {
        event.stopPropagation();
        selectNode(node.id === selectedNodeId ? null : node.id);
      });

    nodeElements
      .append("circle")
      .attr("r", (node) => getNodeRadius(node) + 5)
      .attr("fill", "none")
      .attr("stroke", (node) => getNodeColor(node.type))
      .attr("stroke-width", 1.5)
      .attr("opacity", (node) => (node.id === selectedNodeId ? 0.65 : 0));

    nodeElements
      .append("circle")
      .attr("r", (node) => getNodeRadius(node))
      .attr("fill", (node) => getNodeColor(node.type))
      .attr("fill-opacity", 0.92)
      .attr("stroke", "var(--surface-void)")
      .attr("stroke-width", 1.5);

    nodeElements
      .append("text")
      .text((node) => truncate(node.label, 18))
      .attr("dy", (node) => getNodeRadius(node) + 12)
      .attr("text-anchor", "middle")
      .attr("font-family", "var(--font-mono)")
      .attr("font-size", 9)
      .attr("fill", "var(--text-secondary)")
      .attr("opacity", (node) => (node.type === "chunk" ? 0 : 0.72))
      .attr("pointer-events", "none");

    simulation.on("tick", () => {
      edgeElements
        .attr("x1", (edge) => (edge.source as SimulationNode).x ?? 0)
        .attr("y1", (edge) => (edge.source as SimulationNode).y ?? 0)
        .attr("x2", (edge) => (edge.target as SimulationNode).x ?? 0)
        .attr("y2", (edge) => (edge.target as SimulationNode).y ?? 0);

      nodeElements.attr("transform", (node) => `translate(${node.x ?? 0},${node.y ?? 0})`);
    });

    return () => {
      simulation.stop();
    };
  }, [edges, nodes, selectNode, selectedNodeId]);

  return (
    <div className={styles.graphCanvas}>
      <svg ref={svgRef} className={styles.svg} onClick={() => selectNode(null)} />
    </div>
  );
}
