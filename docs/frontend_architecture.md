# BrainX Frontend Architecture

## App Structure

```text
apps/desktop/
  src/
    components/
    pages/
    api/
    styles/
    types/
    App.tsx
    main.tsx
```

## Pages

- Dashboard
- Chat
- Documents
- Graph Explorer
- Ingestion
- Interaction History
- Settings
- Snapshot

## Dark Theme

- Background: `#050816`
- Cards: `#0f172a`
- Borders: `#1e293b`
- Accent: `#00d4ff`
- Text primary: `#f8fafc`
- Text secondary: `#94a3b8`
- Error: muted red
- Success: muted green

## Core Components

- `Sidebar`
- `StatusBar`
- `HealthBadge`
- `ChatPanel`
- `SourcePanel`
- `RetrievalTracePanel`
- `FeedbackStars`
- `DocumentTable`
- `GraphCanvas`
- `IngestionForm`
- `SettingsPanel`

## API Client Methods

- `getHealth()`
- `ingestFile(path)`
- `ingestFolder(path, recursive)`
- `listDocuments()`
- `queryBrainX(query)`
- `sendFeedback(interactionId, rating)`
- `getGraphNeighborhood(nodeId, hops, limit)`

## Layout

- Left sidebar for navigation
- Main content area for the active page
- Right inspector panel for sources and retrieval trace
- Dedicated graph page with D3 canvas and node inspector

## Graph Explorer

The Graph Explorer must use `/graph/neighborhood` and render real SQLite-backed graph data. No fake nodes, edges, or placeholder neighborhoods.

## Build Order

1. Create the Vite/Tauri shell
2. Implement the health dashboard
3. Implement the documents page
4. Implement the ingestion page
5. Implement the chat page
6. Implement feedback controls
7. Implement the graph explorer
8. Polish the dark UI
