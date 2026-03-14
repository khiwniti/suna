/**
 * useToolPanelEventSubscriptions Hook
 *
 * Subscribes the component to tool panel events.
 * Should be called once in the root layout or workspace.
 */

'use client';

import { useEffect } from 'react';
import { toolPanelEventBus } from '@/lib/tool-panel-event-bus';
import { useToolPanelStore } from '@/stores/tool-panel-store';
import { ToolPanelEventType } from '@/types/tool-panel';
import type { ToolPanelId } from '@/types/tool-panel';

export function useToolPanelEventSubscriptions() {
  const activatePanel = useToolPanelStore((state) => state.activatePanel);
  const deactivatePanel = useToolPanelStore((state) => state.deactivatePanel);
  const updatePanelData = useToolPanelStore((state) => state.updatePanelData);
  const setPanelLoading = useToolPanelStore((state) => state.setPanelLoading);

  useEffect(() => {
    // Subscribe to ACTIVATE_PANEL events
    const unsubActivate = toolPanelEventBus.subscribe(
      ToolPanelEventType.ACTIVATE_PANEL,
      (event) => {
        const { panelId, autoExpand } = event.payload as {
          panelId: ToolPanelId;
          autoExpand?: boolean;
        };
        activatePanel(panelId, autoExpand ?? true);
      }
    );

    // Subscribe to DEACTIVATE_PANEL events
    const unsubDeactivate = toolPanelEventBus.subscribe(
      ToolPanelEventType.DEACTIVATE_PANEL,
      (event) => {
        const { panelId } = event.payload as { panelId: ToolPanelId };
        deactivatePanel(panelId);
      }
    );

    // Subscribe to UPDATE_PANEL_DATA events
    const unsubUpdate = toolPanelEventBus.subscribe(
      ToolPanelEventType.UPDATE_PANEL_DATA,
      (event) => {
        const { panelId, data, merge } = event.payload as {
          panelId: ToolPanelId;
          data: Record<string, unknown>;
          merge?: boolean;
        };
        updatePanelData(panelId, data, merge);
      }
    );

    // Subscribe to PANEL_LOADING events
    const unsubLoading = toolPanelEventBus.subscribe(
      ToolPanelEventType.PANEL_LOADING,
      (event) => {
        const { panelId, toolId } = event.payload as {
          panelId: ToolPanelId;
          toolId?: string;
        };
        setPanelLoading(panelId, true);
        
        // Auto-clear loading after 30 seconds timeout
        setTimeout(() => {
          setPanelLoading(panelId, false);
        }, 30000);
      }
    );

    return () => {
      unsubActivate();
      unsubDeactivate();
      unsubUpdate();
      unsubLoading();
    };
  }, [activatePanel, deactivatePanel, updatePanelData, setPanelLoading]);
}
