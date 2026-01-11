//
//  DashboardView.swift
//  FallDetectionApp
//
//  Dashboard chính hiển thị trạng thái hệ thống
//

import SwiftUI

struct DashboardView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Connection Status Card
                    ConnectionStatusCard()
                    
                    // System Status Card
                    if let status = webSocketManager.systemStatus {
                        SystemStatusCard(status: status)
                    }
                    
                    // Latest Alert Card
                    if let alert = webSocketManager.latestAlert {
                        LatestAlertCard(alert: alert)
                    }
                    
                    // Quick Stats
                    QuickStatsView()
                }
                .padding()
            }
            .navigationTitle("Giám Sát")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        webSocketManager.refresh()
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
    }
}

// MARK: - Connection Status Card

struct ConnectionStatusCard: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Circle()
                    .fill(statusColor)
                    .frame(width: 12, height: 12)
                
                Text(webSocketManager.connectionStatus.displayName)
                    .font(.headline)
                
                Spacer()
            }
            
            if let error = webSocketManager.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.red)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
    
    var statusColor: Color {
        switch webSocketManager.connectionStatus {
        case .connected: return .green
        case .connecting: return .orange
        case .disconnected: return .gray
        case .error: return .red
        }
    }
}

// MARK: - System Status Card

struct SystemStatusCard: View {
    let status: SystemStatus
    
    var body: some View {
        VStack(spacing: 16) {
            Text("Trạng Thái Hệ Thống")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(spacing: 12) {
                StatusRow(
                    icon: "video.fill",
                    label: "Camera",
                    value: status.isRunning ? "Đang hoạt động" : "Dừng",
                    color: status.isRunning ? .green : .red
                )
                
                StatusRow(
                    icon: "person.2.fill",
                    label: "Số người",
                    value: "\(status.activePeople)",
                    color: .blue
                )
                
                StatusRow(
                    icon: "speedometer",
                    label: "FPS",
                    value: String(format: "%.1f", status.fps),
                    color: status.fps > 20 ? .green : .orange
                )
                
                if let cpu = status.cpuUsage {
                    StatusRow(
                        icon: "cpu",
                        label: "CPU",
                        value: String(format: "%.1f%%", cpu),
                        color: cpu > 80 ? .red : .green
                    )
                }
                
                if let memory = status.memoryUsage {
                    StatusRow(
                        icon: "memorychip",
                        label: "RAM",
                        value: String(format: "%.1f%%", memory),
                        color: memory > 80 ? .red : .green
                    )
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct StatusRow: View {
    let icon: String
    let label: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(color)
                .frame(width: 24)
            
            Text(label)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .fontWeight(.semibold)
                .foregroundColor(color)
        }
    }
}

// MARK: - Latest Alert Card

struct LatestAlertCard: View {
    let alert: FallAlert
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Text("Cảnh Báo Gần Nhất")
                    .font(.headline)
                Spacer()
                Text(alert.timestamp, style: .relative)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: severityIcon)
                        .foregroundColor(severityColor)
                    Text(alert.severity.displayName)
                        .fontWeight(.semibold)
                        .foregroundColor(severityColor)
                    Spacer()
                    Text("Risk: \(alert.riskScore)")
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(severityColor.opacity(0.2))
                        .cornerRadius(8)
                }
                
                Text(alert.message)
                    .font(.body)
                
                if let location = alert.location {
                    HStack {
                        Image(systemName: "location.fill")
                            .font(.caption)
                        Text(location)
                            .font(.caption)
                    }
                    .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(severityColor.opacity(0.1))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(severityColor, lineWidth: 2)
        )
    }
    
    var severityColor: Color {
        switch alert.severity {
        case .warning: return .yellow
        case .alarm: return .orange
        case .emergency: return .red
        }
    }
    
    var severityIcon: String {
        switch alert.severity {
        case .warning: return "exclamationmark.triangle.fill"
        case .alarm: return "bell.fill"
        case .emergency: return "exclamationmark.octagon.fill"
        }
    }
}

// MARK: - Quick Stats

struct QuickStatsView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        VStack(spacing: 12) {
            Text("Thống Kê Nhanh")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            HStack(spacing: 12) {
                StatBox(
                    title: "Tổng cảnh báo",
                    value: "\(webSocketManager.alertHistory.count)",
                    color: .blue
                )
                
                StatBox(
                    title: "Khẩn cấp",
                    value: "\(emergencyCount)",
                    color: .red
                )
                
                StatBox(
                    title: "Hôm nay",
                    value: "\(todayCount)",
                    color: .green
                )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
    
    var emergencyCount: Int {
        webSocketManager.alertHistory.filter { $0.severity == .emergency }.count
    }
    
    var todayCount: Int {
        let today = Calendar.current.startOfDay(for: Date())
        return webSocketManager.alertHistory.filter { 
            Calendar.current.isDate($0.timestamp, inSameDayAs: today)
        }.count
    }
}

struct StatBox: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Text(value)
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

#Preview {
    DashboardView()
        .environmentObject(WebSocketManager())
}
