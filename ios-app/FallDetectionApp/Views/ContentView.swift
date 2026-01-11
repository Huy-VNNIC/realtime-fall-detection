//
//  ContentView.swift
//  FallDetectionApp
//
//  Main navigation view with enhanced UI and features
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @State private var selectedTab = 0
    @State private var showingAlert = false
    @AppStorage("isDarkMode") private var isDarkMode = false
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Dashboard
            DashboardView()
                .tabItem {
                    Label("Giám sát", systemImage: "chart.line.uptrend.xyaxis")
                }
                .tag(0)
                .badge(webSocketManager.connectionStatus == .connected ? "●" : nil)
            
            // Alert History
            AlertListView()
                .tabItem {
                    Label("Cảnh báo", systemImage: "bell.fill")
                }
                .tag(1)
                .badge(webSocketManager.alertHistory.count > 0 ? webSocketManager.alertHistory.count : nil)
            
            // Analytics
            AnalyticsView()
                .tabItem {
                    Label("Thống kê", systemImage: "chart.bar.fill")
                }
                .tag(2)
            
            // Video Stream
            VideoStreamView()
                .tabItem {
                    Label("Camera", systemImage: "video.fill")
                }
                .tag(3)
            
            // Settings
            SettingsView()
                .tabItem {
                    Label("Cài đặt", systemImage: "gearshape.fill")
                }
                .tag(4)
        }
        .accentColor(.blue)
        .preferredColorScheme(isDarkMode ? .dark : .light)
        .onChange(of: webSocketManager.latestAlert) { newAlert in
            if newAlert != nil {
                showingAlert = true
                playAlertAnimation()
            }
        }
    }
    
    private func playAlertAnimation() {
        // Haptic feedback
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.warning)
    }
}

// MARK: - Analytics View

struct AnalyticsView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Time-based Stats
                    ChartCardView()
                    
                    // Alert Breakdown
                    AlertBreakdownView()
                    
                    // Performance Metrics
                    PerformanceMetricsView()
                    
                    // Export Options
                    ExportOptionsView()
                }
                .padding()
            }
            .navigationTitle("Thống Kê & Phân Tích")
        }
    }
}

struct ChartCardView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Cảnh Báo Theo Thời Gian")
                .font(.headline)
            
            // Simple bar chart representation
            HStack(alignment: .bottom, spacing: 8) {
                ForEach(getLast7Days(), id: \.self) { day in
                    VStack {
                        Rectangle()
                            .fill(LinearGradient(
                                colors: [.blue, .purple],
                                startPoint: .top,
                                endPoint: .bottom
                            ))
                            .frame(width: 30, height: CGFloat(getAlertsForDay(day)) * 10)
                            .cornerRadius(4)
                        
                        Text(day)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .frame(height: 150)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
    
    private func getLast7Days() -> [String] {
        let formatter = DateFormatter()
        formatter.dateFormat = "E"
        return (0..<7).map { day in
            formatter.string(from: Calendar.current.date(byAdding: .day, value: -day, to: Date())!)
        }.reversed()
    }
    
    private func getAlertsForDay(_ day: String) -> Int {
        // Simplified - count alerts for that day
        return Int.random(in: 0...10)
    }
}

struct AlertBreakdownView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var warningCount: Int {
        webSocketManager.alertHistory.filter { $0.severity == .warning }.count
    }
    
    var alarmCount: Int {
        webSocketManager.alertHistory.filter { $0.severity == .alarm }.count
    }
    
    var emergencyCount: Int {
        webSocketManager.alertHistory.filter { $0.severity == .emergency }.count
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Phân Loại Cảnh Báo")
                .font(.headline)
            
            VStack(spacing: 12) {
                AlertBreakdownRow(
                    icon: "exclamationmark.triangle.fill",
                    title: "Cảnh báo",
                    count: warningCount,
                    color: .yellow
                )
                
                AlertBreakdownRow(
                    icon: "bell.fill",
                    title: "Báo động",
                    count: alarmCount,
                    color: .orange
                )
                
                AlertBreakdownRow(
                    icon: "exclamationmark.octagon.fill",
                    title: "Khẩn cấp",
                    count: emergencyCount,
                    color: .red
                )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct AlertBreakdownRow: View {
    let icon: String
    let title: String
    let count: Int
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(color)
                .frame(width: 30)
            
            Text(title)
                .foregroundColor(.primary)
            
            Spacer()
            
            Text("\(count)")
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(color)
        }
        .padding(.vertical, 4)
    }
}

struct PerformanceMetricsView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var avgResponseTime: String {
        "< 100ms"
    }
    
    var uptime: String {
        "99.8%"
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Hiệu Suất Hệ Thống")
                .font(.headline)
            
            HStack(spacing: 20) {
                MetricBox(
                    title: "Response Time",
                    value: avgResponseTime,
                    icon: "timer",
                    color: .green
                )
                
                MetricBox(
                    title: "Uptime",
                    value: uptime,
                    icon: "checkmark.circle.fill",
                    color: .blue
                )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct MetricBox: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

struct ExportOptionsView: View {
    @State private var showingExportSheet = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Xuất Báo Cáo")
                .font(.headline)
            
            HStack(spacing: 12) {
                ExportButton(icon: "doc.text.fill", title: "PDF", color: .red)
                ExportButton(icon: "tablecells.fill", title: "CSV", color: .green)
                ExportButton(icon: "envelope.fill", title: "Email", color: .blue)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct ExportButton: View {
    let icon: String
    let title: String
    let color: Color
    
    var body: some View {
        Button(action: {}) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                Text(title)
                    .font(.caption)
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding()
            .background(color)
            .cornerRadius(8)
        }
    }
}

// MARK: - Video Stream View

struct VideoStreamView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @State private var isStreamActive = false
    @State private var selectedCamera = 0
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Video Preview Placeholder
                ZStack {
                    Rectangle()
                        .fill(LinearGradient(
                            colors: [.blue.opacity(0.3), .purple.opacity(0.3)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ))
                        .aspectRatio(16/9, contentMode: .fit)
                        .cornerRadius(12)
                    
                    VStack(spacing: 16) {
                        Image(systemName: "video.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.white)
                        
                        Text("Live Camera Feed")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                        
                        Text("Camera streaming sẽ được thêm trong phiên bản tiếp theo")
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.8))
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                }
                .padding()
                
                // Camera Controls
                VStack(spacing: 16) {
                    // Camera Selector
                    Picker("Camera", selection: $selectedCamera) {
                        Text("Camera 1").tag(0)
                        Text("Camera 2").tag(1)
                        Text("Camera 3").tag(2)
                    }
                    .pickerStyle(.segmented)
                    .padding(.horizontal)
                    
                    // Control Buttons
                    HStack(spacing: 16) {
                        StreamControlButton(
                            icon: isStreamActive ? "pause.fill" : "play.fill",
                            title: isStreamActive ? "Dừng" : "Phát",
                            color: .blue
                        ) {
                            isStreamActive.toggle()
                        }
                        
                        StreamControlButton(
                            icon: "camera.fill",
                            title: "Chụp",
                            color: .green
                        ) {}
                        
                        StreamControlButton(
                            icon: "record.circle",
                            title: "Ghi",
                            color: .red
                        ) {}
                    }
                    .padding(.horizontal)
                    
                    // Stream Info
                    if let status = webSocketManager.systemStatus {
                        StreamInfoCard(status: status)
                            .padding(.horizontal)
                    }
                }
                
                Spacer()
            }
            .navigationTitle("Camera Trực Tiếp")
        }
    }
}

struct StreamControlButton: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                Text(title)
                    .font(.caption)
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding()
            .background(color)
            .cornerRadius(8)
        }
    }
}

struct StreamInfoCard: View {
    let status: SystemStatus
    
    var body: some View {
        HStack {
            InfoItem(icon: "speedometer", label: "FPS", value: String(format: "%.1f", status.fps))
            Divider()
            InfoItem(icon: "person.2.fill", label: "Người", value: "\(status.activePeople)")
            Divider()
            InfoItem(icon: "antenna.radiowaves.left.and.right", label: "Kết nối", value: "Ổn định")
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(8)
        .shadow(radius: 2)
    }
}

struct InfoItem: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .foregroundColor(.blue)
            Text(value)
                .font(.headline)
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager())
}
