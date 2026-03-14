/**
 * Tool Panel Types
 * 
 * Type definitions for the tool-panel activation system.
 */

export type ToolCallStatus = 'pending' | 'running' | 'success' | 'error';

/**
 * Panel IDs that can be activated by tools
 */
export type ToolPanelId = 
  | 'carbon-dashboard'
  | 'boq-table'
  | 'clash-report'
  | 'document-editor'
  | '3d-viewer'
  | 'floorplan-viewer'
  | 'materials-panel'
  | 'files-panel';

/**
 * Event types for tool-panel communication
 */
export enum ToolPanelEventType {
  ACTIVATE_PANEL = 'ACTIVATE_PANEL',
  DEACTIVATE_PANEL = 'DEACTIVATE_PANEL',
  UPDATE_PANEL_DATA = 'UPDATE_PANEL_DATA',
  PANEL_LOADING = 'PANEL_LOADING',
  TOOL_COMPLETE = 'TOOL_COMPLETE',
  TOOL_START = 'TOOL_START',
}

/**
 * Tool panel event structure
 */
export interface ToolPanelEvent {
  type: ToolPanelEventType;
  payload: Record<string, unknown>;
  timestamp: number;
}

/**
 * Panel configuration
 */
export interface ToolPanelConfig {
  id: ToolPanelId;
  name: string;
  description: string;
  defaultWidth?: number;
  minWidth?: number;
  maxWidth?: number;
}

/**
 * Panel state in the store
 */
export interface ToolPanelState {
  isActive: boolean;
  isExpanded: boolean;
  data: Record<string, unknown>;
  isLoading: boolean;
  error?: string;
}

/**
 * All panels configuration
 */
export const TOOL_PANELS: ToolPanelConfig[] = [
  {
    id: 'carbon-dashboard',
    name: 'Carbon Dashboard',
    description: 'Display embodied carbon analysis results',
    defaultWidth: 40,
    minWidth: 20,
    maxWidth: 60,
  },
  {
    id: 'boq-table',
    name: 'BOQ Table',
    description: 'Bill of Quantities table view',
    defaultWidth: 50,
    minWidth: 30,
    maxWidth: 70,
  },
  {
    id: 'clash-report',
    name: 'Clash Report',
    description: 'BIM clash detection results',
    defaultWidth: 40,
    minWidth: 20,
    maxWidth: 60,
  },
  {
    id: 'document-editor',
    name: 'Document Editor',
    description: 'Document creation and editing',
    defaultWidth: 60,
    minWidth: 40,
    maxWidth: 80,
  },
  {
    id: '3d-viewer',
    name: '3D Viewer',
    description: '3D BIM model visualization',
    defaultWidth: 50,
    minWidth: 30,
    maxWidth: 70,
  },
  {
    id: 'floorplan-viewer',
    name: 'Floor Plan Viewer',
    description: '2D floor plan visualization',
    defaultWidth: 40,
    minWidth: 20,
    maxWidth: 60,
  },
  {
    id: 'materials-panel',
    name: 'Materials Panel',
    description: 'Material information and properties',
    defaultWidth: 30,
    minWidth: 20,
    maxWidth: 50,
  },
  {
    id: 'files-panel',
    name: 'Files Panel',
    description: 'File browser and manager',
    defaultWidth: 30,
    minWidth: 20,
    maxWidth: 50,
  },
];
