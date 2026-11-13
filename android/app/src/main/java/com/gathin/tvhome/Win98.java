package com.gathin.tvhome;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * Shared look for glass_style "win98" (the flat's theme): every launcher screen (Home, the app library, the tile
 * menu, launcher settings, the clock) asks on() and, when it is on, builds its chrome with these helpers so they all
 * match: silver raised panels, a navy title bar, black text in MS Sans Serif (the bundled font_body), and the
 * focused row or button in white on navy.
 *
 * Drawables already in res/drawable: w98_raised (raised panel/button), w98_pressed (pushed in), w98_button (selector:
 * raised, pushed in while focused), w98_sunken (sunken field), w98_taskbar. Fonts: bold() / regular(), per skin (res/font/skin_*).
 */
final class Win98 {
    // Not final on purpose: glass_style "xp" (Windows XP / Frutiger Aero) swaps the palette at start (init()).
    static int SILVER = 0xFFC0C0C0, NAVY = 0xFF000080, NAVY_LIGHT = 0xFF1084D0, GREY_DARK = 0xFF808080,
            WHITE = 0xFFFFFFFF, BLACK = 0xFF000000, TEAL = 0xFF008080,
            TITLE_A = 0xFF000080, TITLE_B = 0xFF1084D0;

    private static Boolean cached;
    /** glass_style "xp": the same screens with Windows XP Luna / Frutiger Aero colours and xp_* drawables. */
    static boolean xp;
    /** glass_style "8bit": NES-style dark boxes with white pixel borders, yellow selection, pixel font. */
    static boolean bit;
    private static Context app;

    /** Sets the skin once per process from the theme's glass_style. */
    static void init(Context ctx, String glassStyle) {
        app = ctx.getApplicationContext();
        xp = Config.GLASS_XP.equals(glassStyle);
        bit = Config.GLASS_8BIT.equals(glassStyle);
        cached = xp || bit || Config.GLASS_WIN98.equals(glassStyle);
        if (bit) {
            // Dark boxes, so the "ink" is light: BLACK is the text colour, WHITE the text on the selection.
            SILVER = 0xFF0000A8; NAVY = 0xFFFCE020; NAVY_LIGHT = 0xFFFCE020; GREY_DARK = 0xFF7C7C7C; TEAL = 0xFF0000A8;
            BLACK = 0xFFFCFCFC; WHITE = 0xFF000000; TITLE_A = 0xFFD82800; TITLE_B = 0xFFD82800;
        }
        if (xp) {
            SILVER = 0xFFECE9D8; NAVY = 0xFF316AC5; NAVY_LIGHT = 0xFF3D95FF; GREY_DARK = 0xFFACA899; TEAL = 0xFF3A6EA5;
            TITLE_A = 0xFF0A5ADB; TITLE_B = 0xFF3D95FF;
        }
    }

    private static final java.util.Map<String, Drawable> themeIcons = new java.util.HashMap<>();

    /** The skin's own icon for an app (theme folder icons/<package>.png), or null to use the app's icon. */
    static Drawable themeIcon(Context ctx, String pkg) {
        if (!on(ctx) || pkg == null) return null;
        if (themeIcons.containsKey(pkg)) return themeIcons.get(pkg);
        Drawable d = null;
        java.io.File dir = Config.dir(ctx);
        java.io.File f = dir == null ? null : new java.io.File(dir, "icons/" + pkg + ".png");
        if (f != null && f.isFile()) {
            android.graphics.Bitmap b = android.graphics.BitmapFactory.decodeFile(f.getPath());
            if (b != null) {
                android.graphics.drawable.BitmapDrawable bd = new android.graphics.drawable.BitmapDrawable(ctx.getResources(), b);
                bd.setFilterBitmap(!bit);   // pixel art stays crisp
                d = bd;
            }
        }
        themeIcons.put(pkg, d);
        return d;
    }

    /** AlertDialog theme matching the skin (0 for the system one). */
    static int dialogTheme(Context ctx) {
        if (!on(ctx)) return 0;
        return bit ? R.style.BitDialog : xp ? R.style.XpDialog : R.style.W98Dialog;
    }

    /** Shade drawn over a focused icon: navy in Windows 98, light blue in XP, none in 8-bit. */
    static int selectedShade() {
        return bit ? 0 : xp ? 0x55316AC5 : 0x80000080;
    }

    /** The xp_* twin of a w98_* drawable while the XP skin is on (the w98 one when there is no twin). */
    static int d(int w98Res) {
        if ((!xp && !bit) || app == null) return w98Res;
        try {
            String name = app.getResources().getResourceEntryName(w98Res);
            if (!name.startsWith("w98_")) return w98Res;
            int id = app.getResources().getIdentifier((bit ? "bit_" : "xp_") + name.substring(4), "drawable", app.getPackageName());
            return id != 0 ? id : w98Res;
        } catch (RuntimeException e) {
            return w98Res;
        }
    }

    private Win98() {}

    /** True when the theme on the TV asks for the Windows 98 look (glass_style "win98"). Read once per process. */
    static boolean on(Context ctx) {
        if (AppAdapter.win98) return true;
        if (cached == null) {
            try {
                init(ctx, Config.load(ctx.getApplicationContext()).glassStyle);
            } catch (RuntimeException e) {
                cached = false;
            }
        }
        return cached;
    }

    static int dp(Context ctx, float v) {
        return Math.round(TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, ctx.getResources().getDisplayMetrics()));
    }

    /** The skin's bold face: MS Sans Serif Bold, Selawik Bold or Press Start 2P (which has no bold). */
    static Typeface bold(Context ctx) {
        on(ctx);
        return ctx.getResources().getFont(bit ? R.font.skin_pix : xp ? R.font.skin_xp_bold : R.font.skin_w98_bold);
    }

    /** The skin's regular face. */
    static Typeface regular(Context ctx) {
        on(ctx);
        return ctx.getResources().getFont(bit ? R.font.skin_pix : xp ? R.font.skin_xp : R.font.skin_w98);
    }

    /** Gives every TextView under root the skin's font (layouts name the theme-neutral Outfit). */
    static void applyFont(View root) {
        if (root == null || !on(root.getContext())) return;
        Typeface reg = regular(root.getContext()), b = bold(root.getContext());
        apply(root, reg, b);
    }

    private static void apply(View v, Typeface reg, Typeface b) {
        if (v instanceof TextView) {
            TextView t = (TextView) v;
            Typeface cur = t.getTypeface();
            t.setTypeface(cur != null && cur.isBold() ? b : reg);
        }
        if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) apply(g.getChildAt(i), reg, b);
        }
    }

    /** A window: raised silver frame holding a navy title bar with the title, then the content. */
    static LinearLayout window(Context ctx, String title, View content) {
        LinearLayout w = new LinearLayout(ctx);
        w.setOrientation(LinearLayout.VERTICAL);
        w.setBackgroundResource(d(R.drawable.w98_raised));
        int p = dp(ctx, 4);
        w.setPadding(p, p, p, p);
        w.addView(titleBar(ctx, title, true), new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(ctx, 30)));
        if (content != null) {
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f);
            lp.topMargin = dp(ctx, 4);
            w.addView(content, lp);
        }
        return w;
    }

    /** The title bar alone: navy to light blue when active, greys when not; bold white title on the left. */
    static View titleBar(Context ctx, String title, boolean active) {
        FrameLayout bar = new FrameLayout(ctx);
        if (xp) {
            // Luna: glossy blue from top to bottom, rounded top corners; the inactive one washed out.
            GradientDrawable g = new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, active
                    ? new int[]{0xFF3D95FF, 0xFF0A5ADB, 0xFF0841B4} : new int[]{0xFFA6B8E8, 0xFF7A96DF, 0xFF7A96DF});
            float r = dp(ctx, 7);
            g.setCornerRadii(new float[]{r, r, r, r, 0, 0, 0, 0});
            bar.setBackground(g);
        } else {
            bar.setBackground(new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,
                    active ? new int[]{TITLE_A, TITLE_B} : new int[]{GREY_DARK, bit ? GREY_DARK : 0xFFB5B5B5}));
        }
        TextView t = new TextView(ctx);
        t.setText(title);
        t.setTextColor(bit ? 0xFFFCFCFC : active ? WHITE : SILVER);
        if (xp) t.setShadowLayer(2f, 1f, 1f, 0xAA000033);
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 17);
        t.setTypeface(bold(ctx));
        t.setSingleLine(true);
        t.setGravity(Gravity.CENTER_VERTICAL);
        t.setPadding(dp(ctx, 8), 0, dp(ctx, 8), 0);
        bar.addView(t, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        return bar;
    }

    /** Text colours for a row or label: white while focused/selected/activated, black otherwise. */
    static ColorStateList ink() {
        return new ColorStateList(new int[][]{{android.R.attr.state_focused}, {android.R.attr.state_selected},
                {android.R.attr.state_activated}, {}}, new int[]{WHITE, WHITE, WHITE, BLACK});
    }

    /** Background for a list/menu row: navy while focused, transparent otherwise. */
    static Drawable rowBackground() {
        StateListDrawable bg = new StateListDrawable();
        bg.addState(new int[]{android.R.attr.state_focused}, new ColorDrawable(NAVY));
        bg.addState(new int[]{android.R.attr.state_selected}, new ColorDrawable(NAVY));
        bg.addState(new int[]{}, new ColorDrawable(Color.TRANSPARENT));
        return bg;
    }

    /** Styles a menu/list row: black MS Sans Serif text (white on navy when focused), icons tinted the same. */
    static void styleRow(TextView row) {
        Context ctx = row.getContext();
        row.setTypeface(regular(ctx));
        row.setTextColor(ink());
        row.setCompoundDrawableTintList(ink());
        row.setBackground(rowBackground());
    }

    /** Styles a push button: raised silver, pushed in while focused, black text. */
    static void styleButton(TextView b) {
        Context ctx = b.getContext();
        b.setBackgroundResource(R.drawable.w98_button);
        b.setTypeface(regular(ctx));
        b.setTextColor(BLACK);
        b.setCompoundDrawableTintList(ColorStateList.valueOf(BLACK));
    }
}
