/**
 * Tool Panel Components
 * 
 * Reusable panel components for tool-triggered panels.
 * These panels can be embedded in the workspace to display tool results.
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import { X, ChevronLeft, ChevronRight, Loader2, AlertCircle } from 'lucide-react';
import { useToolPanelStore } from '@/stores/tool-panel-store';
import { TOOL_PANELS, type ToolPanelId } from '@/types/tool-panel';
import { cn } from '@/lib/utils';

interface ToolPanelProps {
  panelId: ToolPanelId;
  children: (data: Record<string, unknown>, isLoading: boolean, error?: string) => React.ReactNode;
  className?: string;
  defaultWidth?: number;
}

/**
 * Individual tool panel component
 */
export function ToolPanel({
  panelId,
  children,
  className,
  defaultWidth = 40,
}: ToolPanelProps) {
  const panelConfig = TOOL_PANELS.find(p => p.id === panelId);
  const { isActive, isExpanded, data, isLoading, error } = useToolPanelStore(
    (state) => state.panelStates[panelId] || {}
  );
  const { collapsePanel, clearPanelData } = useToolPanelStore();
  
  const wasJustActivated = useRef(false);
  const [showActivationGlow, setShowActivationGlow] = useState(false);

  // Activation glow effect
  useEffect(() => {
    if (isActive && !wasJustActivated.current) {
      wasJustActivated.current = true;
      setShowActivationGlow(true);
      const timer = setTimeout(() => setShowActivationGlow(false), 1500);
      return () => clearTimeout(timer);
    } else if (!isActive) {
      wasJustActivated.current = false;
    }
  }, [isActive]);

  if (!isActive) {
    return null;
  }

  return (
    <div
      className={cn(
        'flex flex-col h-full bg-background border-l border-border',
        'transition-all duration-300 ease-in-out',
        showActivationGlow && 'ring-2 ring-primary/50 animate-pulse',
        className
      )}
      style={{ width: isExpanded ? `${defaultWidth}%` : '48px' }}
    >
      {/* Panel Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <button
          onClick={() => collapsePanel(panelId)}
          className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors"
        >
          {isExpanded ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
          {isExpanded && panelConfig?.name}
        </button>
        
        {isExpanded && (
          <button
            onClick={() => {
              collapsePanel(panelId);
              clearPanelData(panelId);
            }}
            className="p-1 hover:bg-secondary rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Panel Content */}
      {isExpanded && (
        <div className="flex-1 overflow-auto p-4">
          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-2 text-muted-foreground">Loading...</span>
            </div>
          )}
          
          {error && !isLoading && (
            <div className="flex items-center justify-center h-full text-destructive">
              <AlertCircle className="w-5 h-5 mr-2" />
              <span>{error}</span>
            </div>
          )}
          
          {!isLoading && !error && children(data, isLoading, error)}
        </div>
      )}
    </div>
  );
}

/**
 * Panel Container - manages multiple tool panels
 */
interface PanelContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function ToolPanelContainer({ children, className }: PanelContainerProps) {
  const activePanelIds = useToolPanelStore(
    (state) => Object.keys(state.panelStates).filter(
      (id) => state.panelStates[id as ToolPanelId]?.isActive
    ) as ToolPanelId[]
  );

  return (
    <div className={cn('flex h-full', className)}>
      {children}
    </div>
  );
}

/**
 * Carbon Dashboard Panel
 */
export function CarbonDashboardPanel() {
  const data = useToolPanelStore((state) => state.panelStates['carbon-dashboard']?.data);
  const isLoading = useToolPanelStore((state) => state.panelStates['carbon-dashboard']?.isLoading);
  
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Embodied Carbon Results</h2>
      
      {data && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-secondary rounded-lg">
              <div className="text-sm text-muted-foreground">Total Carbon</div>
              <div className="text-2xl font-bold">
                {data.total_carbon_kg ? `${Number(data.total_carbon_kg).toLocaleString()} kg` : 'N/A'}
              </div>
            </div>
            <div className="p-4 bg-secondary rounded-lg">
              <div className="text-sm text-muted-foreground">Transport</div>
              <div className="text-2xl font-bold">
                {data.transport_carbon_kg ? `${Number(data.transport_carbon_kg).toLocaleString()} kg` : 'N/A'}
              </div>
            </div>
          </div>
          
          {data.summary && (
            <div>
              <h3 className="text-sm font-medium mb-2">Carbon by Category</h3>
              <div className="space-y-2">
                {Object.entries(data.summary as Record<string, { carbon_kg: number; percentage: number }>).map(
                  ([category, values]) => (
                    <div key={category} className="flex justify-between text-sm">
                      <span className="capitalize">{category}</span>
                      <span>
                        {values.carbon_kg.toLocaleString()} kg ({values.percentage}%)
                      </span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

/**
 * BOQ Table Panel
 */
export function BOQTablePanel() {
  const data = useToolPanelStore((state) => state.panelStates['boq-table']?.data);
  const isLoading = useToolPanelStore((state) => state.panelStates['boq-table']?.isLoading);
  
  const items = data?.items as Array<{
    id: string;
    name: string;
    quantity: number;
    unit: string;
    rate?: number;
    amount?: number;
  }> | undefined;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Bill of Quantities</h2>
      
      {items && items.length > 0 ? (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Item</th>
              <th className="text-right py-2">Quantity</th>
              <th className="text-right py-2">Unit</th>
              <th className="text-right py-2">Rate</th>
              <th className="text-right py-2">Amount</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b">
                <td className="py-2">{item.name}</td>
                <td className="text-right">{item.quantity}</td>
                <td className="text-right">{item.unit}</td>
                <td className="text-right">{item.rate?.toLocaleString() || '-'}</td>
                <td className="text-right">{item.amount?.toLocaleString() || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="text-muted-foreground">No BOQ data available</p>
      )}
    </div>
  );
}

export { ToolPanel, ToolPanelContainer, CarbonDashboardPanel, BOQTablePanel };
