package com.gathin.tvhome;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.os.SystemClock;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.text.Normalizer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Voice skin switching (tema del piso). The assistant on this TV does not open launcher entries by name, so this
 * reads what it understood on its search screen (the query shown at the top after speaking into the remote) and,
 * when the whole query is a skin name, optionally after "abre", "pon", "cambia a"..., switches to that skin.
 * Only watches com.google.android.katniss (see res/xml/skin_voice_service.xml); everything else is ignored.
 */
public class SkinVoiceService extends AccessibilityService {
    private static final Pattern QUERY = Pattern.compile(
            "^(?:(?:abre|abrir|pon|poner|activa|activar|cambia a|cambiar a|usa|usar|quiero|el|la|modo|estilo|tema|skin|tema de|estilo de)\\s+)*"
                    + "(windows 98|windows noventa y ocho|windows98|windows 9 8|(?:fruti ?gu?er|fruti ger|frutiger)(?: a[ei]?ro| aero)?|aero|windows xp|windows equis pe|8 bits?|ocho bits?|8bit|8-bit|8 bit)$");
    private long lastSwitch;

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (SystemClock.elapsedRealtime() - lastSwitch < 8000) return;
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null) return;
        String skin = find(root, 0);
        if (skin == null) return;
        lastSwitch = SystemClock.elapsedRealtime();
        performGlobalAction(GLOBAL_ACTION_BACK);   // close the assistant's results
        Intent i = new Intent(this, SkinActivity.class).putExtra("skin", skin)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(i);
    }

    /** The skin named by a text on screen that is only a skin name (the assistant's query), or null. */
    private String find(AccessibilityNodeInfo n, int depth) {
        if (n == null || depth > 25) return null;
        CharSequence t = n.getText();
        if (t != null && t.length() < 60) {
            String s = skinFor(t.toString());
            if (s != null) return s;
        }
        for (int i = 0; i < n.getChildCount(); i++) {
            String s = find(n.getChild(i), depth + 1);
            if (s != null) return s;
        }
        return null;
    }

    static String skinFor(String text) {
        String q = Normalizer.normalize(text, Normalizer.Form.NFD).replaceAll("\\p{M}", "")
                .toLowerCase(java.util.Locale.ROOT).replaceAll("[¡!¿?.,\"']", " ").replaceAll("\\s+", " ").trim();
        Matcher m = QUERY.matcher(q);
        if (!m.matches()) return null;
        String name = m.group(1);
        if (name.contains("98") || name.contains("noventa")) return "win98";
        if (name.contains("frut") || name.contains("aero") || name.contains("xp") || name.contains("equis")) return "xp";
        return "8bit";
    }

    @Override
    public void onInterrupt() {
    }
}
