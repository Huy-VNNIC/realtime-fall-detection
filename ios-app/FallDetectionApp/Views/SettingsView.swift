//
//  SettingsView.swift
//  FallDetectionApp
//
//  Màn hình cài đặt
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var notificationManager: NotificationManager
    
    @AppStorage("settings") private var settingsData: Data = try! JSONEncoder().encode(AppSettings.default)
    
    @State private var settings: AppSettings = .default
    @State private var showingResetAlert = false
    
    var body: some View {
        NavigationView {
            Form {
                // Server Section
                Section("Kết Nối Server") {
                    HStack {
                        Text("Host")
                        Spacer()
                        TextField("192.168.1.100", text: $settings.serverHost)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.URL)
                    }
                    
                    HStack {
                        Text("Port")
                        Spacer()
                        TextField("8080", value: $settings.serverPort, format: .number)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.numberPad)
                    }
                    
                    Toggle("Tự động kết nối", isOn: $settings.autoConnect)
                    
                    Button(action: reconnect) {
                        HStack {
                            Image(systemName: "arrow.clockwise")
                            Text("Kết nối lại")
                        }
                    }
                }
                
                // Notification Section
                Section("Thông Báo") {
                    Toggle("Bật thông báo", isOn: $settings.enableNotifications)
                        .onChange(of: settings.enableNotifications) { newValue in
                            if newValue && !notificationManager.isAuthorized {
                                notificationManager.requestAuthorization()
                            }
                        }
                    
                    Toggle("Âm thanh", isOn: $settings.notificationSound)
                        .disabled(!settings.enableNotifications)
                    
                    Picker("Mức độ tối thiểu", selection: $settings.minimumSeverity) {
                        ForEach(AlertSeverity.allCases, id: \.self) { severity in
                            Text(severity.displayName).tag(severity)
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
                
                // Info Section
                Section("Thông Tin") {
                    HStack {
                        Text("Phiên bản")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }
                    
                    HStack {
                        Text("Trạng thái")
                        Spacer()
                        Text(webSocketManager.connectionStatus.displayName)
                            .foregroundColor(statusColor)
                    }
                    
                    if let status = webSocketManager.systemStatus {
                        HStack {
                            Text("FPS")
                            Spacer()
                            Text(String(format: "%.1f", status.fps))
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                // Actions Section
                Section {
                    Button(action: clearNotifications) {
                        HStack {
                            Image(systemName: "bell.slash")
                            Text("Xóa tất cả thông báo")
                        }
                    }
                    
                    Button(action: { showingResetAlert = true }) {
                        HStack {
                            Image(systemName: "arrow.counterclockwise")
                            Text("Đặt lại cài đặt")
                        }
                        .foregroundColor(.red)
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
}

#Preview {
    SettingsView()
        .environmentObject(WebSocketManager())
        .environmentObject(NotificationManager.shared)
}
