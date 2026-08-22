import { createFileRoute } from "@tanstack/react-router";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import {
  ActivityIcon,
  AlertTriangleIcon,
  ArrowRightIcon,
  BuildingIcon,
  CheckCircle2Icon,
  ChevronRightIcon,
  CircuitBoardIcon,
  ClipboardListIcon,
  DropletsIcon,
  LayoutDashboardIcon,
  MapPinnedIcon,
  RouteIcon,
  ShieldCheckIcon,
  WavesIcon,
  XIcon,
  ZapIcon,
} from "lucide-react";

import heroImg from "@/assets/hero-skyline.jpg";
import bridgeImg from "@/assets/bridge.jpg";
import roadsImg from "@/assets/roads.jpg";
import {
  assets,
  cities,
  kpis,
  projects,
  riskCopy,
  warnings,
  type Asset,
  type City,
  type Risk,
} from "@/lib/infra-data";

const LiveMap = lazy(() => import("@/components/LiveMap"));

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "SmartInfra AI — City Infrastructure Intelligence" },
      {
        name: "description",
        content:
          "An interactive control surface for bridges, roads, drainage and civic buildings: live risk, predicted failures and one-click actions.",
      },
      { property: "og:title", content: "SmartInfra AI — City Infrastructure Intelligence" },
      {
        property: "og:description",
        content: "Live risk, predicted failures and one-click actions for every city asset.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

const typeIcon = {
  Bridge: WavesIcon,
  Road: RouteIcon,
  Building: BuildingIcon,
  Drainage: DropletsIcon,
  Utility: ZapIcon,
} as const;

const riskStyles: Record<Risk, string> = {
  critical: "bg-destructive/12 text-destructive border-destructive/30",
  high: "bg-warn/18 text-foreground border-warn/50",
  medium: "bg-secondary text-secondary-foreground border-border",
  low: "bg-ok/15 text-foreground border-ok/45",
};

const riskDot: Record<Risk, string> = {
  critical: "bg-destructive",
  high: "bg-warn",
  medium: "bg-muted-foreground",
  low: "bg-ok",
};

function Pill({ risk }: { risk: Risk }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[0.7rem] font-medium ${riskStyles[risk]}`}
    >
      <span className={`size-1.5 rounded-full ${riskDot[risk]}`} />
      {riskCopy[risk]}
    </span>
  );
}

function Index() {
  const [city, setCity] = useState<City>("Pune");
  const [filter, setFilter] = useState<Risk | "all">("all");
  const [tab, setTab] = useState<"assets" | "warnings" | "projects">("assets");
  const [selected, setSelected] = useState<Asset | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const visible = useMemo(
    () =>
      assets.filter(
        (a) => a.city === city && (filter === "all" ? true : a.risk === filter),
      ),
    [filter, city],
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
          <a href="#top" className="flex items-center gap-2.5">
            <span className="grid size-8 place-items-center rounded-lg bg-ink text-on-ink">
              <CircuitBoardIcon className="size-4" />
            </span>
            <span className="font-display text-base font-bold tracking-tight">SmartInfra AI</span>
          </a>
          <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
            <a className="transition-colors hover:text-foreground" href="#console">
              Live console
            </a>
            <a className="transition-colors hover:text-foreground" href="#coverage">
              Coverage
            </a>
            <a className="transition-colors hover:text-foreground" href="#how">
              How it works
            </a>
          </nav>
          <a
            href="#console"
            className="inline-flex items-center gap-1.5 rounded-full bg-ink px-4 py-2 text-sm font-medium text-on-ink transition-transform hover:-translate-y-0.5"
          >
            Open console
            <ArrowRightIcon className="size-3.5" />
          </a>
        </div>
      </header>

      {/* Hero */}
      <section id="top" className="relative isolate overflow-hidden">
        <img
          src={heroImg}
          alt="City skyline rising above low clouds"
          width={1920}
          height={1088}
          className="absolute inset-0 size-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-ink/78 via-ink/55 to-background" />
        <div className="relative mx-auto max-w-6xl px-5 pb-28 pt-24 md:pb-36 md:pt-32">
          <p className="eyebrow text-on-ink/75">Predictive infrastructure intelligence</p>
          <h1 className="mt-5 max-w-3xl text-5xl font-bold leading-[0.95] text-on-ink md:text-7xl">
            Every bridge, road and drain — watched, scored, acted on.
          </h1>
          <p className="mt-6 max-w-xl text-base leading-relaxed text-on-ink/80">
            SmartInfra AI merges sensor feeds, inspection records and weather into one clear picture
            of city risk, so teams know what to fix first — today, not after the failure.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-3">
            <a
              href="#console"
              className="inline-flex items-center gap-2 rounded-full bg-accent px-6 py-3 text-sm font-semibold text-accent-foreground shadow-[var(--shadow-lift)] transition-transform hover:-translate-y-0.5"
            >
              Explore the live console
              <ArrowRightIcon className="size-4" />
            </a>
            <a
              href="#coverage"
              className="inline-flex items-center gap-2 rounded-full border border-on-ink/35 px-6 py-3 text-sm font-medium text-on-ink transition-colors hover:bg-on-ink/10"
            >
              See what we monitor
            </a>
          </div>

          <dl className="mt-16 grid max-w-3xl grid-cols-2 gap-px overflow-hidden rounded-2xl border border-on-ink/20 bg-on-ink/20 md:grid-cols-4">
            {[
              ["12,482", "Assets tracked"],
              ["34", "Failures predicted (90d)"],
              ["17", "Live warnings"],
              ["₹2.4 Cr", "Risk exposure avoided"],
            ].map(([v, l]) => (
              <div key={l} className="bg-ink/70 px-5 py-4 backdrop-blur-sm">
                <dt className="font-display text-2xl font-bold text-on-ink">{v}</dt>
                <dd className="mt-1 text-xs text-on-ink/70">{l}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* Console */}
      <section id="console" className="blueprint-grid border-y border-border">
        <div className="mx-auto max-w-6xl px-5 py-20">
          <div className="flex flex-wrap items-end justify-between gap-6">
            <div>
              <p className="eyebrow text-muted-foreground">Live console</p>
              <h2 className="mt-3 text-3xl font-bold md:text-4xl">City operating picture</h2>
              <p className="mt-3 max-w-lg text-sm text-muted-foreground">
                Pick a city, tap a metric to filter, then open any asset for the AI reading and the
                recommended next step.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 rounded-full border border-border bg-card p-1.5 shadow-[var(--shadow-panel)]">
              {cities.map((c) => (
                <button
                  key={c}
                  onClick={() => setCity(c)}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                    city === c
                      ? "bg-ink text-on-ink"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {/* KPI buttons */}
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {kpis.map((k) => {
              const active = filter === k.filter;
              return (
                <button
                  key={k.id}
                  onClick={() => {
                    setFilter(k.filter);
                    setTab("assets");
                  }}
                  className={`panel group relative overflow-hidden p-5 text-left transition-all hover:-translate-y-1 hover:shadow-[var(--shadow-lift)] ${
                    active ? "ring-2 ring-accent" : ""
                  }`}
                >
                  <span
                    className={`absolute inset-x-0 top-0 h-1 ${
                      k.tone === "critical"
                        ? "bg-destructive"
                        : k.tone === "warn"
                          ? "bg-warn"
                          : k.tone === "ok"
                            ? "bg-ok"
                            : "bg-ink"
                    }`}
                  />
                  <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    {k.label}
                  </p>
                  <p className="mt-3 font-display text-3xl font-bold">{k.value}</p>
                  <p className="mt-2 text-xs text-muted-foreground">{k.hint}</p>
                  <span className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-accent-foreground/80 group-hover:text-foreground">
                    Filter list <ChevronRightIcon className="size-3" />
                  </span>
                </button>
              );
            })}
          </div>

          {/* Live map */}
          <div className="panel mt-6 overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3">
              <div className="flex items-center gap-2">
                <MapPinnedIcon className="size-4 text-accent" />
                <p className="text-sm font-medium">Live asset map · {city}</p>
                <span className="rounded-full bg-secondary px-2 py-0.5 text-[0.7rem] text-muted-foreground">
                  {visible.length} plotted
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-[0.7rem] text-muted-foreground">
                {(["critical", "high", "medium", "low"] as const).map((r) => (
                  <span key={r} className="inline-flex items-center gap-1.5">
                    <span className={`size-2 rounded-full ${riskDot[r]}`} />
                    {riskCopy[r]}
                  </span>
                ))}
              </div>
            </div>
            <div className="p-2">
              {mounted ? (
                <Suspense
                  fallback={
                    <div className="grid h-[380px] place-items-center rounded-xl bg-secondary text-sm text-muted-foreground">
                      Loading map…
                    </div>
                  }
                >
                  <LiveMap
                    city={city}
                    items={visible}
                    selectedId={selected?.id}
                    onSelect={(a) => {
                      setSelected(a);
                      setTab("assets");
                    }}
                  />
                </Suspense>
              ) : (
                <div className="grid h-[380px] place-items-center rounded-xl bg-secondary text-sm text-muted-foreground">
                  Loading map…
                </div>
              )}
            </div>
            <p className="border-t border-border px-4 py-3 text-xs text-muted-foreground">
              Markers reflect the current risk filter — tap a marker to open that asset in the
              inspector.
            </p>
          </div>

          {/* Tabs + panel */}
          <div className="mt-6 grid gap-6 lg:grid-cols-[1.35fr_1fr]">

            <div className="panel overflow-hidden">
              <div className="flex items-center gap-1 border-b border-border p-2">
                {(
                  [
                    ["assets", "Assets", LayoutDashboardIcon],
                    ["warnings", "Warnings", AlertTriangleIcon],
                    ["projects", "Projects", ClipboardListIcon],
                  ] as const
                ).map(([id, label, Icon]) => (
                  <button
                    key={id}
                    onClick={() => setTab(id)}
                    className={`inline-flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                      tab === id
                        ? "bg-secondary text-foreground"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <Icon className="size-4" />
                    {label}
                  </button>
                ))}
              </div>

              {tab === "assets" && (
                <div>
                  <div className="flex flex-wrap items-center gap-2 border-b border-border px-4 py-3">
                    <span className="text-xs text-muted-foreground">Risk filter</span>
                    {(["all", "critical", "high", "medium", "low"] as const).map((f) => (
                      <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                          filter === f
                            ? "border-ink bg-ink text-on-ink"
                            : "border-border text-muted-foreground hover:bg-secondary hover:text-foreground"
                        }`}
                      >
                        {f === "all" ? "All" : riskCopy[f]}
                      </button>
                    ))}
                  </div>
                  <ul className="divide-y divide-border">
                    {visible.map((a) => {
                      const Icon = typeIcon[a.type];
                      const isSel = selected?.id === a.id;
                      return (
                        <li key={a.id}>
                          <button
                            onClick={() => setSelected(isSel ? null : a)}
                            className={`flex w-full items-center gap-4 px-4 py-4 text-left transition-colors hover:bg-secondary/60 ${
                              isSel ? "bg-secondary/70" : ""
                            }`}
                          >
                            <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-secondary text-foreground">
                              <Icon className="size-4" />
                            </span>
                            <span className="min-w-0 flex-1">
                              <span className="flex flex-wrap items-center gap-2">
                                <span className="truncate font-medium">{a.name}</span>
                                <span className="font-display text-[0.7rem] text-muted-foreground">
                                  {a.id}
                                </span>
                              </span>
                              <span className="mt-1 block truncate text-xs text-muted-foreground">
                                {a.ward} · {a.city} · inspected {a.lastInspected}
                              </span>
                            </span>
                            <span className="hidden w-24 shrink-0 sm:block">
                              <span className="block h-1.5 overflow-hidden rounded-full bg-secondary">
                                <span
                                  className={`block h-full rounded-full ${riskDot[a.risk]}`}
                                  style={{ width: `${a.health}%` }}
                                />
                              </span>
                              <span className="mt-1 block text-right text-[0.68rem] text-muted-foreground">
                                {a.health}% health
                              </span>
                            </span>
                            <Pill risk={a.risk} />
                          </button>
                        </li>
                      );
                    })}
                    {visible.length === 0 && (
                      <li className="px-4 py-10 text-center text-sm text-muted-foreground">
                        No assets in this risk band for {city}.
                      </li>
                    )}
                  </ul>
                </div>
              )}

              {tab === "warnings" && (
                <ul className="divide-y divide-border">
                  {warnings.map((w) => (
                    <li key={w.id} className="flex gap-4 px-4 py-5">
                      <span
                        className={`mt-0.5 grid size-9 shrink-0 place-items-center rounded-xl ${
                          w.risk === "critical"
                            ? "bg-destructive/12 text-destructive"
                            : "bg-warn/20 text-foreground"
                        }`}
                      >
                        <AlertTriangleIcon className="size-4" />
                      </span>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-display text-[0.7rem] font-bold tracking-wider text-muted-foreground">
                            {w.priority}
                          </span>
                          <span className="font-medium">{w.title}</span>
                        </div>
                        <p className="mt-1.5 text-sm text-muted-foreground">{w.detail}</p>
                        <div className="mt-3 flex flex-wrap items-center gap-2">
                          <span className="rounded-full bg-secondary px-3 py-1 text-xs text-secondary-foreground">
                            {w.window}
                          </span>
                          <button className="rounded-full border border-border px-3 py-1 text-xs font-medium transition-colors hover:bg-ink hover:text-on-ink">
                            Acknowledge
                          </button>
                          <button className="rounded-full border border-border px-3 py-1 text-xs font-medium transition-colors hover:bg-ink hover:text-on-ink">
                            Assign crew
                          </button>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}

              {tab === "projects" && (
                <ul className="divide-y divide-border">
                  {projects.map((p) => (
                    <li key={p.id} className="px-4 py-5">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="font-medium">{p.name}</span>
                        <span
                          className={`rounded-full border px-2.5 py-1 text-[0.7rem] font-medium ${
                            p.status === "Delayed"
                              ? "border-destructive/30 bg-destructive/10 text-destructive"
                              : "border-ok/45 bg-ok/15 text-foreground"
                          }`}
                        >
                          {p.status}
                        </span>
                      </div>
                      <div className="mt-3 h-2 overflow-hidden rounded-full bg-secondary">
                        <div
                          className="h-full rounded-full bg-ink transition-all"
                          style={{ width: `${p.progress}%` }}
                        />
                      </div>
                      <p className="mt-2 text-xs text-muted-foreground">
                        {p.progress}% complete · {p.budget} · target {p.ends}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Detail panel */}
            <aside className="panel flex flex-col p-5 lg:sticky lg:top-24 lg:self-start">
              {selected ? (
                <>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="eyebrow text-muted-foreground">{selected.type} · {selected.id}</p>
                      <h3 className="mt-2 text-xl font-bold">{selected.name}</h3>
                      <p className="mt-1 text-xs text-muted-foreground">{selected.ward}</p>
                    </div>
                    <button
                      onClick={() => setSelected(null)}
                      aria-label="Close asset details"
                      className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                    >
                      <XIcon className="size-4" />
                    </button>
                  </div>
                  <div className="mt-4 flex items-center gap-3">
                    <Pill risk={selected.risk} />
                    <span className="text-sm text-muted-foreground">
                      Health score <strong className="text-foreground">{selected.health}</strong>/100
                    </span>
                  </div>
                  <div className="mt-5 rounded-xl bg-secondary/70 p-4">
                    <p className="eyebrow text-muted-foreground">AI reading</p>
                    <p className="mt-2 text-sm leading-relaxed">{selected.insight}</p>
                  </div>
                  <div className="mt-3 rounded-xl border border-accent/40 bg-accent/10 p-4">
                    <p className="eyebrow text-muted-foreground">Recommended action</p>
                    <p className="mt-2 text-sm leading-relaxed">{selected.action}</p>
                  </div>
                  <div className="mt-5 flex flex-wrap gap-2">
                    <button className="inline-flex items-center gap-2 rounded-full bg-ink px-4 py-2 text-sm font-medium text-on-ink transition-transform hover:-translate-y-0.5">
                      <CheckCircle2Icon className="size-4" /> Create work order
                    </button>
                    <button className="rounded-full border border-border px-4 py-2 text-sm font-medium transition-colors hover:bg-secondary">
                      Schedule inspection
                    </button>
                  </div>
                </>
              ) : (
                <div className="flex flex-1 flex-col items-center justify-center py-14 text-center">
                  <span className="grid size-12 place-items-center rounded-2xl bg-secondary text-muted-foreground">
                    <ActivityIcon className="size-5" />
                  </span>
                  <p className="mt-4 font-display text-base font-bold">Select an asset</p>
                  <p className="mt-2 max-w-xs text-sm text-muted-foreground">
                    Tap any row in the list to see its AI reading, health trend and the recommended
                    next action.
                  </p>
                </div>
              )}
            </aside>
          </div>
        </div>
      </section>

      {/* Coverage */}
      <section id="coverage" className="mx-auto max-w-6xl px-5 py-24">
        <p className="eyebrow text-muted-foreground">Coverage</p>
        <h2 className="mt-3 max-w-2xl text-3xl font-bold md:text-4xl">
          Built for the structures a city cannot afford to lose.
        </h2>
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          <article className="group relative isolate overflow-hidden rounded-3xl">
            <img
              src={bridgeImg}
              alt="Cable-stayed bridge at blue hour"
              width={1280}
              height={900}
              loading="lazy"
              className="h-80 w-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-ink/90 via-ink/30 to-transparent" />
            <div className="absolute inset-x-0 bottom-0 p-6">
              <h3 className="text-2xl font-bold text-on-ink">Bridges & structures</h3>
              <p className="mt-2 max-w-sm text-sm text-on-ink/80">
                Vibration, tilt and strain signatures compared against a per-span baseline to catch
                fatigue long before it is visible.
              </p>
            </div>
          </article>
          <article className="group relative isolate overflow-hidden rounded-3xl">
            <img
              src={roadsImg}
              alt="Aerial view of a highway interchange"
              width={1280}
              height={900}
              loading="lazy"
              className="h-80 w-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-ink/90 via-ink/30 to-transparent" />
            <div className="absolute inset-x-0 bottom-0 p-6">
              <h3 className="text-2xl font-bold text-on-ink">Roads & corridors</h3>
              <p className="mt-2 max-w-sm text-sm text-on-ink/80">
                Surface degradation, subgrade moisture and traffic load fused into a repair
                priority for every kilometre.
              </p>
            </div>
          </article>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-3">
          {[
            [BuildingIcon, "Civic buildings", "Facade, moisture and structural condition tracking for hospitals, schools and offices."],
            [DropletsIcon, "Drainage & flood", "Node-level pressure anomalies matched to live rainfall forecasts."],
            [ZapIcon, "Utilities", "Feeder loads, outages and capacity headroom across the grid."],
          ].map(([Icon, title, body]) => {
            const I = Icon as typeof BuildingIcon;
            return (
              <div key={title as string} className="panel p-6 transition-transform hover:-translate-y-1">
                <span className="grid size-10 place-items-center rounded-xl bg-ink text-on-ink">
                  <I className="size-4" />
                </span>
                <h3 className="mt-4 text-lg font-bold">{title as string}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{body as string}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="border-y border-border bg-secondary/50">
        <div className="mx-auto max-w-6xl px-5 py-24">
          <p className="eyebrow text-muted-foreground">How it works</p>
          <h2 className="mt-3 text-3xl font-bold md:text-4xl">Three steps, no training required.</h2>
          <ol className="mt-10 grid gap-5 md:grid-cols-3">
            {[
              ["01", "Connect", "Sensor feeds, inspection PDFs, GIS layers and weather sync into one asset registry."],
              ["02", "Predict", "Models score every asset daily and flag the failures likely within 90 days."],
              ["03", "Act", "Each warning arrives with a plain-language action, an owner and a deadline."],
            ].map(([n, t, b]) => (
              <li key={n} className="panel p-6">
                <span className="font-display text-4xl font-bold text-accent">{n}</span>
                <h3 className="mt-4 text-lg font-bold">{t}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{b}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-6xl px-5 py-24">
        <div className="relative isolate overflow-hidden rounded-3xl bg-ink px-8 py-16 text-center">
          <div className="blueprint-grid absolute inset-0 opacity-25" />
          <div className="relative">
            <ShieldCheckIcon className="mx-auto size-8 text-accent" />
            <h2 className="mx-auto mt-5 max-w-2xl text-3xl font-bold text-on-ink md:text-4xl">
              Know your city's weakest structure before the monsoon does.
            </h2>
            <p className="mx-auto mt-4 max-w-lg text-sm text-on-ink/75">
              Start with one ward, one bridge or one corridor. The console works the same at any
              scale.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <a
                href="#console"
                className="inline-flex items-center gap-2 rounded-full bg-accent px-6 py-3 text-sm font-semibold text-accent-foreground transition-transform hover:-translate-y-0.5"
              >
                Open the console <ArrowRightIcon className="size-4" />
              </a>
              <a
                href="#coverage"
                className="rounded-full border border-on-ink/35 px-6 py-3 text-sm font-medium text-on-ink transition-colors hover:bg-on-ink/10"
              >
                Talk to the team
              </a>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-5 py-8 text-sm text-muted-foreground">
          <span className="flex items-center gap-2">
            <CircuitBoardIcon className="size-4" /> SmartInfra AI
          </span>
          <span>Demo data · Pune, Pimpri-Chinchwad, Nashik, Nagpur</span>
        </div>
      </footer>
    </div>
  );
}
