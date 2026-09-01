package com.conrad.focusbridge;

import android.accessibilityservice.AccessibilityServiceInfo;
import android.app.KeyguardManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.drawable.Icon;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.view.accessibility.AccessibilityManager;

import org.json.JSONObject;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.UUID;

/** Always-on owner of polling, heartbeat, and the pre-execution offer lifecycle. */
public final class BridgeForegroundService extends Service {
    private static final String FOREGROUND_CHANNEL = "focus_bridge_foreground";
    private static final String DECISION_CHANNEL = "focus_bridge";
    private static final int FOREGROUND_NOTIFICATION_ID = 1001;
    private static final long POLL_MS = 15_000L;
    private static final long OFFER_TICK_MS = 1_000L;
    private static final long HEARTBEAT_MS = 5 * 60_000L;
    private static final long HEARTBEAT_RETRY_MS = 60_000L;
    private static final long DECISION_RETRY_MS = 15_000L;
    private static final long RESULT_RETRY_MS = 15_000L;
    private static final long PROMPT_LAUNCH_RETRY_MS = 5_000L;
    private static final String ACTION_SUBMIT_DECISION = "com.conrad.focusbridge.SUBMIT_DECISION";
    private static final String EXTRA_REQUEST_ID = "request_id";
    private static final String EXTRA_DECISION = "decision";
    private static final String EXTRA_REASON = "reason";
    private static final String INSTANCE_PREF = "foreground_instance_id";
    private static final String RESTART_PREF = "foreground_restart_count";
    private static final String CONNECT_PREF = "foreground_connection_count";
    private static final String OFFER_ID_PREF = "offer_request_id";
    private static final String OFFER_MESSAGE_PREF = "offer_message";
    private static final String OFFER_FIRST_SEEN_PREF = "offer_first_seen_at";
    private static final String OFFER_PROMPT_VISIBLE_PREF = "offer_prompt_visible";
    private static final String OFFER_PROMPT_DEADLINE_PREF = "offer_prompt_deadline_at";
    private static final String OFFER_DECISION_PREF = "offer_pending_decision";
    private static final String OFFER_REASON_PREF = "offer_pending_reason";
    private static final String RESULT_REQUEST_ID_PREF = "result_request_id";
    private static final String RESULT_DECISION_PREF = "result_decision";
    private static final String RESULT_STATUS_PREF = "result_status";
    private static final String RESULT_DETAIL_PREF = "result_detail";
    private static final String LOCK_STATUS_PREF = "lock_status";
    private static final String LOCK_REQUEST_ID_PREF = "lock_request_id";
    private static final String LOCK_MINUTES_PREF = "lock_minutes";
    private static final String LOCK_ATTEMPTS_PREF = "lock_attempts";
    private static final String LOCK_DETAIL_PREF = "lock_detail";
    private static final String LOCK_UPDATED_AT_PREF = "lock_updated_at";
    private static final String LAST_EXECUTION_ERROR_PREF = "last_execution_error";
    private static final DateTimeFormatter ISO_INSTANT = DateTimeFormatter.ISO_INSTANT;

    private static volatile BridgeForegroundService instance;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable pollTask = new Runnable() {
        @Override public void run() {
            pollOnce();
            handler.postDelayed(this, POLL_MS);
        }
    };
    private final Runnable heartbeatTask = new Runnable() {
        @Override public void run() {
            sendHeartbeat();
            handler.postDelayed(this, lastHeartbeatOk ? HEARTBEAT_MS : HEARTBEAT_RETRY_MS);
        }
    };
    private final Runnable offerTickTask = new Runnable() {
        @Override public void run() {
            advanceOffer();
            submitPendingExecutionResultIfDue();
            handler.postDelayed(this, OFFER_TICK_MS);
        }
    };

    private long startedAtMillis;
    private volatile long lastPollAtMillis;
    private volatile String lastPollStatus = "stopped";
    private volatile String lastError = "";
    private volatile boolean lastHeartbeatOk;
    private final AtomicBoolean heartbeatInFlight = new AtomicBoolean(false);
    private volatile boolean heartbeatKickPending;
    private String offerRequestId = "";
    private String offerMessage = "";
    private long offerFirstSeenAt;
    private boolean promptVisible;
    private long promptDeadlineAt;
    private String pendingDecision = "";
    private String pendingDecisionReason = "";
    private boolean decisionInFlight;
    private long nextDecisionRetryAt;
    private long nextPromptLaunchAt;
    private String resultRequestId = "";
    private String resultDecision = "";
    private String resultStatus = "";
    private String resultDetail = "";
    private boolean resultInFlight;
    private long nextResultRetryAt;
    private volatile long executionGeneration;

    static boolean isRunning() {
        return instance != null;
    }

    /** Starts (or re-delivers to) the foreground service; safe to call repeatedly. */
    static void start(Context context) {
        startIntent(context, new Intent(context, BridgeForegroundService.class));
    }

    private static void startIntent(Context context, Intent intent) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent);
        } else {
            context.startService(intent);
        }
    }

    static void receiveOffer(Context context, JSONObject request) {
        BridgeForegroundService service = instance;
        if (service != null) {
            service.handler.post(() -> service.handleOffer(request));
        } else {
            start(context);
        }
    }

    static void submitDecision(Context context, String requestId, String decision, String reason) {
        BridgeForegroundService service = instance;
        if (service != null) {
            service.handler.post(() -> service.queueDecision(requestId, decision, reason));
            return;
        }
        Intent intent = new Intent(context, BridgeForegroundService.class)
                .setAction(ACTION_SUBMIT_DECISION)
                .putExtra(EXTRA_REQUEST_ID, requestId)
                .putExtra(EXTRA_DECISION, decision)
                .putExtra(EXTRA_REASON, reason);
        startIntent(context, intent);
    }

    static void reportExecutionState(Context context, String status, String requestId,
                                     int minutes, int attempts, String detail) {
        SharedPreferences prefs = context.getSharedPreferences("focus_bridge", MODE_PRIVATE);
        SharedPreferences.Editor editor = prefs.edit()
                .putString(LOCK_STATUS_PREF, status == null ? "" : status)
                .putString(LOCK_REQUEST_ID_PREF, requestId == null ? "" : requestId)
                .putInt(LOCK_MINUTES_PREF, minutes)
                .putInt(LOCK_ATTEMPTS_PREF, attempts)
                .putString(LOCK_DETAIL_PREF, detail == null ? "" : detail)
                .putString(LOCK_UPDATED_AT_PREF, ISO_INSTANT.format(Instant.now()));
        if ("failed".equals(status)) {
            editor.putString(LAST_EXECUTION_ERROR_PREF, detail == null ? "unknown" : detail);
        } else if ("waiting_screen".equals(status) || "attempting".equals(status)
                || "confirmed".equals(status)) {
            editor.remove(LAST_EXECUTION_ERROR_PREF);
        }
        editor.apply();
        BridgeForegroundService service = instance;
        if (service != null) {
            service.handler.post(service::updateNotification);
            service.handler.post(service::sendHeartbeatNow);
        }
    }

    static void submitExecutionResult(Context context, String requestId, String decision,
                                      String status, String detail) {
        SharedPreferences current = context.getSharedPreferences("focus_bridge", MODE_PRIVATE);
        int attempts = current.getInt(LOCK_ATTEMPTS_PREF, 0);
        ExecutionRequestStore.markResultPending(context, requestId, attempts);
        context.getSharedPreferences("focus_bridge", MODE_PRIVATE).edit()
                .putString(RESULT_REQUEST_ID_PREF, requestId == null ? "" : requestId)
                .putString(RESULT_DECISION_PREF, decision == null ? "" : decision)
                .putString(RESULT_STATUS_PREF, status == null ? "" : status)
                .putString(RESULT_DETAIL_PREF, detail == null ? "" : detail)
                .apply();
        BridgeForegroundService service = instance;
        if (service == null) {
            start(context);
            return;
        }
        service.handler.post(() -> {
            service.executionGeneration++;
            service.restoreExecutionResult();
            service.nextResultRetryAt = 0L;
            service.submitPendingExecutionResultIfDue();
        });
    }

    static void notifyNotificationListenerChanged() {
        BridgeForegroundService service = instance;
        if (service == null) return;
        service.handler.post(service::updateNotification);
        service.handler.post(service::sendHeartbeatNow);
    }

    /** Called by the accessibility service whenever its connection state changes. */
    static void notifyAccessibilityConnected(boolean connected) {
        BridgeForegroundService service = instance;
        if (service == null) return;
        if (connected) {
            SharedPreferences prefs = service.prefs();
            prefs.edit().putInt(CONNECT_PREF, prefs.getInt(CONNECT_PREF, 0) + 1).apply();
        }
        service.updateNotification();
        service.handler.post(service::sendHeartbeatNow);
        service.handler.post(service::advanceOffer);
    }

    @Override public void onCreate() {
        super.onCreate();
        instance = this;
        startedAtMillis = System.currentTimeMillis();
        String id = UUID.randomUUID().toString();
        prefs().edit()
                .putString(INSTANCE_PREF, id)
                .putInt(RESTART_PREF, prefs().getInt(RESTART_PREF, 0) + 1)
                .apply();
        restoreOffer();
        restoreExecutionResult();
        createChannels();
        startForeground(FOREGROUND_NOTIFICATION_ID, buildNotification());
        BridgeLog.write(this, "前台服务已启动（实例 " + shortId(id) + "）");
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_SUBMIT_DECISION.equals(intent.getAction())) {
            String requestId = intent.getStringExtra(EXTRA_REQUEST_ID);
            String decision = intent.getStringExtra(EXTRA_DECISION);
            String reason = intent.getStringExtra(EXTRA_REASON);
            handler.post(() -> queueDecision(requestId, decision, reason));
        }
        handler.removeCallbacks(pollTask);
        handler.removeCallbacks(heartbeatTask);
        handler.removeCallbacks(offerTickTask);
        handler.postDelayed(pollTask, 500L);
        handler.postDelayed(heartbeatTask, 5_000L);
        handler.post(offerTickTask);
        return START_STICKY;
    }

    @Override public void onDestroy() {
        if (instance == this) instance = null;
        handler.removeCallbacksAndMessages(null);
        BridgeLog.write(this, "前台服务已停止");
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) {
        return null;
    }

    private void pollOnce() {
        lastPollAtMillis = System.currentTimeMillis();
        lastPollStatus = "polling";
        final long generation = executionGeneration;
        new Thread(() -> {
            try {
                JSONObject pending = BridgeApi.getPending(this).optJSONObject("request");
                lastError = "";
                handler.post(() -> {
                    if (generation != executionGeneration) {
                        lastPollStatus = "stale_poll_ignored";
                        BridgeLog.write(this, "已忽略执行状态变化前发出的旧轮询响应");
                        return;
                    }
                    handlePendingResponse(pending);
                });
            } catch (Exception error) {
                lastPollStatus = "error";
                lastError = error.getClass().getSimpleName();
                BridgeLog.write(this, "轮询失败：" + lastError);
            }
        }, "focus-bridge-poll").start();
    }

    private void handlePendingResponse(JSONObject pending) {
        // A locally chosen decision outranks later poll snapshots. In particular, a
        // temporary POST failure must not be erased by a null response or a newer offer.
        if (!pendingDecision.isEmpty()) {
            lastPollStatus = "offer_decision_pending";
            advanceOffer();
            return;
        }
        if (!resultRequestId.isEmpty()) {
            String pendingId = pending == null ? "" : pending.optString("request_id");
            if (pendingId.isEmpty() || resultRequestId.equals(pendingId)) {
                lastPollStatus = "execution_result_pending";
                submitPendingExecutionResultIfDue();
                return;
            }
        }
        if (pending == null) {
            lastPollStatus = "no_pending";
            if (!offerRequestId.isEmpty()) clearOffer("resolved_elsewhere_or_absent");
            return;
        }
        if ("offer".equals(pending.optString("mode"))) {
            handleOffer(pending);
            return;
        }
        String pendingId = pending.optString("request_id");
        if (ExecutionRequestStore.suppressPending(this, pendingId)) {
            lastPollStatus = "duplicate_execution_ignored";
            BridgeLog.write(this, "已拦截重复锁机请求：" + pendingId);
            submitPendingExecutionResultIfDue();
            return;
        }
        if (!offerRequestId.isEmpty()) clearOffer("execution_received");
        if (!FocusBridgeAccessibilityService.handlePendingRequest(pending)) {
            lastPollStatus = "accessibility_disconnected";
            BridgeLog.write(this, "收到 Pi 执行请求但无障碍服务未连接");
        } else {
            lastPollStatus = "pending_dispatched";
        }
    }

    private void handleOffer(JSONObject request) {
        String requestId = request.optString("request_id");
        if (requestId.isEmpty()) return;
        if (!pendingDecision.isEmpty() && !requestId.equals(offerRequestId)) {
            lastPollStatus = "offer_deferred_for_decision";
            BridgeLog.write(this, "旧介入决定尚未提交，暂缓新介入选择：" + requestId);
            advanceOffer();
            return;
        }
        if (!requestId.equals(offerRequestId)) {
            if (!offerRequestId.isEmpty()) clearOffer("replaced_by_new_offer");
            offerRequestId = requestId;
            offerMessage = request.optString("message", "是否让电脑和手机同步开始专注？");
            offerFirstSeenAt = System.currentTimeMillis();
            promptVisible = false;
            promptDeadlineAt = 0L;
            pendingDecision = "";
            pendingDecisionReason = "";
            nextPromptLaunchAt = 0L;
            persistOffer();
            BridgeLog.write(this, "收到介入选择：" + requestId);
        }
        advanceOffer();
    }

    private void advanceOffer() {
        if (offerRequestId.isEmpty()) return;
        long now = System.currentTimeMillis();
        boolean available = isAvailableForPrompt();
        OfferStateMachine.Next next = OfferStateMachine.next(
                now, offerFirstSeenAt, available, promptVisible, promptDeadlineAt,
                !pendingDecision.isEmpty());
        switch (next) {
            case WAIT_FOR_SUBMISSION:
                lastPollStatus = "offer_decision_pending";
                if (now >= nextDecisionRetryAt) submitPendingDecision();
                break;
            case WAIT_FOR_UNLOCK:
                lastPollStatus = "offer_waiting_unlock";
                showFallbackNotification();
                break;
            case SHOW_PROMPT:
                if (now < nextPromptLaunchAt) {
                    showFallbackNotification();
                    break;
                }
                promptVisible = true;
                promptDeadlineAt = now + OfferStateMachine.PROMPT_WINDOW_MS;
                persistOffer();
                if (FocusBridgeAccessibilityService.showInterventionPrompt(
                        offerRequestId, offerMessage, promptDeadlineAt)) {
                    lastPollStatus = "offer_prompt_visible";
                    cancelOfferNotification(offerRequestId);
                    BridgeLog.write(this, "介入选择页面已弹出，等待 10 秒决定");
                } else {
                    promptVisible = false;
                    promptDeadlineAt = 0L;
                    nextPromptLaunchAt = now + PROMPT_LAUNCH_RETRY_MS;
                    persistOffer();
                    lastPollStatus = "offer_waiting_accessibility";
                    showFallbackNotification();
                }
                break;
            case KEEP_PROMPT:
                lastPollStatus = "offer_prompt_visible";
                break;
            case DISMISS_FOR_LOCK:
                promptVisible = false;
                promptDeadlineAt = 0L;
                persistOffer();
                InterventionPromptActivity.dismiss(offerRequestId);
                lastPollStatus = "offer_relocked_waiting";
                showFallbackNotification();
                BridgeLog.write(this, "选择页面期间检测到锁屏，继续等待解锁");
                break;
            case IGNORE_LOCK_TIMEOUT:
                queueDecision(offerRequestId, "ignored", "locked_timeout_120s");
                break;
            case IGNORE_PROMPT_TIMEOUT:
                queueDecision(offerRequestId, "ignored", "prompt_timeout_10s");
                break;
        }
    }

    private void queueDecision(String requestId, String decision, String reason) {
        if (requestId == null || decision == null || requestId.isEmpty()) return;
        if (!decision.equals("accepted") && !decision.equals("declined") && !decision.equals("ignored")) return;
        if (!requestId.equals(offerRequestId)) {
            BridgeLog.write(this, "忽略过期页面决定：" + requestId);
            return;
        }
        if (!pendingDecision.isEmpty()) return;
        pendingDecision = decision;
        pendingDecisionReason = reason == null ? "" : reason;
        promptVisible = false;
        promptDeadlineAt = 0L;
        nextDecisionRetryAt = 0L;
        persistOffer();
        InterventionPromptActivity.dismiss(requestId);
        cancelOfferNotification(requestId);
        BridgeLog.write(this, "介入决定待提交：" + decision + " / " + pendingDecisionReason);
        submitPendingDecision();
    }

    private void submitPendingDecision() {
        if (decisionInFlight || offerRequestId.isEmpty() || pendingDecision.isEmpty()) return;
        decisionInFlight = true;
        final String requestId = offerRequestId;
        final String decision = pendingDecision;
        final String reason = pendingDecisionReason;
        new Thread(() -> {
            try {
                BridgeApi.decide(this, requestId, decision);
                handler.post(() -> {
                    decisionInFlight = false;
                    BridgeLog.write(this, "介入决定已提交：" + decision + " / " + reason);
                    clearOffer("decision_submitted");
                });
            } catch (Exception error) {
                handler.post(() -> {
                    decisionInFlight = false;
                    nextDecisionRetryAt = System.currentTimeMillis() + DECISION_RETRY_MS;
                    lastError = error.getClass().getSimpleName();
                    BridgeLog.write(this, "介入决定提交失败，15 秒后重试：" + lastError);
                });
            }
        }, "focus-bridge-decision").start();
    }

    private void restoreExecutionResult() {
        SharedPreferences prefs = prefs();
        resultRequestId = prefs.getString(RESULT_REQUEST_ID_PREF, "");
        resultDecision = prefs.getString(RESULT_DECISION_PREF, "");
        resultStatus = prefs.getString(RESULT_STATUS_PREF, "");
        resultDetail = prefs.getString(RESULT_DETAIL_PREF, "");
    }

    private void submitPendingExecutionResultIfDue() {
        if (resultInFlight || resultRequestId.isEmpty()
                || System.currentTimeMillis() < nextResultRetryAt) return;
        resultInFlight = true;
        final String requestId = resultRequestId;
        final String decision = resultDecision;
        final String status = resultStatus;
        final String detail = resultDetail;
        new Thread(() -> {
            try {
                BridgeApi.event(this, requestId, decision, status, detail);
                handler.post(() -> {
                    resultInFlight = false;
                    if (requestId.equals(resultRequestId)) {
                        ExecutionRequestStore.markCompleted(this, requestId);
                        executionGeneration++;
                        clearExecutionResult();
                    }
                    lastPollStatus = "execution_result_submitted";
                    BridgeLog.write(this, "锁机执行结果已上传：" + status + " / " + detail);
                    sendHeartbeatNow();
                });
            } catch (Exception error) {
                handler.post(() -> {
                    resultInFlight = false;
                    nextResultRetryAt = System.currentTimeMillis() + RESULT_RETRY_MS;
                    lastError = error.getClass().getSimpleName();
                    lastPollStatus = "execution_result_retry";
                    BridgeLog.write(this, "锁机执行结果上传失败，15 秒后重试：" + lastError);
                });
            }
        }, "focus-bridge-result").start();
    }

    private void clearExecutionResult() {
        resultRequestId = "";
        resultDecision = "";
        resultStatus = "";
        resultDetail = "";
        nextResultRetryAt = 0L;
        prefs().edit()
                .remove(RESULT_REQUEST_ID_PREF)
                .remove(RESULT_DECISION_PREF)
                .remove(RESULT_STATUS_PREF)
                .remove(RESULT_DETAIL_PREF)
                .apply();
    }

    private boolean isAvailableForPrompt() {
        PowerManager power = (PowerManager) getSystemService(Context.POWER_SERVICE);
        KeyguardManager keyguard = (KeyguardManager) getSystemService(Context.KEYGUARD_SERVICE);
        return power != null && power.isInteractive()
                && keyguard != null && !keyguard.isKeyguardLocked();
    }

    private void clearOffer(String reason) {
        String previous = offerRequestId;
        if (previous.isEmpty()) return;
        InterventionPromptActivity.dismiss(previous);
        cancelOfferNotification(previous);
        offerRequestId = "";
        offerMessage = "";
        offerFirstSeenAt = 0L;
        promptVisible = false;
        promptDeadlineAt = 0L;
        pendingDecision = "";
        pendingDecisionReason = "";
        decisionInFlight = false;
        nextDecisionRetryAt = 0L;
        nextPromptLaunchAt = 0L;
        clearPersistedOffer();
        BridgeLog.write(this, "介入选择已清理：" + reason);
    }

    private void restoreOffer() {
        SharedPreferences prefs = prefs();
        offerRequestId = prefs.getString(OFFER_ID_PREF, "");
        offerMessage = prefs.getString(OFFER_MESSAGE_PREF, "");
        offerFirstSeenAt = prefs.getLong(OFFER_FIRST_SEEN_PREF, 0L);
        promptVisible = prefs.getBoolean(OFFER_PROMPT_VISIBLE_PREF, false);
        promptDeadlineAt = prefs.getLong(OFFER_PROMPT_DEADLINE_PREF, 0L);
        pendingDecision = prefs.getString(OFFER_DECISION_PREF, "");
        pendingDecisionReason = prefs.getString(OFFER_REASON_PREF, "");
        if (!offerRequestId.isEmpty() && offerFirstSeenAt <= 0L) offerFirstSeenAt = System.currentTimeMillis();
    }

    private void persistOffer() {
        prefs().edit()
                .putString(OFFER_ID_PREF, offerRequestId)
                .putString(OFFER_MESSAGE_PREF, offerMessage)
                .putLong(OFFER_FIRST_SEEN_PREF, offerFirstSeenAt)
                .putBoolean(OFFER_PROMPT_VISIBLE_PREF, promptVisible)
                .putLong(OFFER_PROMPT_DEADLINE_PREF, promptDeadlineAt)
                .putString(OFFER_DECISION_PREF, pendingDecision)
                .putString(OFFER_REASON_PREF, pendingDecisionReason)
                .apply();
    }

    private void clearPersistedOffer() {
        prefs().edit()
                .remove(OFFER_ID_PREF)
                .remove(OFFER_MESSAGE_PREF)
                .remove(OFFER_FIRST_SEEN_PREF)
                .remove(OFFER_PROMPT_VISIBLE_PREF)
                .remove(OFFER_PROMPT_DEADLINE_PREF)
                .remove(OFFER_DECISION_PREF)
                .remove(OFFER_REASON_PREF)
                .apply();
    }

    private void showFallbackNotification() {
        if (offerRequestId.isEmpty() || !pendingDecision.isEmpty()) return;
        Intent accept = new Intent(this, DecisionReceiver.class).setAction(DecisionReceiver.ACTION_DECIDE)
                .putExtra(EXTRA_REQUEST_ID, offerRequestId).putExtra(EXTRA_DECISION, "accepted");
        Intent decline = new Intent(this, DecisionReceiver.class).setAction(DecisionReceiver.ACTION_DECIDE)
                .putExtra(EXTRA_REQUEST_ID, offerRequestId).putExtra(EXTRA_DECISION, "declined");
        int flags = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE;
        int base = offerRequestId.hashCode();
        Icon icon = Icon.createWithResource(this, android.R.drawable.ic_lock_lock);
        Notification notification = new Notification.Builder(this, DECISION_CHANNEL)
                .setSmallIcon(android.R.drawable.ic_lock_lock)
                .setContentTitle("当前需要介入")
                .setContentText("解锁后尝试弹出选择页；也可直接用通知按钮。")
                .setStyle(new Notification.BigTextStyle().bigText(offerMessage))
                .setOngoing(true)
                .addAction(new Notification.Action.Builder(icon, "接受",
                        PendingIntent.getBroadcast(this, base * 2, accept, flags)).build())
                .addAction(new Notification.Action.Builder(icon, "拒绝",
                        PendingIntent.getBroadcast(this, base * 2 + 1, decline, flags)).build())
                .build();
        getSystemService(NotificationManager.class).notify(base, notification);
    }

    private void cancelOfferNotification(String requestId) {
        if (requestId == null || requestId.isEmpty()) return;
        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager != null) manager.cancel(requestId.hashCode());
    }

    private void sendHeartbeatNow() {
        // Accessibility/notification callbacks may arrive in bursts.  Do not
        // start one network thread per callback; one queued heartbeat is enough.
        if (heartbeatInFlight.get()) {
            heartbeatKickPending = true;
            return;
        }
        handler.removeCallbacks(heartbeatTask);
        handler.postDelayed(heartbeatTask, 1_000L);
    }

    private void sendHeartbeat() {
        if (!heartbeatInFlight.compareAndSet(false, true)) return;
        final long uptimeSeconds = Math.max(0L, (System.currentTimeMillis() - startedAtMillis) / 1000L);
        final String pollAt = lastPollAtMillis == 0L ? "" : ISO_INSTANT.format(Instant.ofEpochMilli(lastPollAtMillis));
        final String pollStatus = lastPollStatus;
        final String error = lastError;
        new Thread(() -> {
            try {
                JSONObject metadata = new JSONObject();
                metadata.put("runtime_mode", "foreground_service");
                metadata.put("app_version", BridgeApi.APP_VERSION);
                metadata.put("service_instance_id", instanceId());
                metadata.put("process_started_at", ISO_INSTANT.format(Instant.ofEpochMilli(startedAtMillis)));
                metadata.put("service_started_at", ISO_INSTANT.format(Instant.ofEpochMilli(startedAtMillis)));
                metadata.put("last_poll_at", pollAt);
                metadata.put("last_poll_status", pollStatus);
                metadata.put("last_error", error);
                metadata.put("accessibility_enabled", isAccessibilityEnabled());
                metadata.put("accessibility_connected", FocusBridgeAccessibilityService.isConnected());
                SharedPreferences prefs = prefs();
                metadata.put("notification_access_enabled",
                        GetawayNotificationListenerService.isPermissionGranted(this));
                metadata.put("notification_listener_connected",
                        GetawayNotificationListenerService.isConnected());
                metadata.put("getaway_lock_active",
                        !GetawayNotificationListenerService.activePomodoroToken().isEmpty());
                metadata.put("lock_status", prefs.getString(LOCK_STATUS_PREF, "idle"));
                metadata.put("lock_request_id", prefs.getString(LOCK_REQUEST_ID_PREF, ""));
                metadata.put("duplicate_execution_requests_blocked",
                        ExecutionRequestStore.duplicateBlockedCount(this));
                metadata.put("lock_minutes", prefs.getInt(LOCK_MINUTES_PREF, 0));
                metadata.put("lock_attempts", prefs.getInt(LOCK_ATTEMPTS_PREF, 0));
                metadata.put("lock_detail", prefs.getString(LOCK_DETAIL_PREF, ""));
                metadata.put("lock_updated_at", prefs.getString(LOCK_UPDATED_AT_PREF, ""));
                metadata.put("last_execution_error",
                        prefs.getString(LAST_EXECUTION_ERROR_PREF, ""));
                metadata.put("service_uptime_seconds", uptimeSeconds);
                metadata.put("restart_count", restartCount());
                metadata.put("connection_count", connectionCount());
                metadata.put("transport", BridgeApi.lastTransport());
                metadata.put("fallback_active", BridgeApi.isFallbackActive());
                BridgeApi.heartbeat(this, "running", "foreground service running", metadata);
                lastHeartbeatOk = true;
                lastError = "";
                BridgeLog.write(this, "前台心跳已上报");
            } catch (Exception error2) {
                lastHeartbeatOk = false;
                lastError = error2.getClass().getSimpleName();
                BridgeLog.write(this, "前台心跳失败：" + lastError + "（公网 HTTPS 与备用地址均未完成）");
            } finally {
                heartbeatInFlight.set(false);
                if (heartbeatKickPending) {
                    heartbeatKickPending = false;
                    sendHeartbeatNow();
                }
            }
        }, "focus-bridge-heartbeat").start();
    }

    private boolean isAccessibilityEnabled() {
        try {
            AccessibilityManager manager = (AccessibilityManager) getSystemService(Context.ACCESSIBILITY_SERVICE);
            if (manager == null) return false;
            List<AccessibilityServiceInfo> enabled = manager.getEnabledAccessibilityServiceList(
                    AccessibilityServiceInfo.FEEDBACK_ALL_MASK);
            if (enabled == null) return false;
            for (AccessibilityServiceInfo info : enabled) {
                if (getPackageName().equals(info.getResolveInfo().serviceInfo.packageName)) return true;
            }
        } catch (Exception ignored) {
            // Never let a settings probe break the heartbeat.
        }
        return false;
    }

    private SharedPreferences prefs() {
        return getSharedPreferences("focus_bridge", MODE_PRIVATE);
    }

    private String instanceId() {
        return prefs().getString(INSTANCE_PREF, "");
    }

    private int restartCount() {
        return prefs().getInt(RESTART_PREF, 0);
    }

    private int connectionCount() {
        return prefs().getInt(CONNECT_PREF, 0);
    }

    private void createChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationChannel foreground = new NotificationChannel(
                FOREGROUND_CHANNEL, getString(R.string.foreground_channel), NotificationManager.IMPORTANCE_LOW);
        foreground.setDescription("保持 Focus Bridge 后台进程常驻");
        foreground.setShowBadge(false);
        NotificationChannel decision = new NotificationChannel(
                DECISION_CHANNEL, getString(R.string.notification_channel), NotificationManager.IMPORTANCE_HIGH);
        decision.setDescription("介入决定页面不可用时的操作兜底");
        NotificationManager manager = getSystemService(NotificationManager.class);
        manager.createNotificationChannel(foreground);
        manager.createNotificationChannel(decision);
    }

    private Notification buildNotification() {
        boolean accessibility = FocusBridgeAccessibilityService.isConnected();
        boolean listener = GetawayNotificationListenerService.isConnected();
        String text = accessibility && listener
                ? "无障碍与锁机确认已连接，心跳与轮询正常"
                : "守护中：等待" + (!accessibility ? "无障碍" : "通知确认") + "服务连接";
        return new Notification.Builder(this, FOREGROUND_CHANNEL)
                .setSmallIcon(android.R.drawable.ic_lock_lock)
                .setContentTitle("专注花园手机桥接运行中")
                .setContentText(text)
                .setOngoing(true)
                .build();
    }

    private void updateNotification() {
        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager != null) manager.notify(FOREGROUND_NOTIFICATION_ID, buildNotification());
    }

    private static String shortId(String id) {
        return id.length() <= 8 ? id : id.substring(0, 8);
    }
}
