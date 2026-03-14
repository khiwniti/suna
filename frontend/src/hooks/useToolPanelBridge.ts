/**
 * Tool-Panel Bridge Hook
 *
 * Bridges tool call completion events to panel activation.
 * When an AI tool completes successfully, this hook:
 * 1. Detects which panel should display the results
 * 2. Activates and expands the panel
 * 3. Passes tool result data to the panel
 */

'use client';

import { useCallback } from 'react';
import { useToolPanelStore } from '@/stores/tool-panel-store';
import { createToolPanelEvent, ToolPanelEventType } from '@/lib/tool-panel-event-bus';
import type { ToolCallStatus, ToolPanelId } from '@/types/tool-panel';

// Tool name → Panel ID mapping
export const TOOL_PANEL_MAP: Record<string, ToolPanelId> = {
  // Carbon analysis tools
  carbon_analysis: 'carbon-dashboard',
  calculate_carbon: 'carbon-dashboard',
  analyze_sustainability: 'carbon-dashboard',
  get_emission_factors: 'carbon-dashboard',
  calculate_embodied_carbon: 'carbon-dashboard',
  get_tgo_factors: 'carbon-dashboard',
  assess_edge_certification: 'carbon-dashboard',
  generate_carbon_report: 'carbon-dashboard',
  optimize_materials: 'carbon-dashboard',

  // BOQ tools
  extract_boq: 'boq-table',
  update_boq_row: 'boq-table',
  add_boq_item: 'boq-table',
  calculate_quantities: 'boq-table',
  get_element_quantities: 'boq-table',

  // Clash detection tools
  clash_detection: 'clash-report',
  find_clashes: 'clash-report',
  resolve_clash: 'clash-report',

  // Document tools
  generate_report: 'document-editor',
  create_document: 'document-editor',
  export_pdf: 'document-editor',

  // 3D viewer tools
  highlight_elements: '3d-viewer',
  isolate_elements: '3d-viewer',
  navigate_to_element: '3d-viewer',
  show_section: '3d-viewer',
  parse_ifc_file: '3d-viewer',
  extract_elements: '3d-viewer',
  get_element_properties: '3d-viewer',

  // Floor plan tools
  analyze_floor_plan: 'floorplan-viewer',
  calculate_areas: 'floorplan-viewer',

  // BIM tools
  get_element_materials: 'materials-panel',
  list_ifc_files: 'files-panel',
};

export interface ToolCallResult {
  id: string;
  name: string;
  status: ToolCallStatus;
  result?: unknown;
  error?: string;
}

export function useToolPanelBridge() {
  const activatePanel = useToolPanelStore((state) => state.activatePanel);
  const updatePanelData = useToolPanelStore((state) => state.updatePanelData);

  const onToolComplete = useCallback(
    (tool: ToolCallResult) => {
      // Only activate for successful tools
      if (tool.status !== 'success') {
        return;
      }

      // Find the panel for this tool
      const panelId = TOOL_PANEL_MAP[tool.name];
      if (!panelId) {
        return;
      }

      // Activate the panel
      activatePanel(panelId, true);

      // Send the tool result data to the panel
      if (tool.result) {
        updatePanelData(panelId, tool.result as Record<string, unknown>);
        
        // Also publish event for components that listen to event bus
        createToolPanelEvent(ToolPanelEventType.UPDATE_PANEL_DATA, {
          panelId,
          data: tool.result as Record<string, unknown>,
          merge: true,
        });
      }
      
      // Publish activation event
      createToolPanelEvent(ToolPanelEventType.ACTIVATE_PANEL, {
        panelId,
        autoExpand: true,
      });
    },
    [activatePanel, updatePanelData]
  );

  const onToolStart = useCallback(
    (tool: { id: string; name: string }) => {
      // Optional: Pre-activate panel to show loading state
      const panelId = TOOL_PANEL_MAP[tool.name];
      if (panelId) {
        // Update panel to show loading state
        updatePanelData(panelId, { isLoading: true, toolId: tool.id });
        
        // Publish loading event
        createToolPanelEvent(ToolPanelEventType.PANEL_LOADING, {
          panelId,
          toolId: tool.id,
        });
      }
    },
    [updatePanelData]
  );

  return {
    onToolComplete,
    onToolStart,
    TOOL_PANEL_MAP,
  };
}

export { TOOL_PANEL_MAP };
