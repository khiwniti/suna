/**
 * useToolCallHandler Hook
 * 
 * Hook that integrates with the tool call system to trigger panel activation.
 * This should be used in components that process tool calls.
 * 
 * Usage:
 * const { onToolStarted, onToolCompleted } = useToolCallHandler();
 * 
 * Then call these functions when tool events occur:
 * - onToolStarted({ id: 'tool-1', name: 'calculate_carbon' })
 * - onToolCompleted({ id: 'tool-1', name: 'calculate_carbon', status: 'success', result: {...} })
 */

'use client';

import { useEffect, useCallback, useRef } from 'react';
import { toolPanelEventBus } from '@/lib/tool-panel-event-bus';
import { useToolPanelStore } from '@/stores/tool-panel-store';
import { ToolPanelEventType } from '@/types/tool-panel';
import { TOOL_PANEL_MAP } from '@/hooks/useToolPanelBridge';
import type { ToolPanelId } from '@/types/tool-panel';

interface ToolEvent {
  id: string;
  name: string;
}

interface ToolCompleteEvent extends ToolEvent {
  status: 'success' | 'error' | 'pending' | 'running';
  result?: unknown;
  error?: string;
}

export function useToolCallHandler() {
  const activatePanel = useToolPanelStore((state) => state.activatePanel);
  const updatePanelData = useToolPanelStore((state) => state.updatePanelData);
  const setPanelLoading = useToolPanelStore((state) => state.setPanelLoading);
  
  // Track which tools are currently running
  const runningToolsRef = useRef<Map<string, ToolEvent>>(new Map());

  const onToolStarted = useCallback((tool: ToolEvent) => {
    // Track running tool
    runningToolsRef.current.set(tool.id, tool);
    
    // Find the panel for this tool
    const panelId = TOOL_PANEL_MAP[tool.name] as ToolPanelId | undefined;
    if (panelId) {
      // Show loading state
      setPanelLoading(panelId, true);
      
      // Publish loading event
      toolPanelEventBus.publish('tool-handler', {
        type: ToolPanelEventType.PANEL_LOADING,
        payload: { panelId, toolId: tool.id },
        timestamp: Date.now(),
      });
    }
  }, [setPanelLoading]);

  const onToolCompleted = useCallback((tool: ToolCompleteEvent) => {
    // Remove from running tools
    runningToolsRef.current.delete(tool.id);
    
    // Find the panel for this tool
    const panelId = TOOL_PANEL_MAP[tool.name] as ToolPanelId | undefined;
    if (!panelId) {
      return;
    }
    
    // Clear loading state
    setPanelLoading(panelId, false);
    
    // Only activate panel for successful tools
    if (tool.status === 'success') {
      // Activate the panel
      activatePanel(panelId, true);
      
      // Update panel data with tool result
      if (tool.result) {
        updatePanelData(panelId, tool.result as Record<string, unknown>);
        
        // Publish update event
        toolPanelEventBus.publish('tool-handler', {
          type: ToolPanelEventType.UPDATE_PANEL_DATA,
          payload: { 
            panelId, 
            data: tool.result as Record<string, unknown>, 
            merge: true 
          },
          timestamp: Date.now(),
        });
      }
      
      // Publish activation event
      toolPanelEventBus.publish('tool-handler', {
        type: ToolPanelEventType.ACTIVATE_PANEL,
        payload: { panelId, autoExpand: true },
        timestamp: Date.now(),
      });
    } else if (tool.status === 'error') {
      // Publish error event
      toolPanelEventBus.publish('tool-handler', {
        type: ToolPanelEventType.PANEL_LOADING,
        payload: { panelId, error: tool.error },
        timestamp: Date.now(),
      });
    }
  }, [activatePanel, updatePanelData, setPanelLoading]);

  return {
    onToolStarted,
    onToolCompleted,
    runningToolsCount: runningToolsRef.current.size,
  };
}
