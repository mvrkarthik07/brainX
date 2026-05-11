import {
  Outlet,
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
} from "@tanstack/react-router";

import { AppShell } from "@/components/layout/AppShell";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { ChatView } from "@/views/ChatView";
import { DocumentsView } from "@/views/DocumentsView";
import { GraphView } from "@/views/GraphView";
import { HistoryView } from "@/views/HistoryView";
import { IngestView } from "@/views/IngestView";
import { SettingsView } from "@/views/SettingsView";

function RootLayout() {
  useKeyboardShortcuts();
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}

const rootRoute = createRootRoute({
  component: RootLayout,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: ChatView,
});

const graphRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/graph",
  component: GraphView,
});

const documentsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/documents",
  component: DocumentsView,
});

const ingestRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/ingest",
  component: IngestView,
});

const historyRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/history",
  component: HistoryView,
});

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/settings",
  component: SettingsView,
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  graphRoute,
  documentsRoute,
  ingestRoute,
  historyRoute,
  settingsRoute,
]);

export const router = createRouter({
  routeTree,
  defaultPreload: "intent",
  defaultNotFoundComponent: () => {
    throw redirect({ to: "/" });
  },
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
