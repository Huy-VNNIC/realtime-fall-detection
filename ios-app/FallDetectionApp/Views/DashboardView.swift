//
//  DashboardView.swift
//  FallDetectionApp
//
//  Enhanced Dashboard with animations and new features
//

import SwiftUI

struct DashboardView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @State private var isRefreshing = false
    @State private var showingDetailedStats = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Connection Status Card with Animation
                    ConnectionStatusCard()
                        .transition(.scale.combined(with: .opacity))
                    
                    // Live Monitoring Card
                    LiveMonitoringCard()
                    
                    // System Status Card
                    if let status = webSocketManager.systemStatus {
                        SystemStatusCard(status: status)
                            .transition(.slide.combined(with: .opacity))
                    }
                    
                    // Latest Alert Card with Pulse Animation
                    if let alert = webSocketManager.latestAlert {
                        LatestAlertCard(alert: alert)
                            .transition(.move(edge: .top).combined(with: .opacity))
                    }
                    
                    // Quick Stats with Gradient
                    QuickStatsView()
                    
                    // Activity Timeline
                    ActivityTimelineView()
                    
                    // System Health Card
                    SystemHealthCard()
                }
                .padding()
            }
            .navigationTitle("Giám Sát Realtime")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: { showingDetailedStats.toggle() }) {
                        Image(systemName: "chart.xyaxis.line")
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: refreshDashboard) {
                        Image(systemName: "arrow.clockwise")
                            .rotationEffect(.degrees(isRefreshing ? 360 : 0))
                            .animation(
                                isRefreshing ? .linear(duration: 1).repeatForever(autoreverses: false) : .default,
                                value: isRefreshing
                            )
                    }
                }
            }
            .sheet(isPresented: $showingDetailedStats) {
                DetailedStatsView()
            }
        }
    }
    
    private func refreshDashboard() {
        isRefreshing = true
        webSocketManager.refresh()
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            isRefreshing = false
        }
    }
}

// MARK: - Connection Status Card

struct ConnectionStatusCard: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @State private var pulseAnimation = false
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Circle()
                    .fill(statusColor)
                    .frame(width: 12, height: 12)
                    .scaleEffect(pulseAnimation ? 1.2 : 1.0)
                    .opacity(pulseAnimation ? 0.5 : 1.0)
                    .animation(.easeInOut(duration: 1).repeatForever(autoreverses: true), value: pulseAnimation)
                
                Text(webSocketManager.connectionStatus.displayName)
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Spacer()
                
                if webSocketManager.connectionStatus == .connected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                        .font(.title3)
                }
            }
            
            if let error = webSocketManager.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.red)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .padding()
        .background(
            LinearGradient(
                colors: [statusColor.opacity(0.1), statusColor.opacity(0.05)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(12)
        .shadow(color: statusColor.opacity(0.3), radius: 5)
        .onAppear { pulseAnimation = true }
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

// MARK: - Live Monitoring Card

struct LiveMonitoringCard: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @State private var waveAnimation = false
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: "waveform.path.ecg")
                    .font(.title2)
                    .foregroundColor(.blue)
                    .scaleEffect(waveAnimation ? 1.2 : 1.0)
                    .animation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true), value: waveAnimation)
                
                Text("Đang Giám Sát Trực Tiếp")
                    .font(.headline)
                
                Spacer()
                
                Text("LIVE")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.red)
                    .cornerRadius(4)
            }
            
            if let status = webSocketManager.systemStatus {
                HStack(spacing: 20) {
                    MonitoringMetric(
                        icon: "person.2.fill",
                        value: "\(status.activePeople)",
                        label: "Người đang giám sát"
                    )
                    
                    Divider()
                    
                    MonitoringMetric(
                        icon: "clock.fill",
                        value: timeRunning(),
                        label: "Thời gian chạy"
                    )
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
        .onAppear { waveAnimation = true }
    }
    
    private func timeRunning() -> String {
        // Simplified - would calculate actual uptime
        return "2h 15m"
    }
}

struct MonitoringMetric: View {
    let icon: String
    let value: String
    let label: String
    
    var body: some View {
        VStack(spacing: 4) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .foregroundColor(.blue)
                Text(value)
                    .font(.title2)
                    .fontWeight(.bold)
            }
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
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
    @State private var showingDetails = false
    @State private var pulseAnimation = false
    
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
            
            Button(action: { showingDetails.toggle() }) {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: severityIcon)
                            .foregroundColor(severityColor)
                            .font(.title3)
                            .scaleEffect(pulseAnimation ? 1.1 : 1.0)
                            .animation(.easeInOut(duration: 0.5).repeatForever(autoreverses: true), value: pulseAnimation)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(alert.severity.displayName)
                                .fontWeight(.semibold)
                                .foregroundColor(severityColor)
                            
                            Text(alert.eventType.displayName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing) {
                            Text("Risk")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("\(alert.riskScore)")
                                .font(.title3)
                                .fontWeight(.bold)
                                .foregroundColor(severityColor)
                        }
                        .padding(8)
                        .background(severityColor.opacity(0.2))
                        .cornerRadius(8)
                    }
                    
                    Text(alert.message)
                        .font(.body)
                        .foregroundColor(.primary)
                        .multilineTextAlignment(.leading)
                    
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
            .buttonStyle(PlainButtonStyle())
        }
        .padding()
        .background(severityColor.opacity(0.1))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(severityColor, lineWidth: 2)
        )
        .shadow(color: severityColor.opacity(0.3), radius: 5)
        .onAppear { pulseAnimation = alert.severity == .emergency }
        .sheet(isPresented: $showingDetails) {
            AlertDetailView(alert: alert)
        }
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

// MARK: - Alert Detail View

struct AlertDetailView: View {
    let alert: FallAlert
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Alert Header
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: severityIcon)
                                .font(.largeTitle)
                                .foregroundColor(severityColor)
                            
                            VStack(alignment: .leading) {
                                Text(alert.severity.displayName)
                                    .font(.title2)
                                    .fontWeight(.bold)
                                
                                Text(alert.eventType.displayName)
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                        
                        Text(alert.message)
                            .font(.body)
                            .padding(.top, 4)
                    }
                    .padding()
                    .background(severityColor.opacity(0.1))
                    .cornerRadius(12)
                    
                    // Details
                    Group {
                        DetailRow(icon: "clock", label: "Thời gian", value: alert.timestamp.formatted())
                        DetailRow(icon: "number", label: "ID người", value: "#\(alert.trackId)")
                        DetailRow(icon: "chart.bar.fill", label: "Risk Score", value: "\(alert.riskScore)/100")
                        
                        if let location = alert.location {
                            DetailRow(icon: "location.fill", label: "Vị trí", value: location)
                        }
                    }
                    
                    // Metadata
                    if let metadata = alert.metadata {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Chi Tiết")
                                .font(.headline)
                            
                            if let fallDuration = metadata.fallDuration {
                                DetailRow(icon: "timer", label: "Thời gian ngã", value: String(format: "%.1fs", fallDuration))
                            }
                            
                            if let immobility = metadata.immobilityDuration {
                                DetailRow(icon: "figure.stand", label: "Thời gian bất động", value: String(format: "%.1fs", immobility))
                            }
                            
                            if let position = metadata.positionInfo {
                                DetailRow(icon: "person.fill", label: "Tư thế", value: position)
                            }
                        }
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(12)
                    }
                    
                    // Actions
                    VStack(spacing: 12) {
                        ActionButton(icon: "phone.fill", title: "Gọi Cấp Cứu", color: .red) {}
                        ActionButton(icon: "message.fill", title: "Gửi Tin Nhắn", color: .blue) {}
                        ActionButton(icon: "doc.text.fill", title: "Xuất Báo Cáo", color: .green) {}
                    }
                }
                .padding()
            }
            .navigationTitle("Chi Tiết Cảnh Báo")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Đóng") {
                        dismiss()
                    }
                }
            }
        }
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

struct DetailRow: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 24)
            
            Text(label)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .fontWeight(.semibold)
        }
        .padding(.vertical, 4)
    }
}

struct ActionButton: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
                Spacer()
                Image(systemName: "chevron.right")
            }
            .foregroundColor(.white)
            .padding()
            .background(color)
            .cornerRadius(10)
        }
    }
}

// MARK: - Activity Timeline View

struct ActivityTimelineView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Hoạt Động Gần Đây")
                .font(.headline)
            
            if webSocketManager.alertHistory.isEmpty {
                EmptyActivityView()
            } else {
                VStack(spacing: 8) {
                    ForEach(webSocketManager.alertHistory.prefix(5)) { alert in
                        TimelineItemView(alert: alert)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct TimelineItemView: View {
    let alert: FallAlert
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(severityColor)
                .frame(width: 8, height: 8)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(alert.message)
                    .font(.subheadline)
                    .lineLimit(1)
                
                Text(alert.timestamp, style: .relative)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
    }
    
    var severityColor: Color {
        switch alert.severity {
        case .warning: return .yellow
        case .alarm: return .orange
        case .emergency: return .red
        }
    }
}

struct EmptyActivityView: View {
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: "checkmark.circle.fill")
                .font(.title)
                .foregroundColor(.green)
            Text("Không có cảnh báo gần đây")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
    }
}

// MARK: - System Health Card

struct SystemHealthCard: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Sức Khỏe Hệ Thống")
                .font(.headline)
            
            if let status = webSocketManager.systemStatus {
                VStack(spacing: 12) {
                    HealthIndicator(
                        label: "FPS",
                        value: status.fps,
                        threshold: 20,
                        unit: ""
                    )
                    
                    if let cpu = status.cpuUsage {
                        HealthIndicator(
                            label: "CPU",
                            value: cpu,
                            threshold: 80,
                            unit: "%"
                        )
                    }
                    
                    if let memory = status.memoryUsage {
                        HealthIndicator(
                            label: "Memory",
                            value: memory,
                            threshold: 80,
                            unit: "%"
                        )
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct HealthIndicator: View {
    let label: String
    let value: Double
    let threshold: Double
    let unit: String
    
    var isHealthy: Bool {
        value >= threshold
    }
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text(label)
                    .foregroundColor(.secondary)
                Spacer()
                Text(String(format: "%.1f%@", value, unit))
                    .fontWeight(.semibold)
                    .foregroundColor(isHealthy ? .green : .orange)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color(.systemGray5))
                        .frame(height: 6)
                        .cornerRadius(3)
                    
                    Rectangle()
                        .fill(LinearGradient(
                            colors: isHealthy ? [.green, .blue] : [.orange, .red],
                            startPoint: .leading,
                            endPoint: .trailing
                        ))
                        .frame(width: geometry.size.width * CGFloat(min(value / 100, 1.0)), height: 6)
                        .cornerRadius(3)
                        .animation(.easeInOut, value: value)
                }
            }
            .frame(height: 6)
        }
    }
}

// MARK: - Detailed Stats View

struct DetailedStatsView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            List {
                Section("Kết Nối") {
                    StatRow(label: "Trạng thái", value: webSocketManager.connectionStatus.displayName)
                    StatRow(label: "Số lần kết nối lại", value: "0")
                }
                
                if let status = webSocketManager.systemStatus {
                    Section("Hệ Thống") {
                        StatRow(label: "FPS", value: String(format: "%.1f", status.fps))
                        StatRow(label: "Người đang theo dõi", value: "\(status.activePeople)")
                        
                        if let cpu = status.cpuUsage {
                            StatRow(label: "CPU", value: String(format: "%.1f%%", cpu))
                        }
                        
                        if let memory = status.memoryUsage {
                            StatRow(label: "RAM", value: String(format: "%.1f%%", memory))
                        }
                    }
                }
                
                Section("Cảnh Báo") {
                    StatRow(label: "Tổng số", value: "\(webSocketManager.alertHistory.count)")
                    StatRow(label: "Hôm nay", value: "\(todayAlertCount)")
                    StatRow(label: "Tuần này", value: "\(weekAlertCount)")
                }
            }
            .navigationTitle("Thống Kê Chi Tiết")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Đóng") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    var todayAlertCount: Int {
        let today = Calendar.current.startOfDay(for: Date())
        return webSocketManager.alertHistory.filter {
            Calendar.current.isDate($0.timestamp, inSameDayAs: today)
        }.count
    }
    
    var weekAlertCount: Int {
        let weekAgo = Calendar.current.date(byAdding: .day, value: -7, to: Date())!
        return webSocketManager.alertHistory.filter {
            $0.timestamp >= weekAgo
        }.count
    }
}

struct StatRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
            Spacer()
            Text(value)
                .fontWeight(.semibold)
                .foregroundColor(.blue)
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
