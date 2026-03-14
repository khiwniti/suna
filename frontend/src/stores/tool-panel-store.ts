/**
 * Tool Panel Store
 * 
 * Zustand store for managing tool-triggered panels.
 * Provides state management for panel activation, data, and loading states.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { ToolPanelId, ToolPanelState } from '@/types/tool-panel';
import { TOOL_PANELS } from '@/types/tool-panel';

interface ToolPanelStore {
  // Active panel state
  activePanelId: ToolPanelId | null;
  expandedPanels: Set<ToolPanelId>;
  panelStates: Record<ToolPanelId, ToolPanelState>;
  
  // Actions
  activatePanel: (panelId: ToolPanelId, autoExpand?: boolean) => void;
  deactivatePanel: (panelId: ToolPanelId) => void;
  deactivateAllPanels: () => void;
  expandPanel: (panelId: ToolPanelId) => void;
  collapsePanel: (panelId: ToolPanelId) => void;
  togglePanel: (panelId: ToolPanelId) => void;
  updatePanelData: (panelId: ToolPanelId, data: Record<string, unknown>, merge?: boolean) => void;
  setPanelLoading: (panelId: ToolPanelId, isLoading: boolean) => void;
  setPanelError: (panelId: ToolPanelId, error: string | undefined) => void;
  clearPanelData: (panelId: ToolPanelId) => void;
}

// Initialize default panel states
function createDefaultPanelStates(): Record<ToolPanelId, ToolPanelState> {
  const states: Record<string, ToolPanelState> = {};
  
  TOOL_PANELS.forEach(panel => {
    states[panel.id] = {
      isActive: false,
      isExpanded: false,
      data: {},
      isLoading: false,
      error: undefined,
    };
  });
  
  return states as Record<ToolPanelId, ToolPanelState>;
}

export const useToolPanelStore = create<ToolPanelStore>()(
  devtools(
    (set, get) => ({
      activePanelId: null,
      expandedPanels: new Set<ToolPanelId>(),
      panelStates: createDefaultPanelStates(),

      activatePanel: (panelId: ToolPanelId, autoExpand = false) => {
        set((state) => {
          const newExpandedPanels = new Set(state.expandedPanels);
          if (autoExpand) {
            newExpandedPanels.add(panelId);
          }
          
          return {
            activePanelId: panelId,
            expandedPanels: newExpandedPanels,
            panelStates: {
              ...state.panelStates,
              [panelId]: {
                ...state.panelStates[panelId],
                isActive: true,
                isExpanded: autoExpand || state.panelStates[panelId].isExpanded,
              },
            },
          };
        }, false, `activatePanel('${panelId}', ${autoExpand})`);
      },

      deactivatePanel: (panelId: ToolPanelId) => {
        set((state) => {
          const newExpandedPanels = new Set(state.expandedPanels);
          newExpandedPanels.delete(panelId);
          
          return {
            activePanelId: state.activePanelId === panelId ? null : state.activePanelId,
            expandedPanels: newExpandedPanels,
            panelStates: {
              ...state.panelStates,
              [panelId]: {
                ...state.panelStates[panelId],
                isActive: false,
                isExpanded: false,
              },
            },
          };
        }, false, `deactivatePanel('${panelId}')`);
      },

      deactivateAllPanels: () => {
        set(() => ({
          activePanelId: null,
          expandedPanels: new Set(),
          panelStates: createDefaultPanelStates(),
        }), false, 'deactivateAllPanels');
      },

      expandPanel: (panelId: ToolPanelId) => {
        set((state) => {
          const newExpandedPanels = new Set(state.expandedPanels);
          newExpandedPanels.add(panelId);
          
          return {
            expandedPanels: newExpandedPanels,
            panelStates: {
              ...state.panelStates,
              [panelId]: {
                ...state.panelStates[panelId],
                isExpanded: true,
              },
            },
          };
        }, false, `expandPanel('${panelId}')`);
      },

      collapsePanel: (panelId: ToolPanelId) => {
        set((state) => {
          const newExpandedPanels = new Set(state.expandedPanels);
          newExpandedPanels.delete(panelId);
          
          return {
            expandedPanels: newExpandedPanels,
            panelStates: {
              ...state.panelStates,
              [panelId]: {
                ...state.panelStates[panelId],
                isExpanded: false,
              },
            },
          };
        }, false, `collapsePanel('${panelId}')`);
      },

      togglePanel: (panelId: ToolPanelId) => {
        const state = get();
        if (state.panelStates[panelId]?.isExpanded) {
          state.collapsePanel(panelId);
        } else {
          state.expandPanel(panelId);
        }
      },

      updatePanelData: (panelId: ToolPanelId, data: Record<string, unknown>, merge = true) => {
        set((state) => ({
          panelStates: {
            ...state.panelStates,
            [panelId]: {
              ...state.panelStates[panelId],
              data: merge
                ? { ...state.panelStates[panelId].data, ...data }
                : data,
            },
          },
        }), false, `updatePanelData('${panelId}', ${JSON.stringify(data).slice(0, 50)}...)`);
      },

      setPanelLoading: (panelId: ToolPanelId, isLoading: boolean) => {
        set((state) => ({
          panelStates: {
            ...state.panelStates,
            [panelId]: {
              ...state.panelStates[panelId],
              isLoading,
            },
          },
        }), false, `setPanelLoading('${panelId}', ${isLoading})`);
      },

      setPanelError: (panelId: ToolPanelId, error: string | undefined) => {
        set((state) => ({
          panelStates: {
            ...state.panelStates,
            [panelId]: {
              ...state.panelStates[panelId],
              error,
            },
          },
        }), false, `setPanelError('${panelId}', ${error ? `"${error}"` : 'undefined'})`);
      },

      clearPanelData: (panelId: ToolPanelId) => {
        set((state) => ({
          panelStates: {
            ...state.panelStates,
            [panelId]: {
              ...state.panelStates[panelId],
              data: {},
              isLoading: false,
              error: undefined,
            },
          },
        }), false, `clearPanelData('${panelId}')`);
      },
    }),
    {
      name: 'tool-panel-store',
    }
  )
);
