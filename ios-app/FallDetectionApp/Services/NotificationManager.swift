//
//  NotificationManager.swift
//  FallDetectionApp
//
//  Manager để xử lý local notifications
//

import Foundation
import UserNotifications

/// Manager để xử lý push notifications
class NotificationManager: NSObject, ObservableObject {
    static let shared = NotificationManager()
    
    @Published var isAuthorized = false
    
    private override init() {
        super.init()
        checkAuthorization()
    }
    
    // MARK: - Authorization
    
    /// Kiểm tra quyền notification
    func checkAuthorization() {
        UNUserNotificationCenter.current().getNotificationSettings { settings in
            DispatchQueue.main.async {
                self.isAuthorized = settings.authorizationStatus == .authorized
            }
        }
    }
    
    /// Request quyền notification
    func requestAuthorization() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            DispatchQueue.main.async {
                self.isAuthorized = granted
            }
            
            if let error = error {
                print("[Notification] Authorization error: \(error)")
            }
        }
    }
    
    // MARK: - Send Notifications
    
    /// Gửi notification cho alert
    func sendAlertNotification(_ alert: FallAlert) {
        guard isAuthorized else { return }
        
        let content = UNMutableNotificationContent()
        content.title = "⚠️ \(alert.severity.displayName)"
        content.body = alert.message
        content.sound = .default
        content.badge = 1
        
        // Category dựa vào severity
        content.categoryIdentifier = alert.severity.rawValue
        
        // User info
        content.userInfo = [
            "alert_id": alert.id,
            "track_id": alert.trackId,
            "severity": alert.severity.rawValue,
            "risk_score": alert.riskScore
        ]
        
        // Trigger ngay lập tức
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        
        let request = UNNotificationRequest(
            identifier: alert.id,
            content: content,
            trigger: trigger
        )
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("[Notification] Send error: \(error)")
            }
        }
    }
    
    /// Clear tất cả notifications
    func clearAllNotifications() {
        UNUserNotificationCenter.current().removeAllDeliveredNotifications()
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
    }
    
    /// Clear badge
    func clearBadge() {
        UNUserNotificationCenter.current().setBadgeCount(0)
    }
}
