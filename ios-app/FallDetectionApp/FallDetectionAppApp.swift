//
//  FallDetectionAppApp.swift
//  FallDetectionApp
//
//  Entry point cho ứng dụng
//

import SwiftUI

@main
struct FallDetectionAppApp: App {
    // StateObject để quản lý WebSocket và Settings
    @StateObject private var webSocketManager = WebSocketManager()
    @StateObject private var notificationManager = NotificationManager.shared
    
    // AppStorage cho settings
    @AppStorage("settings") private var settingsData: Data = try! JSONEncoder().encode(AppSettings.default)
    
    var settings: AppSettings {
        (try? JSONDecoder().decode(AppSettings.self, from: settingsData)) ?? .default
    }
    
    init() {
        // Setup notification delegate
        UNUserNotificationCenter.current().delegate = NotificationDelegate.shared
        
        // Request notification permission
        NotificationManager.shared.requestAuthorization()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(webSocketManager)
                .environmentObject(notificationManager)
                .onAppear {
                    // Auto-connect nếu enabled
                    if settings.autoConnect {
                        webSocketManager.connect(
                            host: settings.serverHost,
                            port: settings.serverPort
                        )
                    }
                }
        }
    }
}

// MARK: - Notification Delegate

class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    static let shared = NotificationDelegate()
    
    // Hiển thị notification khi app đang foreground
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound, .badge])
    }
    
    // Xử lý khi user tap vào notification
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        print("[Notification] Tapped: \(userInfo)")
        
        // TODO: Navigate to alert detail
        
        completionHandler()
    }
}
