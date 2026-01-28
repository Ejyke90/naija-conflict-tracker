import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * WebSocket connection status
 */
export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'polling-fallback';

/**
 * Options for the useWebSocket hook
 */
export interface UseWebSocketOptions {
  endpoint: string;
  onMessage?: (data: any) => void;
  onStatusChange?: (status: WebSocketStatus) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  enableLogging?: boolean;
}

/**
 * Custom hook for WebSocket connection management with automatic polling fallback
 * 
 * @param options - Configuration options for WebSocket behavior
 * @returns Object containing connection status, last message, and disconnect function
 */
export function useWebSocket({
  endpoint,
  onMessage,
  onStatusChange,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
  enableLogging = false,
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<WebSocketStatus>('connecting');
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [isUsingFallback, setIsUsingFallback] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);
  const lastHeartbeatRef = useRef<number>(Date.now());

  const log = useCallback(
    (message: string, data?: any) => {
      if (enableLogging) {
        console.log(`[WebSocket] ${message}`, data);
      }
    },
    [enableLogging]
  );

  const updateStatus = useCallback(
    (newStatus: WebSocketStatus) => {
      if (isMountedRef.current) {
        setStatus(newStatus);
        onStatusChange?.(newStatus);
        log(`Status changed to: ${newStatus}`);
      }
    },
    [onStatusChange, log]
  );

  /**
   * Construct WebSocket URL from environment variable
   * Converts HTTP(S) -> WS(S)
   */
  const getWebSocketUrl = useCallback((): string => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Convert HTTP(S) URL to WS(S)
    const protocol = apiUrl.includes('https') ? 'wss' : 'ws';
    const baseUrl = apiUrl.replace(/^https?:\/\//, '');
    
    return `${protocol}://${baseUrl}${endpoint}`;
  }, [endpoint]);

  /**
   * Fallback polling mechanism when WebSocket is unavailable
   */
  const startPolling = useCallback(async () => {
    log('Starting polling fallback (5-second interval)');
    updateStatus('polling-fallback');
    setIsUsingFallback(true);

    pollingIntervalRef.current = setInterval(async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/monitoring/pipeline-status`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        
        if (isMountedRef.current) {
          setLastMessage(data);
          onMessage?.(data);
        }
      } catch (error) {
        log('Polling fetch failed:', error);
      }
    }, 5000); // 5-second polling interval
  }, [log, updateStatus, onMessage]);

  /**
   * Stop the polling fallback
   */
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
      setIsUsingFallback(false);
      log('Polling fallback stopped');
    }
  }, [log]);

  /**
   * Connect to WebSocket with automatic fallback to polling
   */
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      log('WebSocket already connected');
      return;
    }

    updateStatus('connecting');
    const wsUrl = getWebSocketUrl();

    try {
      log(`Attempting to connect to ${wsUrl}`);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (!isMountedRef.current) return;
        
        log('WebSocket connected');
        updateStatus('connected');
        reconnectAttemptsRef.current = 0;
        lastHeartbeatRef.current = Date.now();
        
        // Clear reconnect timeout if exists
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }

        // Stop polling if it was active
        stopPolling();
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;

        try {
          const data = JSON.parse(event.data);
          lastHeartbeatRef.current = Date.now();
          setLastMessage(data);
          onMessage?.(data);
          log('Message received', data);
        } catch (error) {
          log('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        if (!isMountedRef.current) return;
        log('WebSocket error:', error);
        // Errors will be handled by onclose
      };

      ws.onclose = () => {
        if (!isMountedRef.current) return;

        log('WebSocket closed');
        wsRef.current = null;

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          updateStatus('reconnecting');
          reconnectAttemptsRef.current++;
          
          // Exponential backoff: 1s, 2s, 4s, 8s, 16s
          const backoffDelay = Math.min(
            reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1),
            30000
          );
          
          log(`Reconnecting in ${backoffDelay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              connect();
            }
          }, backoffDelay);
        } else {
          // Max reconnection attempts reached, fall back to polling
          log('Max reconnection attempts reached, switching to polling fallback');
          startPolling();
        }
      };

      wsRef.current = ws;
    } catch (error) {
      log('WebSocket connection error:', error);
      updateStatus('disconnected');
      
      // Fall back to polling immediately
      startPolling();
    }
  }, [
    getWebSocketUrl,
    updateStatus,
    log,
    onMessage,
    maxReconnectAttempts,
    reconnectInterval,
    stopPolling,
    startPolling,
  ]);

  /**
   * Disconnect WebSocket and stop polling
   */
  const disconnect = useCallback(() => {
    log('Disconnecting WebSocket and polling');

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Clear timeouts
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Stop polling
    stopPolling();

    updateStatus('disconnected');
  }, [log, stopPolling, updateStatus]);

  /**
   * Effect: Connect on mount, disconnect on unmount
   */
  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;
      disconnect();
    };
  }, [connect, disconnect, endpoint]);

  /**
   * Heartbeat check: Reconnect if no messages received in 30 seconds
   */
  useEffect(() => {
    const heartbeatInterval = setInterval(() => {
      if (isMountedRef.current && status === 'connected') {
        const timeSinceLastMessage = Date.now() - lastHeartbeatRef.current;
        
        if (timeSinceLastMessage > 30000) {
          log('No heartbeat received in 30 seconds, reconnecting...');
          disconnect();
          setTimeout(() => {
            if (isMountedRef.current) {
              connect();
            }
          }, 1000);
        }
      }
    }, 10000); // Check every 10 seconds

    return () => clearInterval(heartbeatInterval);
  }, [status, log, connect, disconnect]);

  return {
    status,
    lastMessage,
    isUsingFallback,
    connect,
    disconnect,
  };
}
