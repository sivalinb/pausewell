import Foundation
import HealthKit
import CoreMotion
import UserNotifications

@MainActor
final class HealthBridge: ObservableObject {
    @Published var status = "Connect Apple Health to begin."
    @Published var checkinID: String?
    @Published var offered = ""
    @Published var resources: [[String: String]] = []
    @Published var enabled = UserDefaults.standard.bool(forKey: "monitor-enabled")
    private let health = HKHealthStore()
    private let motion = CMMotionActivityManager()
    private var observer: HKObserverQuery?
    private var syncing = false
    private var monitorGeneration = 0
    private var exerciseConfirmedUntil = Date.distantPast
    private let hr = HKQuantityType(.heartRate)
    private let hrv = HKQuantityType(.heartRateVariabilitySDNN)
    private let steps = HKQuantityType(.stepCount)
    private let sleep = HKCategoryType(.sleepAnalysis)
    private let workouts = HKObjectType.workoutType()
    private let iso = ISO8601DateFormatter()

    func confirmNoExercise() {
        exerciseConfirmedUntil = Date().addingTimeInterval(15 * 60)
        status = "No exercise confirmed for 15 minutes. Motion and workout history are still checked."
    }
    func connect() async {
        guard HKHealthStore.isHealthDataAvailable() else { status = "HealthKit unavailable on this device."; return }
        let generation = monitorGeneration
        do {
            try await health.requestAuthorization(toShare: [], read: [hr, hrv, steps, sleep, workouts])
            _ = try await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])
            guard generation == monitorGeneration else { return }
            enabled = true
            UserDefaults.standard.set(true, forKey: "monitor-enabled")
            startObserver()
            await sync()
        } catch {
            if generation == monitorGeneration { status = "Could not request access. Review Apple Health permissions." }
        }
    }
    func restore() { if enabled { startObserver() } }
    func pause() {
        monitorGeneration += 1
        enabled = false
        UserDefaults.standard.set(false, forKey: "monitor-enabled")
        if let observer { health.stop(observer) }
        observer = nil
        health.disableAllBackgroundDelivery { _, _ in }
        exerciseConfirmedUntil = .distantPast
        checkinID = nil
        offered = ""
        resources = []
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
        UNUserNotificationCenter.current().removeAllDeliveredNotifications()
        status = "Monitoring paused."
    }
    private func startObserver() {
        guard observer == nil else { return }
        let query = HKObserverQuery(sampleType: hr, predicate: nil) { [weak self] _, completion, error in
            Task { @MainActor in
                defer { completion() }
                guard error == nil else { return }
                await self?.sync()
            }
        }
        observer = query
        health.execute(query)
        health.enableBackgroundDelivery(for: hr, frequency: .immediate) { _, _ in }
    }
    private func samples(_ type: HKSampleType, since: Date) async throws -> [HKSample] {
        try await withCheckedThrowingContinuation { continuation in
            let query = HKSampleQuery(sampleType: type, predicate: HKQuery.predicateForSamples(withStart: since, end: Date(), options: []), limit: HKObjectQueryNoLimit, sortDescriptors: [NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: true)]) { _, values, error in
                if let error { continuation.resume(throwing: error) }
                else { continuation.resume(returning: values ?? []) }
            }
            health.execute(query)
        }
    }
    private func activity(since: Date) async -> String {
        guard CMMotionActivityManager.isActivityAvailable() else { return "unknown" }
        return await withCheckedContinuation { continuation in
            motion.queryActivityStarting(from: since, to: Date(), to: .main) { values, error in
                guard error == nil, let values, let latest = values.last, latest.confidence != .low,
                      Date().timeIntervalSince(latest.startDate) < 15 * 60 else { continuation.resume(returning: "unknown"); return }
                let moving = values.contains { $0.walking || $0.running || $0.cycling || $0.automotive }
                continuation.resume(returning: moving ? "moving" : latest.stationary ? "stationary" : "unknown")
            }
        }
    }
    private func median(_ values: [Double]) -> Double {
        let v = values.sorted(); guard !v.isEmpty else { return 0 }
        return v.count % 2 == 0 ? (v[v.count / 2 - 1] + v[v.count / 2]) / 2 : v[v.count / 2]
    }
    func request(_ path: String, method: String = "POST", body: [String: Any]? = nil) async throws -> [String: Any] {
        guard let base = URL(string: UserDefaults.standard.string(forKey: "server") ?? ""), base.scheme == "https", base.host != nil, base.user == nil, base.password == nil,
              let url = URL(string: path, relativeTo: base) else { throw URLError(.badURL) }
        var req = URLRequest(url: url); req.httpMethod = method; req.timeoutInterval = 20
        req.setValue("Bearer " + Keychain.read(), forHTTPHeaderField: "Authorization")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let body { req.httpBody = try JSONSerialization.data(withJSONObject: body) }
        let session = URLSession(configuration: .ephemeral, delegate: NoRedirect(), delegateQueue: nil)
        defer { session.finishTasksAndInvalidate() }
        let (data, response) = try await session.data(for: req)
        guard let response = response as? HTTPURLResponse, (200..<300).contains(response.statusCode) else { throw URLError(.badServerResponse) }
        return (try JSONSerialization.jsonObject(with: data)) as? [String: Any] ?? [:]
    }
    func sync() async {
        guard enabled, !syncing else { return }
        let generation = monitorGeneration
        syncing = true; defer { syncing = false }
        do {
            let now = Date(), start = Date().addingTimeInterval(-14 * 86400)
            let all = try await samples(hr, since: start).compactMap { $0 as? HKQuantitySample }.filter {
                $0.device?.manufacturer == "Apple Inc." && ($0.device?.model?.contains("Watch") ?? false) && ($0.metadata?[HKMetadataKeyWasUserEntered] as? Bool != true)
            }
            guard enabled, generation == monitorGeneration else { return }
            guard !all.isEmpty else { status = "No readable Watch heart-rate samples. HealthKit does not reveal whether read access was denied."; return }
            let workoutSamples = try await samples(workouts, since: start)
            let stepSamples = try await samples(steps, since: start).compactMap { $0 as? HKQuantitySample }
            let sleepSamples = try await samples(sleep, since: start).compactMap { $0 as? HKCategorySample }.filter { $0.value != HKCategoryValueSleepAnalysis.awake.rawValue }
            guard enabled, generation == monitorGeneration else { return }
            let unit = HKUnit.count().unitDivided(by: .minute())
            let baseline = all.filter { sample in
                sample.startDate < now.addingTimeInterval(-86400) &&
                !workoutSamples.contains { sample.startDate >= $0.startDate.addingTimeInterval(-900) && sample.startDate <= $0.endDate.addingTimeInterval(2700) } &&
                !stepSamples.contains { $0.quantity.doubleValue(for: .count()) > 0 && sample.startDate >= $0.startDate.addingTimeInterval(-300) && sample.startDate <= $0.endDate.addingTimeInterval(300) } &&
                !sleepSamples.contains { sample.startDate >= $0.startDate && sample.startDate <= $0.endDate }
            }
            let values = baseline.map { $0.quantity.doubleValue(for: unit) }
            guard values.count >= 20 else { status = "Calibrating: need at least 20 eligible daytime samples over 7 days."; return }
            let center = median(values), mad = median(values.map { abs($0-center) })
            let days = Set(baseline.map { Calendar.current.startOfDay(for: $0.startDate) }).count
            let recent = Array(all.filter { $0.startDate > now.addingTimeInterval(-900) }.suffix(60))
            guard let latest = recent.last, let oldestBaseline = baseline.last else { status = "Waiting for fresh Watch readings."; return }
            let moving = await activity(since: now.addingTimeInterval(-900))
            guard enabled, generation == monitorGeneration else { return }
            let stepMoving = stepSamples.contains { $0.endDate > now.addingTimeInterval(-900) && $0.quantity.doubleValue(for: .count()) > 0 }
            let recentWorkout = workoutSamples.last
            // HealthKit workout records cannot prove another app has no active workout.
            let workoutState = exerciseConfirmedUntil > now ? "inactive" : "unknown"
            var payload: [String: Any] = ["event_id": latest.uuid.uuidString, "source": "healthkit", "readings": recent.map { ["time": iso.string(from: $0.startDate), "bpm": $0.quantity.doubleValue(for: unit)] }, "baseline_bpm": center, "baseline_mad": mad, "baseline_days": days, "baseline_samples": values.count, "baseline_updated": iso.string(from: oldestBaseline.endDate), "workout": workoutState, "activity": stepMoving ? "moving" : moving,
                "asleep": sleepSamples.contains { $0.endDate > now.addingTimeInterval(-900) }]
            if let recentWorkout { payload["workout_ended"] = iso.string(from: recentWorkout.endDate) }
            guard enabled, generation == monitorGeneration else { return }
            let result = try await request("/api/windows", body: payload)
            guard enabled, generation == monitorGeneration else { return }
            status = (result["reason"] as? String ?? "Synced").replacingOccurrences(of: "_", with: " ")
            if let id = result["checkin_id"] as? String {
                checkinID = id
                if result["duplicate"] as? Bool != true {
                    let content = UNMutableNotificationContent(); content.title = "A small pause?"; content.body = "Open Pausewell for an optional check-in."; content.sound = .default
                    content.userInfo = ["checkin_id": id]
                    guard enabled, generation == monitorGeneration else { return }
                    try await UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: id, content: content, trigger: nil))
                    // Pause can run while notification registration is suspended.
                    if !enabled || generation != monitorGeneration {
                        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: [id])
                        UNUserNotificationCenter.current().removeDeliveredNotifications(withIdentifiers: [id])
                    }
                }
            }
        } catch {
            if enabled && generation == monitorGeneration {
                status = "Sync unavailable. Check permissions, server address and network. No new prompt sent."
            }
        }
    }
    func loadPending() async {
        guard enabled else { return }
        let generation = monitorGeneration
        do {
            let history = try await request("/api/history", method: "GET")
            guard enabled, generation == monitorGeneration else { return }
            let rows = history["checkins"] as? [[String: Any]] ?? []
            checkinID = rows.first(where: { $0["source"] as? String == "healthkit" && $0["status"] as? String == "pending" })?["id"] as? String
        } catch { }
    }
    func reply(feeling: String, context: String, choice: String, symptoms: String) async {
        guard let id = checkinID else { return }
        let generation = monitorGeneration
        do {
            let result = try await request("/api/checkins/\(id)/reply", body: ["feeling": feeling, "context": context, "choice": choice, "symptoms": symptoms])
            guard enabled, generation == monitorGeneration else { return }
            let cards = result["cards"] as? [[String: Any]] ?? []
            offered = ([result["message"] as? String ?? ""] + cards.compactMap { $0["text"] as? String }).joined(separator: "\n\n")
            resources = (result["resources"] as? [[String: Any]] ?? []).map { ["title": $0["title"] as? String ?? "Resource", "url": $0["url"] as? String ?? ""] }
        } catch {
            if enabled && generation == monitorGeneration { status = "Reply could not be saved. Try again." }
        }
    }
}

final class NoRedirect: NSObject, URLSessionTaskDelegate {
    func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse, newRequest request: URLRequest, completionHandler: @escaping (URLRequest?) -> Void) {
        completionHandler(nil)
    }
}
