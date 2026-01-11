//
//  ContentView.swift
//  FallDetectionApp
//
//  Main navigation view
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Dashboard
            DashboardView()
                .tabItem {
                    Label("Giám sát", systemImage: "chart.line.uptrend.xyaxis")
                }
                .tag(0)
            
            // Alert History
            AlertListView()
                .tabItem {
                    Label("Cảnh báo", systemImage: "bell.fill")
                }
                .tag(1)
            
            // Settings
            SettingsView()
                .tabItem {
                    Label("Cài đặt", systemImage: "gearshape.fill")
                }
                .tag(2)
        }
        .accentColor(.blue)
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager())
}
