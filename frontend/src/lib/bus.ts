/**
 * Event bus for cross-component communication
 * Used to trigger task list refresh when tasks are modified via chatbot
 */

type EventCallback = () => void;

const listeners: Set<EventCallback> = new Set();

export const taskEvents = {
  /**
   * Emit a task refresh event
   */
  emitRefresh: () => {
    listeners.forEach(callback => callback());
  },

  /**
   * Subscribe to task refresh events
   * Returns a cleanup function to unsubscribe
   */
  onRefresh: (callback: EventCallback): (() => void) => {
    listeners.add(callback);
    return () => {
      listeners.delete(callback);
    };
  },
};
