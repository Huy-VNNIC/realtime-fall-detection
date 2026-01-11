//
//  Models.swift
//  FallDetectionApp
//
//  Data models cho Fall Detection System
//

import Foundation

// MARK: - Alert Models

/// Trạng thái cảnh báo
enum AlertSeverity: String, Codable, CaseIterable {
    case warning = "WARNING"
    case alarm = "ALARM"
    case emergency = "EMERGENCY"
    
    var displayName: String {
        switch self {
        case .warning: return "Cảnh báo"
        case .alarm: return "Báo động"
        case .emergency: return "Khẩn cấp"
        }
    }
    
    var color: String {
        switch self {
        case .warning: return "yellow"
        case .alarm: return "orange"
        case .emergency: return "red"
        }
    }
}

/// Loại sự kiện
enum EventType: String, Codable {
    case fall = "FALL"
    case immobility = "IMMOBILITY"
    case recovery = "RECOVERY"
    
    var displayName: String {
        switch self {
        case .fall: return "Té ngã"
        case .immobility: return "Bất động"
        case .recovery: return "Hồi phục"
        }
    }
}

/// Model cho một cảnh báo
struct FallAlert: Identifiable, Codable {
    let id: String
    let trackId: Int
    let severity: AlertSeverity
    let eventType: EventType
    let riskScore: Int
    let timestamp: Date
    let location: String?
    let message: String
    let metadata: AlertMetadata?
    
    enum CodingKeys: String, CodingKey {
        case id = "alert_id"
        case trackId = "track_id"
        case severity
        case eventType = "event_type"
        case riskScore = "risk_score"
        case timestamp
        case location
        case message
        case metadata
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        trackId = try container.decode(Int.self, forKey: .trackId)
        severity = try container.decode(AlertSeverity.self, forKey: .severity)
        eventType = try container.decode(EventType.self, forKey: .eventType)
        riskScore = try container.decode(Int.self, forKey: .riskScore)
        location = try container.decodeIfPresent(String.self, forKey: .location)
        message = try container.decode(String.self, forKey: .message)
        metadata = try container.decodeIfPresent(AlertMetadata.self, forKey: .metadata)
        
        // Parse timestamp
        let timestampString = try container.decode(String.self, forKey: .timestamp)
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = formatter.date(from: timestampString) {
            timestamp = date
        } else {
            timestamp = Date()
        }
    }
}

/// Metadata bổ sung cho cảnh báo
struct AlertMetadata: Codable {
    let fallDuration: Double?
    let immobilityDuration: Double?
    let positionInfo: String?
    
    enum CodingKeys: String, CodingKey {
        case fallDuration = "fall_duration"
        case immobilityDuration = "immobility_duration"
        case positionInfo = "position_info"
    }
}

// MARK: - System Status Models

/// Trạng thái kết nối
enum ConnectionStatus: String {
    case connected = "connected"
    case connecting = "connecting"
    case disconnected = "disconnected"
    case error = "error"
    
    var displayName: String {
        switch self {
        case .connected: return "Đã kết nối"
        case .connecting: return "Đang kết nối..."
        case .disconnected: return "Mất kết nối"
        case .error: return "Lỗi"
        }
    }
}

/// Trạng thái hệ thống
struct SystemStatus: Codable {
    let isRunning: Bool
    let activePeople: Int
    let fps: Double
    let cpuUsage: Double?
    let memoryUsage: Double?
    let timestamp: Date
    
    enum CodingKeys: String, CodingKey {
        case isRunning = "is_running"
        case activePeople = "active_people"
        case fps
        case cpuUsage = "cpu_usage"
        case memoryUsage = "memory_usage"
        case timestamp
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        isRunning = try container.decode(Bool.self, forKey: .isRunning)
        activePeople = try container.decode(Int.self, forKey: .activePeople)
        fps = try container.decode(Double.self, forKey: .fps)
        cpuUsage = try container.decodeIfPresent(Double.self, forKey: .cpuUsage)
        memoryUsage = try container.decodeIfPresent(Double.self, forKey: .memoryUsage)
        timestamp = Date()
    }
}

// MARK: - WebSocket Messages

/// Loại message từ WebSocket
enum WSMessageType: String, Codable {
    case alert = "alert"
    case status = "status"
    case heartbeat = "heartbeat"
}

/// Base message từ WebSocket
struct WSMessage: Codable {
    let type: WSMessageType
    let data: WSMessageData?
}

/// Data trong WebSocket message
enum WSMessageData: Codable {
    case alert(FallAlert)
    case status(SystemStatus)
    case heartbeat
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if let alert = try? container.decode(FallAlert.self) {
            self = .alert(alert)
        } else if let status = try? container.decode(SystemStatus.self) {
            self = .status(status)
        } else {
            self = .heartbeat
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch self {
        case .alert(let alert):
            try container.encode(alert)
        case .status(let status):
            try container.encode(status)
        case .heartbeat:
            try container.encode("heartbeat")
        }
    }
}

// MARK: - Settings Models

/// Cài đặt ứng dụng
struct AppSettings: Codable {
    var serverHost: String
    var serverPort: Int
    var autoConnect: Bool
    var enableNotifications: Bool
    var notificationSound: Bool
    var minimumSeverity: AlertSeverity
    
    static var `default`: AppSettings {
        return AppSettings(
            serverHost: "192.168.1.100",
            serverPort: 8080,
            autoConnect: true,
            enableNotifications: true,
            notificationSound: true,
            minimumSeverity: .warning
        )
    }
}
