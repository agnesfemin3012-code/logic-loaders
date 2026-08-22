import React from 'react';
import { CheckCircle2Icon, ShieldAlertIcon } from 'lucide-react';
import { Panel } from '../components/ui/Panel';
import { StatusBadge } from '../components/ui/StatusBadge';
import { precautions } from '../data/intelligence';
import { assetById } from '../data/assets';

interface PageProps {
  onOpenAsset: (id: string) => void;
  onNavigate: (page: string) => void;
}

export function Precautions({ onOpenAsset, onNavigate }: PageProps) {
  return (
    <div className="flex flex-col gap-4 p-4">
      <header>
        <h1 className="text-base font-semibold tracking-tight text-txt">Precautions</h1>
        <p className="text-xs text-muted">
          Detected risks converted into ranked, ownable actions. Safety-critical items need authorised
          verification before execution.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        {precautions.map((p) =>
        <Panel
          key={p.id}
          title={`Priority ${p.priority}`}
          subtitle={p.trigger}
          actions={
          p.requiresVerification ?
          <StatusBadge level="critical">Verification required</StatusBadge> :

          <StatusBadge level="low">Ready to execute</StatusBadge>

          }
          bodyClassName="p-4"
          footer={
          <span className="flex flex-wrap items-center gap-x-4 gap-y-1">
                <span>Owner: {p.owner}</span>
                <span>Window: {p.window}</span>
              </span>
          }>
          
            <h2 className="text-sm font-semibold text-txt">{p.title}</h2>
            <ul className="mt-3 space-y-2">
              {p.actions.map((action) =>
            <li key={action} className="flex items-start gap-2 text-[12px] leading-snug text-txt">
                  <CheckCircle2Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-low" />
                  {action}
                </li>
            )}
            </ul>

            <div className="mt-3 flex flex-wrap items-center gap-2">
              {p.relatedAssets.map((id) => {
              const asset = assetById(id);
              if (!asset) return null;
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => onOpenAsset(id)}
                  className="rounded border border-line bg-ink/50 px-2 py-1 font-mono text-[10px] text-muted transition-colors duration-150 ease-swift hover:text-txt focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/70">
                  
                    {asset.id}
                  </button>);

            })}
              <button
              type="button"
              onClick={() => onNavigate('work-orders')}
              className="ml-auto rounded-md bg-accent px-2.5 py-1.5 text-[11px] font-semibold text-ink transition-colors duration-150 ease-swift hover:bg-accent/85 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/70">
              
                Convert to work orders
              </button>
            </div>

            {p.requiresVerification ?
          <p className="mt-3 flex items-start gap-2 rounded border border-critical/30 bg-critical/[0.07] px-3 py-2 text-[11px] leading-snug text-critical">
                <ShieldAlertIcon className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                Engineering / authorised officer verification required before any traffic restriction,
                shutdown or closure.
              </p> :
          null}
          </Panel>
        )}
      </div>
    </div>);

}