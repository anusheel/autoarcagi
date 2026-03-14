"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const ARC_COLORS: Record<number, string> = {
  0: "#111",
  1: "#e53935",
  2: "#43a047",
  3: "#ffb300",
  4: "#1e88e5",
  5: "#8e24aa",
  6: "#00acc1",
  7: "#f57c00",
  8: "#ec407a",
  9: "#7cb342",
  10: "#5c6bc0",
  11: "#ab47bc",
  12: "#26a69a",
  13: "#ef5350",
  14: "#66bb6a",
  15: "#ffa726",
};

interface Status {
  game_id: string;
  guid: string;
  frame: number[][][];
  state: string;
  levels_completed: number;
  experiment: string;
  title: string;
  logs: string[];
  updated_at: number;
}

function GameGrid({ frame }: { frame: number[][][] }) {
  const grid = frame[frame.length - 1] || [];
  if (!grid.length) return <div className="text-muted-foreground text-sm">No frame data</div>;

  const cellSize = Math.min(8, Math.floor(600 / Math.max(grid.length, grid[0]?.length || 1)));

  return (
    <div
      className="border border-border rounded overflow-hidden inline-block"
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${grid[0]?.length || 0}, ${cellSize}px)`,
        gap: 0,
      }}
    >
      {grid.map((row, y) =>
        row.map((val, x) => (
          <div
            key={`${y}-${x}`}
            style={{
              width: cellSize,
              height: cellSize,
              backgroundColor: ARC_COLORS[val] || `hsl(${(val * 37) % 360}, 70%, 50%)`,
            }}
          />
        ))
      )}
    </div>
  );
}

function stateBadgeVariant(state: string) {
  if (state === "WIN") return "default" as const;
  if (state === "GAME_OVER") return "destructive" as const;
  return "secondary" as const;
}

function timeSince(ts: number) {
  const seconds = Math.floor(Date.now() / 1000 - ts);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

export default function Dashboard() {
  const [statuses, setStatuses] = useState<Status[]>([]);

  useEffect(() => {
    const poll = async () => {
      try {
        const res = await fetch("/api/status");
        const data = await res.json();
        setStatuses(data);
      } catch {
        // ignore
      }
    };
    poll();
    const interval = setInterval(poll, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-background p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">ARC-AGI Dashboard</h1>
        <p className="text-muted-foreground text-sm">
          {statuses.length} active game{statuses.length !== 1 ? "s" : ""}
        </p>
      </div>
      {statuses.length === 0 ? (
        <p className="text-muted-foreground">No active experiments. Waiting for status data...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {statuses
            .sort((a, b) => b.updated_at - a.updated_at)
            .map((s) => (
              <Card key={s.guid}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-mono">{s.game_id}</CardTitle>
                    <Badge variant={stateBadgeVariant(s.state)}>{s.state || "PLAYING"}</Badge>
                  </div>
                  <CardDescription className="font-mono text-xs">
                    {s.title || s.experiment} &middot; Level {s.levels_completed} &middot;{" "}
                    {timeSince(s.updated_at)}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <GameGrid frame={s.frame} />
                  {s.logs?.length > 0 && (
                    <pre className="text-xs text-muted-foreground bg-muted rounded p-2 max-h-40 overflow-y-auto whitespace-pre-wrap">
                      {s.logs.slice(-20).join("\n")}
                    </pre>
                  )}
                </CardContent>
              </Card>
            ))}
        </div>
      )}
    </main>
  );
}
