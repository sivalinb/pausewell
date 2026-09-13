import SwiftUI

@main
struct PausewellApp: App {
    @StateObject private var bridge = HealthBridge()
    @Environment(\.scenePhase) private var scenePhase
    var body: some Scene {
        WindowGroup { ContentView(bridge: bridge).task { bridge.restore(); await bridge.loadPending() }
            .onChange(of: scenePhase) { _, phase in if phase == .active { Task { await bridge.loadPending() } } }
        }
    }
}

struct ContentView: View {
    @ObservedObject var bridge: HealthBridge
    @AppStorage("server") var server = ""
    @State var token = ""
    @State var feeling = "unsure"
    @State var context = "private"
    @State var choice = "suggest"
    @State var symptoms = "none"
    var body: some View {
        NavigationStack {
            Form {
                Section("Your private connection") {
                    TextField("HTTPS server URL", text: $server).textInputAutocapitalization(.never).autocorrectionDisabled()
                    SecureField("Access token", text: $token)
                    Button("Save token in Keychain") { Keychain.save(token); token = "" }
                    Text("Your server receives a small recent window and a personal comparison summary. Cloud AI is off by default. No notes or raw biometrics go to AI providers.").font(.caption)
                }
                Section("Apple Health") {
                    Text(bridge.status)
                    Button("Connect read-only Apple Health") { Task { await bridge.connect() } }
                    Button("I'm not exercising · confirm for 15 minutes") { bridge.confirmNoExercise(); Task { await bridge.sync() } }
                    Button("Sync now") { Task { await bridge.sync() } }
                    Button("Pause monitoring") { bridge.pause() }
                    Text("Readings arrive intermittently. Other apps' live workouts cannot be ruled out by HealthKit history alone. Prompts stay off when exercise context is unknown. Notifications may mirror to your Watch based on system settings.").font(.caption)
                }
                if bridge.checkinID != nil {
                    Section("A small check-in?") {
                        Picker("Feeling", selection: $feeling) { ForEach(["unsure", "overwhelmed", "frustrated", "worried", "tired", "okay"], id: \.self) { Text($0).tag($0) } }
                        Picker("Context", selection: $context) { ForEach(["private", "work", "relationship", "caffeine", "exercise", "illness", "other"], id: \.self) { Text($0).tag($0) } }
                        Picker("Small action", selection: $choice) { ForEach(["suggest", "move", "hydrate", "name", "breathe", "skip", "snooze"], id: \.self) { Text($0).tag($0) } }
                        Picker("Immediate support", selection: $symptoms) { Text("No urgent symptoms reported").tag("none"); Text("Urgent medical symptoms").tag("urgent"); Text("Crisis / might hurt myself").tag("crisis") }
                        Button("Continue") { Task { await bridge.reply(feeling: feeling, context: context, choice: choice, symptoms: symptoms) } }
                    }
                }
                if !bridge.offered.isEmpty {
                    Section("A little space") {
                        Text(bridge.offered)
                        ForEach(bridge.resources, id: \.self) { resource in if let url = URL(string: resource["url"] ?? "") { Link(resource["title"] ?? "Resource", destination: url) } }
                        Button("This helped") { Task { if let id = bridge.checkinID { _ = try? await bridge.request("/api/checkins/\(id)/feedback", body: ["helpful": true, "completed": true]); bridge.checkinID = nil; bridge.offered = "" } } }
                    }
                }
                Section { Text("Watch readings cannot tell us whether you are stressed. Pausewell offers wellness reflection, not diagnosis or emergency monitoring.").font(.caption) }
            }.navigationTitle("Pausewell")
        }
    }
}
