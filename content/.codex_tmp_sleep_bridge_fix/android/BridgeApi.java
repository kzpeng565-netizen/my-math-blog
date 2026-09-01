package com.conrad.focusbridge;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Base64;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;

final class BridgeApi {
    static final String APP_VERSION = "1.3.4";
    static final String DEFAULT_BASE_URL = "https://pi.taild4d3f7.ts.net:8460";
    private static final String PUBLIC_BASE_URL = "https://pi.taild4d3f7.ts.net";
    private static final String TOKEN_FILE = "focus-bridge-token.txt";

    private static volatile String lastTransport = "unknown";
    private static volatile boolean fallbackActive;

    private BridgeApi() {}

    static String baseUrl(Context context) {
        SharedPreferences prefs = context.getSharedPreferences("focus_bridge", Context.MODE_PRIVATE);
        return prefs.getString("base_url", DEFAULT_BASE_URL).replaceAll("/+$", "");
    }

    static String lastTransport() { return lastTransport; }
    static boolean isFallbackActive() { return fallbackActive; }

    static int quickPresetMinutes(Context context) {
        return context.getSharedPreferences("focus_bridge", Context.MODE_PRIVATE)
                .getInt("quick_preset_minutes", 40);
    }

    static float confirmX(Context context) {
        return context.getSharedPreferences("focus_bridge", Context.MODE_PRIVATE)
                .getFloat("confirm_x", -1f);
    }

    static float confirmY(Context context) {
        return context.getSharedPreferences("focus_bridge", Context.MODE_PRIVATE)
                .getFloat("confirm_y", -1f);
    }

    static boolean hasConfirmCoordinate(Context context) {
        return confirmX(context) >= 0f && confirmY(context) >= 0f;
    }

    static float quickGridYOffset(Context context) {
        return context.getSharedPreferences("focus_bridge", Context.MODE_PRIVATE)
                .getFloat("quick_grid_y_offset", 0f);
    }

    static JSONObject getPending(Context context) throws Exception {
        return request(context, "GET", "/api/focus-bridge/pending", null);
    }

    static JSONObject decide(Context context, String requestId, String decision) throws Exception {
        JSONObject body = new JSONObject();
        body.put("request_id", requestId);
        body.put("decision", decision);
        return request(context, "POST", "/api/focus-bridge/decision", body);
    }

    static JSONObject event(Context context, String requestId, String decision, String status, String detail) throws Exception {
        JSONObject body = new JSONObject();
        body.put("request_id", requestId);
        body.put("decision", decision);
        body.put("status", status);
        body.put("final", true);
        body.put("detail", detail);
        return request(context, "POST", "/api/focus-bridge/event", body);
    }

    static JSONObject heartbeat(Context context, String status, String detail, JSONObject metadata) throws Exception {
        JSONObject body = new JSONObject();
        body.put("status", status);
        body.put("detail", detail);
        if (metadata != null) {
            java.util.Iterator<String> keys = metadata.keys();
            while (keys.hasNext()) {
                String key = keys.next();
                body.put(key, metadata.get(key));
            }
        }
        return request(context, "POST", "/api/focus-bridge/heartbeat", body);
    }

    private static JSONObject request(Context context, String method, String internalPath,
                                      JSONObject payload) throws Exception {
        String publicPath = internalPath.startsWith("/api/") ? internalPath.substring(4) : internalPath;
        try {
            JSONObject result = requestUrl(
                    PUBLIC_BASE_URL + publicPath,
                    method,
                    withTransport(payload, internalPath, "public_https", false),
                    deviceToken(context),
                    10_000,
                    15_000);
            lastTransport = "public_https";
            fallbackActive = false;
            return result;
        } catch (IOException publicError) {
            try {
                JSONObject result = requestUrl(
                        baseUrl(context) + internalPath,
                        method,
                        withTransport(payload, internalPath, "tailnet_fallback", true),
                        null,
                        3_000,
                        5_000);
                lastTransport = "tailnet_fallback";
                fallbackActive = true;
                return result;
            } catch (Exception fallbackError) {
                lastTransport = "unavailable";
                fallbackActive = false;
                fallbackError.addSuppressed(publicError);
                throw fallbackError;
            }
        }
    }

    private static JSONObject withTransport(JSONObject payload, String path,
                                            String transport, boolean fallback) throws Exception {
        if (payload == null || !path.endsWith("/heartbeat")) return payload;
        JSONObject copy = new JSONObject(payload.toString());
        copy.put("transport", transport);
        copy.put("fallback_active", fallback);
        return copy;
    }

    private static JSONObject requestUrl(String address, String method, JSONObject payload,
                                         String bearerToken, int connectTimeout, int readTimeout) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(address).openConnection();
        try {
            connection.setConnectTimeout(connectTimeout);
            connection.setReadTimeout(readTimeout);
            connection.setRequestMethod(method);
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("User-Agent", "focus-bridge-android/1.3.0");
            if (bearerToken != null) {
                connection.setRequestProperty("Authorization", "Bearer " + bearerToken);
            }
            if (payload != null) {
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                try (OutputStream stream = connection.getOutputStream()) {
                    stream.write(payload.toString().getBytes(StandardCharsets.UTF_8));
                }
            }
            int status = connection.getResponseCode();
            InputStream input = status >= 400 ? connection.getErrorStream() : connection.getInputStream();
            StringBuilder response = new StringBuilder();
            if (input != null) {
                try (BufferedReader reader = new BufferedReader(
                        new java.io.InputStreamReader(input, StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = reader.readLine()) != null) response.append(line);
                }
            }
            JSONObject result = response.length() == 0 ? new JSONObject() : new JSONObject(response.toString());
            if (status >= 400) {
                throw new IllegalStateException(result.optString("error", "HTTP " + status));
            }
            return result;
        } finally {
            connection.disconnect();
        }
    }

    private static synchronized String deviceToken(Context context) throws IOException {
        File tokenFile = new File(context.getFilesDir(), TOKEN_FILE);
        if (!tokenFile.exists()) {
            byte[] random = new byte[32];
            new SecureRandom().nextBytes(random);
            String token = Base64.encodeToString(
                    random, Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
            try (FileOutputStream output = context.openFileOutput(TOKEN_FILE, Context.MODE_PRIVATE)) {
                output.write(token.getBytes(StandardCharsets.US_ASCII));
            }
        }
        try (FileInputStream input = new FileInputStream(tokenFile)) {
            byte[] bytes = new byte[(int) tokenFile.length()];
            int count = input.read(bytes);
            if (count <= 0) throw new IOException("empty bridge token");
            return new String(bytes, 0, count, StandardCharsets.US_ASCII).trim();
        }
    }
}
