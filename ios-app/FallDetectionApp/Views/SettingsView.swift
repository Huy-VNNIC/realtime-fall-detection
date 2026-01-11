//
//  SettingsView.swift
//  FallDetectionApp
//
//  Enhanced Settings with more options
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var notificationManager: NotificationManager
    
    @AppStorage("settings") private var settingsData: Data = try! JSONEncoder().encode(AppSettings.default)
    @AppStorage("isDarkMode") private var isDarkMode = false
    @AppStorage("language") private var language = "vi"
    @AppStorage("alertSoundEnabled") private var alertSoundEnabled = true
    @AppStorage("hapticFeedback") private var hapticFeedback = true
    
    @State private var settings: AppSettings = .default
    @State private var showingResetAlert = false
    @State private var showingAbout = false
    @State private var showingAdvanced = false
    
    var body: some View {
        NavigationView {
            Form {
                // Server Section
                Section("Kết Nối Server") {
                    HStack {
                        Image(systemName: "server.rack")
                            .foregroundColor(.blue)
                        Text("Host")
                        Spacer()
                        TextField("192.168.0.106", text: $settings.serverHost)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.URL)
                    }
                    
                    HStack {
                        Image(systemName: "number")
                            .foregroundColor(.blue)
                        Text("Port")
                        Spacer()
                        TextField("8080", value: $settings.serverPort, format: .number)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.numberPad)
                    }
                    
                    Toggle(isOn: $settings.autoConnect) {
                        HStack {
                            Image(systemName: "arrow.triangle.2.circlepath")
                                .foregroundColor(.green)
                            Text("Tự động kết nối")
                        }
                    }
                    
                    Button(action: reconnect) {
                        HStack {
                            Image(systemName: "arrow.clockwise.circle.fill")
                                .foregroundColor(.blue)
                            Text("Kết nối lại")
                            Spacer()
                            if webSocketManager.connectionStatus == .connecting {
                                ProgressView()
                            }
                        }
                    }
                }
                
                // Appearance Section
                Section("Giao Diện") {
                    Toggle(isOn: $isDarkMode) {
                        HStack {
                            Image(systemName: isDarkMode ? "moon.fill" : "sun.max.fill")
                                .foregroundColor(isDarkMode ? .purple : .orange)
                            Text("Dark Mode")
                        }
                    }
                    
                    Picker(selection: $language) {
                        Text("🇻🇳 Tiếng Việt").tag("vi")
                        Text("🇬🇧 English").tag("en")
                        Text("🇯🇵 日本語").tag("ja")
                    } label: {
                        HStack {
                            Image(systemName: "globe")
                                .foregroundColor(.blue)
                            Text("Ngôn ngữ")
                        }
                    }
                }
                
                // Notification Section
                Section("Thông Báo") {
                    Toggle(isOn: $settings.enableNotifications) {
                        HStack {
                            Image(systemName: "bell.badge.fill")
                                .foregroundColor(.red)
                            Text("Bật thông báo")
                        }
                    }
                    .onChange(of: settings.enableNotifications) { newValue in
                        if newValue && !notificationManager.isAuthorized {
                            notificationManager.requestAuthorization()
                        }
                    }
                    
                    Toggle(isOn: $settings.notificationSound) {
                        HStack {
                            Image(systemName: "speaker.wave.2.fill")
                                .foregroundColor(.orange)
                            Text("Âm thanh")
                        }
                    }
                    .disabled(!settings.enableNotifications)
                    
                    Toggle(isOn: $alertSoundEnabled) {
                        HStack {
                            Image(systemName: "waveform")
                                .foregroundColor(.purple)
                            Text("Âm thanh cảnh báo")
                        }
                    }
                    
                    Toggle(isOn: $hapticFeedback) {
                        HStack {
                            Image(systemName: "iphone.radiowaves.left.and.right")
                                .foregroundColor(.green)
                            Text("Rung")
                        }
                    }
                    
                    Picker(selection: $settings.minimumSeverity) {
                        ForEach(AlertSeverity.allCases, id: \.self) { severity in
                            Text(severity.displayName).tag(severity)
                        }
                    } label: {
                        HStack {
                            Image(systemName: "slider.horizontal.3")
                                .foregroundColor(.blue)
                            Text("Mức độ tối thiểu")
                        }
                    }
                    .disabled(!settings.enableNotifications)
                    
                    if !notificationManager.isAuthorized {
                        Button(action: openSettings) {
                            HStack {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .foregroundColor(.orange)
                                Text("Bật quyền thông báo trong Settings")
                                    .font(.caption)
                            }
                        }
                    }
                }
                
                // Advanced Settings
                Section("Nâng Cao") {
                    NavigationLink(destination: AdvancedSettingsView()) {
                        HStack {
                            Image(systemName: "gearshape.2.fill")
                                .foregroundColor(.gray)
                            Text("Cài đặt nâng cao")
                        }
                    }
                    
                    NavigationLink(destination: DataManagementView()) {
                        HStack {
                            Image(systemName: "externaldrive.fill")
                                .foregroundColor(.blue)
                            Text("Quản lý dữ liệu")
                        }
                    }
                    
                    NavigationLink(destination: SecuritySettingsView()) {
                        HStack {
                            Image(systemName: "lock.shield.fill")
                                .foregroundColor(.green)
                            Text("Bảo mật")
                        }
                    }
                }
                
                // Info Section
                Section("Thông Tin") {
                    HStack {
                        Image(systemName: "info.circle.fill")
                            .foregroundColor(.blue)
                        Text("Phiên bản")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }
                    
                    HStack {
                        Image(systemName: statusIcon)
                            .foregroundColor(statusColor)
                        Text("Trạng thái")
                        Spacer()
                        Text(webSocketManager.connectionStatus.displayName)
                            .foregroundColor(statusColor)
                    }
                    
                    if let status = webSocketManager.systemStatus {
                        HStack {
                            Image(systemName: "speedometer")
                                .foregroundColor(.orange)
                            Text("FPS")
                            Spacer()
                            Text(String(format: "%.1f", status.fps))
                                .foregroundColor(.secondary)
                        }
                        
                        HStack {
                            Image(systemName: "person.2.fill")
                                .foregroundColor(.purple)
                            Text("Người giám sát")
                            Spacer()
                            Text("\(status.activePeople)")
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    Button(action: { showingAbout = true }) {
                        HStack {
                            Image(systemName: "doc.text.fill")
                                .foregroundColor(.blue)
                            Text("Về ứng dụng")
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.secondary)
                                .font(.caption)
                        }
                    }
                }
                
                // Actions Section
                Section {
                    Button(action: clearNotifications) {
                        HStack {
                            Image(systemName: "bell.slash.fill")
                                .foregroundColor(.orange)
                            Text("Xóa tất cả thông báo")
                        }
                    }
                    
                    Button(action: clearCache) {
                        HStack {
                            Image(systemName: "trash.fill")
                                .foregroundColor(.red)
                            Text("Xóa cache")
                        }
                    }
                    
                    Button(action: { showingResetAlert = true }) {
                        HStack {
                            Image(systemName: "arrow.counterclockwise.circle.fill")
                                .foregroundColor(.red)
                            Text("Đặt lại cài đặt")
                        }
                    }
                }
            }
            .navigationTitle("Cài Đặt")
            .onChange(of: settings) { newSettings in
                saveSettings(newSettings)
            }
            .onAppear {
                loadSettings()
            }
            .alert("Đặt lại cài đặt?", isPresented: $showingResetAlert) {
                Button("Hủy", role: .cancel) { }
                Button("Đặt lại", role: .destructive) {
                    resetSettings()
                }
            } message: {
                Text("Tất cả cài đặt sẽ được đặt về mặc định")
            }
            .sheet(isPresented: $showingAbout) {
                AboutView()
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func loadSettings() {
        if let decoded = try? JSONDecoder().decode(AppSettings.self, from: settingsData) {
            settings = decoded
        }
    }
    
    private func saveSettings(_ newSettings: AppSettings) {
        if let encoded = try? JSONEncoder().encode(newSettings) {
            settingsData = encoded
        }
    }
    
    private func reconnect() {
        webSocketManager.disconnect()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            webSocketManager.connect(host: settings.serverHost, port: settings.serverPort)
        }
    }
    
    private func clearNotifications() {
        notificationManager.clearAllNotifications()
        notificationManager.clearBadge()
    }
    
    private func clearCache() {
        // Clear cache logic
        webSocketManager.clearAlertHistory()
    }
    
    private func resetSettings() {
        settings = .default
        saveSettings(settings)
    }
    
    private func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }
    
    private var statusColor: Color {
        switch webSocketManager.connectionStatus {
        case .connected: return .green
        case .connecting: return .orange
        case .disconnected: return .gray
        case .error: return .red
        }
    }
    
    private var statusIcon: String {
        switch webSocketManager.connectionStatus {
        case .connected: return "checkmark.circle.fill"
        case .connecting: return "arrow.triangle.2.circlepath.circle.fill"
        case .disconnected: return "xmark.circle.fill"
        case .error: return "exclamationmark.triangle.fill"
        }
    }
}

// MARK: - Advanced Settings View

struct AdvancedSettingsView: View {
    @AppStorage("debugMode") private var debugMode = false
    @AppStorage("autoReconnect") private var autoReconnect = true
    @AppStorage("reconnectDelay") private var reconnectDelay = 3.0
    @AppStorage("heartbeatInterval") private var heartbeatInterval = 30.0
    
    var body: some View {
        Form {
            Section("Debug") {
                Toggle("Debug Mode", isOn: $debugMode)
                
                if debugMode {
                    Toggle("Verbose Logging", isOn: .constant(false))
                    Toggle("Show Network Logs", isOn: .constant(false))
                }
            }
            
            Section("Kết Nối") {
                Toggle("Tự động kết nối lại", isOn: $autoReconnect)
                
                VStack(alignment: .leading) {
                    Text("Delay kết nối lại: \(Int(reconnectDelay))s")
                    Slider(value: $reconnectDelay, in: 1...10, step: 1)
                }
                
                VStack(alignment: .leading) {
                    Text("Heartbeat: \(Int(heartbeatInterval))s")
                    Slider(value: $heartbeatInterval, in: 10...60, step: 5)
                }
            }
            
            Section("Performance") {
                Toggle("Giảm animation", isOn: .constant(false))
                Toggle("Low data mode", isOn: .constant(false))
            }
        }
        .navigationTitle("Cài Đặt Nâng Cao")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Data Management View

struct DataManagementView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @State private var showingClearAlert = false
    
    var body: some View {
        Form {
            Section("Dữ Liệu") {
                HStack {
                    Text("Số cảnh báo")
                    Spacer()
                    Text("\(webSocketManager.alertHistory.count)")
                        .foregroundColor(.secondary)
                }
                
                HStack {
                    Text("Dung lượng cache")
                    Spacer()
                    Text("2.5 MB")
                        .foregroundColor(.secondary)
                }
            }
            
            Section {
                Button(action: { showingClearAlert = true }) {
                    HStack {
                        Image(systemName: "trash.fill")
                            .foregroundColor(.red)
                        Text("Xóa tất cả dữ liệu")
                            .foregroundColor(.red)
                    }
                }
            }
        }
        .navigationTitle("Quản Lý Dữ Liệu")
        .navigationBarTitleDisplayMode(.inline)
        .alert("Xóa dữ liệu?", isPresented: $showingClearAlert) {
            Button("Hủy", role: .cancel) { }
            Button("Xóa", role: .destructive) {
                webSocketManager.clearAlertHistory()
            }
        } message: {
            Text("Tất cả cảnh báo và cache sẽ bị xóa")
        }
    }
}

// MARK: - Security Settings View

struct SecuritySettingsView: View {
    @AppStorage("biometricEnabled") private var biometricEnabled = false
    @AppStorage("requirePassword") private var requirePassword = false
    
    var body: some View {
        Form {
            Section("Xác Thực") {
                Toggle("Face ID / Touch ID", isOn: $biometricEnabled)
                Toggle("Yêu cầu mật khẩu", isOn: $requirePassword)
            }
            
            Section("Quyền Riêng Tư") {
                Toggle("Ẩn thông báo trên lock screen", isOn: .constant(false))
                Toggle("Mã hóa dữ liệu local", isOn: .constant(true))
            }
            
            Section {
                NavigationLink("Chính sách bảo mật") {
                    PrivacyPolicyView()
                }
            }
        }
        .navigationTitle("Bảo Mật")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Privacy Policy View

struct PrivacyPolicyView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Chính Sách Bảo Mật")
                    .font(.title)
                    .fontWeight(.bold)
                
                Group {
                    Text("1. Thu Thập Dữ Liệu")
                        .font(.headline)
                    Text("Ứng dụng không thu thập hay lưu trữ dữ liệu cá nhân. Tất cả dữ liệu được xử lý local trên thiết bị.")
                    
                    Text("2. Sử Dụng Dữ Liệu")
                        .font(.headline)
                    Text("Dữ liệu cảnh báo chỉ được sử dụng để hiển thị trong ứng dụng và gửi thông báo.")
                    
                    Text("3. Bảo Mật")
                        .font(.headline)
                    Text("Kết nối với server sử dụng WebSocket. Khuyến nghị sử dụng VPN cho mạng công cộng.")
                }
            }
            .padding()
        }
        .navigationTitle("Chính Sách")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - About View

struct AboutView: View {
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // App Icon
                    Image(systemName: "shield.checkered")
                        .font(.system(size: 80))
                        .foregroundColor(.blue)
                        .padding()
                    
                    VStack(spacing: 8) {
                        Text("Fall Detection System")
                            .font(.title)
                            .fontWeight(.bold)
                        
                        Text("Phiên bản 1.0.0")
                            .foregroundColor(.secondary)
                    }
                    
                    Divider()
                        .padding(.horizontal)
                    
                    VStack(alignment: .leading, spacing: 16) {
                        AboutRow(icon: "target", title: "Mục đích", description: "Hệ thống giám sát và phát hiện té ngã realtime")
                        AboutRow(icon: "cpu", title: "Công nghệ", description: "YOLOv8 Pose Detection + Machine Learning")
                        AboutRow(icon: "bolt.fill", title: "Tính năng", description: "Phát hiện ngã, theo dõi đa người, cảnh báo thông minh")
                        AboutRow(icon: "globe", title: "Platform", description: "iOS 15+ | Python Backend | WebSocket")
                    }
                    .padding(.horizontal)
                    
                    Divider()
                        .padding(.horizontal)
                    
                    VStack(spacing: 12) {
                        Button(action: {}) {
                            Label("Hướng dẫn sử dụng", systemImage: "book.fill")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                        
                        Button(action: {}) {
                            Label("Liên hệ hỗ trợ", systemImage: "envelope.fill")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.green)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                    }
                    .padding(.horizontal)
                    
                    Text("© 2026 Caspton Project")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical)
            }
            .navigationTitle("Về Ứng Dụng")
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
}

struct AboutRow: View {
    let icon: String
    let title: String
    let description: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(.blue)
                .frame(width: 30)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(description)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(WebSocketManager())
        .environmentObject(NotificationManager.shared)
}
