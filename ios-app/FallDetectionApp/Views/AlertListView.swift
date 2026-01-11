//
//  AlertListView.swift
//  FallDetectionApp
//
//  Danh sách tất cả cảnh báo
//

import SwiftUI

struct AlertListView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @State private var selectedSeverityFilter: AlertSeverity?
    @State private var showingFilterSheet = false
    
    var filteredAlerts: [FallAlert] {
        if let filter = selectedSeverityFilter {
            return webSocketManager.alertHistory.filter { $0.severity == filter }
        }
        return webSocketManager.alertHistory
    }
    
    var body: some View {
        NavigationView {
            Group {
                if filteredAlerts.isEmpty {
                    EmptyAlertView()
                } else {
                    List {
                        ForEach(filteredAlerts) { alert in
                            AlertRowView(alert: alert)
                        }
                    }
                    .listStyle(.insetGrouped)
                }
            }
            .navigationTitle("Lịch Sử Cảnh Báo")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: { showingFilterSheet = true }) {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { webSocketManager.clearAlertHistory() }) {
                        Image(systemName: "trash")
                    }
                    .disabled(webSocketManager.alertHistory.isEmpty)
                }
            }
            .sheet(isPresented: $showingFilterSheet) {
                FilterSheet(selectedFilter: $selectedSeverityFilter)
            }
        }
    }
}

// MARK: - Alert Row

struct AlertRowView: View {
    let alert: FallAlert
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: severityIcon)
                    .foregroundColor(severityColor)
                
                Text(alert.severity.displayName)
                    .fontWeight(.semibold)
                    .foregroundColor(severityColor)
                
                Spacer()
                
                Text(alert.timestamp, style: .time)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Text(alert.message)
                .font(.body)
            
            HStack {
                Label("Risk: \(alert.riskScore)", systemImage: "chart.bar.fill")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                if let location = alert.location {
                    Spacer()
                    Label(location, systemImage: "location.fill")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            if let metadata = alert.metadata {
                MetadataView(metadata: metadata)
            }
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
    
    var severityIcon: String {
        switch alert.severity {
        case .warning: return "exclamationmark.triangle.fill"
        case .alarm: return "bell.fill"
        case .emergency: return "exclamationmark.octagon.fill"
        }
    }
}

// MARK: - Metadata View

struct MetadataView: View {
    let metadata: AlertMetadata
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            if let fallDuration = metadata.fallDuration {
                HStack {
                    Image(systemName: "timer")
                        .font(.caption2)
                    Text("Thời gian ngã: \(String(format: "%.1fs", fallDuration))")
                        .font(.caption2)
                }
                .foregroundColor(.secondary)
            }
            
            if let immobilityDuration = metadata.immobilityDuration {
                HStack {
                    Image(systemName: "figure.stand")
                        .font(.caption2)
                    Text("Bất động: \(String(format: "%.1fs", immobilityDuration))")
                        .font(.caption2)
                }
                .foregroundColor(.secondary)
            }
            
            if let position = metadata.positionInfo {
                HStack {
                    Image(systemName: "person.fill")
                        .font(.caption2)
                    Text(position)
                        .font(.caption2)
                }
                .foregroundColor(.secondary)
            }
        }
        .padding(.top, 4)
    }
}

// MARK: - Empty View

struct EmptyAlertView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "bell.slash.fill")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            
            Text("Không có cảnh báo")
                .font(.title3)
                .fontWeight(.semibold)
            
            Text("Tất cả cảnh báo sẽ xuất hiện ở đây")
                .font(.body)
                .foregroundColor(.secondary)
        }
    }
}

// MARK: - Filter Sheet

struct FilterSheet: View {
    @Environment(\.dismiss) var dismiss
    @Binding var selectedFilter: AlertSeverity?
    
    var body: some View {
        NavigationView {
            List {
                Section("Lọc theo mức độ") {
                    Button(action: {
                        selectedFilter = nil
                        dismiss()
                    }) {
                        HStack {
                            Text("Tất cả")
                            Spacer()
                            if selectedFilter == nil {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.blue)
                            }
                        }
                    }
                    
                    ForEach(AlertSeverity.allCases, id: \.self) { severity in
                        Button(action: {
                            selectedFilter = severity
                            dismiss()
                        }) {
                            HStack {
                                Text(severity.displayName)
                                Spacer()
                                if selectedFilter == severity {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.blue)
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Bộ lọc")
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

#Preview {
    AlertListView()
        .environmentObject(WebSocketManager())
}
