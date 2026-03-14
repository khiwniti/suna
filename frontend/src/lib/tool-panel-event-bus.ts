/**
 * Tool Panel Event Bus
 * 
 * A simple pub/sub system for tool-panel communication.
 * Allows loose coupling between tools, panels, and other components.
 */

import { ToolPanelEventType, ToolPanelEvent } from '@/types/tool-panel';

type EventCallback = (event: ToolPanelEvent) => void;

class ToolPanelEventBus {
  private subscribers: Map<ToolPanelEventType, Set<EventCallback>> = new Map();
  private globalSubscribers: Set<EventCallback> = new Set();

  /**
   * Subscribe to a specific event type
   */
  subscribe(eventType: ToolPanelEventType, callback: EventCallback): () => void {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, new Set());
    }
    this.subscribers.get(eventType)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.subscribers.get(eventType)?.delete(callback);
    };
  }

  /**
   * Subscribe to all events (global listener)
   */
  subscribeAll(callback: EventCallback): () => void {
    this.globalSubscribers.add(callback);
    return () => {
      this.globalSubscribers.delete(callback);
    };
  }

  /**
   * Publish an event to all subscribers
   */
  publish(source: string, event: ToolPanelEvent): void {
    // Notify specific event type subscribers
    const specificSubscribers = this.subscribers.get(event.type);
    if (specificSubscribers) {
      specificSubscribers.forEach(callback => {
        try {
          callback(event);
        } catch (error) {
          console.error(`Error in event callback for ${event.type}:`, error);
        }
      });
    }

    // Notify global subscribers
    this.globalSubscribers.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error(`Error in global event callback:`, error);
      }
    });
  }

  /**
   * Clear all subscribers
   */
  clear(): void {
    this.subscribers.clear();
    this.globalSubscribers.clear();
  }
}

// Singleton instance
export const toolPanelEventBus = new ToolPanelEventBus();

/**
 * Helper function to create and publish tool panel events
 */
export function createToolPanelEvent(
  type: ToolPanelEventType,
  payload: Record<string, unknown>,
  source = 'tool-bridge'
): void {
  toolPanelEventBus.publish(source, {
    type,
    payload,
    timestamp: Date.now(),
  });
}
