//
//  WebSocketManager.swift
//  FallDetectionApp
//
//  WebSocket Manager để kết nối với backend Python
//

import Foundation
import Combine

/// Manager để quản lý kết nối WebSocket với backend
class WebSocketManager: NSObject, ObservableObject {
    // MARK: - Published Properties
    
    @Published var connectionStatus: ConnectionStatus = .disconnected
    @Published var systemStatus: SystemStatus?
    @Published var latestAlert: FallAlert?
    @Published var alertHistory: [FallAlert] = []
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    
    private var webSocketTask: URLSessionWebSocketTask?
    private var urlSession: URLSession?
    private var serverURL: URL?
    private var reconnectTimer: Timer?
    private var heartbeatTimer: Timer?
    private let maxReconnectAttempts = 5
    private var reconnectAttempts = 0
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        urlSession = URLSession(configuration: config, delegate: self, delegateQueue: nil)
    }
    
    // MARK: - Connection Methods
    
    /// Kết nối đến WebSocket server
    func connect(host: String, port: Int) {
        // Ngắt kết nối cũ nếu có
        disconnect()
        
        // Tạo URL
        guard let url = URL(string: "ws://\(host):\(port)") else {
            errorMessage = "URL không hợp lệ"
            connectionStatus = .error
            return
        }
        
        serverURL = url
        connectionStatus = .connecting
        
        // Tạo WebSocket task
        webSocketTask = urlSession?.webSocketTask(with: url)
        webSocketTask?.resume()
        
        // Bắt đầu nhận messages
        receiveMessage()
        
        // Bắt đầu heartbeat
        startHeartbeat()
        
        print("[WebSocket] Connecting to \(url)")
    }
    
    /// Ngắt kết nối
    func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = nil
        connectionStatus = .disconnected
        
        stopHeartbeat()
        stopReconnect()
        
        print("[WebSocket] Disconnected")
    }
    
    /// Reconnect với exponential backoff
    private func reconnect() {
        guard reconnectAttempts < maxReconnectAttempts,
              let url = serverURL else {
            errorMessage = "Không thể kết nối lại sau \(maxReconnectAttempts) lần thử"
            connectionStatus = .error
            return
        }
        
        reconnectAttempts += 1
        let delay = min(pow(2.0, Double(reconnectAttempts)), 30.0)
        
        print("[WebSocket] Reconnecting in \(delay)s (attempt \(reconnectAttempts))")
        
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            guard let self = self else { return }
            self.webSocketTask = self.urlSession?.webSocketTask(with: url)
            self.webSocketTask?.resume()
            self.receiveMessage()
        }
    }
    
    private func stopReconnect() {
        reconnectTimer?.invalidate()
        reconnectTimer = nil
        reconnectAttempts = 0
    }
    
    // MARK: - Message Handling
    
    /// Nhận message từ server
    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            guard let self = self else { return }
            
            switch result {
            case .success(let message):
                self.handleMessage(message)
                // Tiếp tục nhận message tiếp theo
                self.receiveMessage()
                
            case .failure(let error):
                print("[WebSocket] Receive error: \(error)")
                DispatchQueue.main.async {
                    self.connectionStatus = .disconnected
                    self.errorMessage = error.localizedDescription
                }
                self.reconnect()
            }
        }
    }
    
    /// Xử lý message nhận được
    private func handleMessage(_ message: URLSessionWebSocketTask.Message) {
        switch message {
        case .string(let text):
            handleTextMessage(text)
        case .data(let data):
            handleDataMessage(data)
        @unknown default:
            break
        }
    }
    
    /// Xử lý text message (JSON)
    private func handleTextMessage(_ text: String) {
        guard let data = text.data(using: .utf8) else { return }
        handleDataMessage(data)
    }
    
    /// Xử lý data message
    private func handleDataMessage(_ data: Data) {
        do {
            let decoder = JSONDecoder()
            let wsMessage = try decoder.decode(WSMessage.self, from: data)
            
            DispatchQueue.main.async { [weak self] in
                guard let self = self else { return }
                
                // Update connection status nếu đang connecting
                if self.connectionStatus == .connecting {
                    self.connectionStatus = .connected
                    self.reconnectAttempts = 0
                }
                
                switch wsMessage.type {
                case .alert:
                    if case .alert(let alert) = wsMessage.data {
                        self.handleAlert(alert)
                    }
                    
                case .status:
                    if case .status(let status) = wsMessage.data {
                        self.systemStatus = status
                    }
                    
                case .heartbeat:
                    // Server responding to heartbeat
                    break
                }
            }
        } catch {
            print("[WebSocket] Parse error: \(error)")
        }
    }
    
    /// Xử lý alert mới
    private func handleAlert(_ alert: FallAlert) {
        latestAlert = alert
        alertHistory.insert(alert, at: 0)
        
        // Giới hạn history
        if alertHistory.count > 100 {
            alertHistory = Array(alertHistory.prefix(100))
        }
        
        // Trigger notification
        NotificationManager.shared.sendAlertNotification(alert)
        
        print("[WebSocket] New alert: \(alert.severity.rawValue) - \(alert.message)")
    }
    
    /// Gửi message đến server
    private func sendMessage(_ message: String) {
        let message = URLSessionWebSocketTask.Message.string(message)
        webSocketTask?.send(message) { error in
            if let error = error {
                print("[WebSocket] Send error: \(error)")
            }
        }
    }
    
    // MARK: - Heartbeat
    
    /// Bắt đầu gửi heartbeat
    private func startHeartbeat() {
        heartbeatTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in
            self?.sendHeartbeat()
        }
    }
    
    /// Dừng heartbeat
    private func stopHeartbeat() {
        heartbeatTimer?.invalidate()
        heartbeatTimer = nil
    }
    
    /// Gửi heartbeat message
    private func sendHeartbeat() {
        let heartbeat = "{\"type\":\"heartbeat\"}"
        sendMessage(heartbeat)
    }
    
    // MARK: - Public Methods
    
    /// Clear alert history
    func clearAlertHistory() {
        alertHistory.removeAll()
        latestAlert = nil
    }
    
    /// Refresh connection
    func refresh() {
        if let url = serverURL {
            let components = URLComponents(url: url, resolvingAgainstBaseURL: false)
            if let host = components?.host, let port = components?.port {
                connect(host: host, port: port)
            }
        }
    }
}

// MARK: - URLSessionWebSocketDelegate

extension WebSocketManager: URLSessionWebSocketDelegate {
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        print("[WebSocket] Connection opened")
        DispatchQueue.main.async {
            self.connectionStatus = .connected
            self.reconnectAttempts = 0
            self.errorMessage = nil
        }
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        print("[WebSocket] Connection closed: \(closeCode)")
        DispatchQueue.main.async {
            self.connectionStatus = .disconnected
        }
        reconnect()
    }
}
