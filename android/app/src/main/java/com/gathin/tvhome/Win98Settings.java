package com.gathin.tvhome;

import android.app.Activity;
import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.StateListDrawable;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/**
 * win98 look for the Launcher settings screen and the quick settings panel. Only restyles views the layouts already
 * have (ids, click listeners, focus order and selected states are untouched): the settings are a silver properties
 * window with a navy title bar over the teal desktop, choices are option buttons in etched group boxes, toggles are
 * push buttons, the focused row is white on navy.
 */
final class Win98Settings {
    private static final int HINT = 0xFF404040;

    private Win98Settings() {}

    /** Inflates the settings layout, restyles it and sets it as the activity's content inside the teal desktop. */
    static void setLauncherSettings(Activity a, int layout, String title) {
        ScrollView scroll = (ScrollView) a.getLayoutInflater().inflate(layout, null);
        styleSettings(a, scroll);
        FrameLayout desk = new FrameLayout(a);
        desk.setBackgroundColor(Win98.TEAL);
        LinearLayout window = Win98.window(a, title, scroll);
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(Win98.dp(a, 780), ViewGroup.LayoutParams.MATCH_PARENT,
                Gravity.CENTER_HORIZONTAL);
        lp.topMargin = Win98.dp(a, 20);
        lp.bottomMargin = Win98.dp(a, 20);
        desk.addView(window, lp);
        a.setContentView(desk);
        Win98.applyFont(desk);
    }

    private static void styleSettings(Context ctx, ScrollView scroll) {
        scroll.setBackgroundColor(Win98.SILVER);
        scroll.setScrollbarFadingEnabled(false);
        scroll.setVerticalScrollBarEnabled(true);
        LinearLayout col = (LinearLayout) scroll.getChildAt(0);
        col.setPadding(Win98.dp(ctx, 28), Win98.dp(ctx, 10), Win98.dp(ctx, 28), Win98.dp(ctx, 16));
        for (int i = 0; i < col.getChildCount(); i++) {
            View v = col.getChildAt(i);
            if (i == 0) {                                   // the big title: the window's title bar says it now
                v.setVisibility(View.GONE);
            } else if (v instanceof LinearLayout) {
                styleGroup(ctx, (LinearLayout) v);
            } else if (v instanceof TextView) {
                TextView t = (TextView) v;
                if (t.isFocusable()) {
                    if (t.getId() == R.id.followThemeChoice) styleCheck(ctx, t);
                    else styleButton(ctx, t);
                } else if (t.getCurrentTextColor() == 0xFFFFFFFF) {   // a section label
                    t.setTextColor(Win98.BLACK);
                    t.setTypeface(Win98.bold(ctx));
                } else {                                            // a hint under a row
                    t.setTextColor(HINT);
                    t.setTypeface(Win98.regular(ctx));
                }
            }
        }
    }

    /** A row of option buttons in an etched group box. */
    private static void styleGroup(Context ctx, LinearLayout group) {
        group.setBackgroundResource(Win98.d(R.drawable.w98_set_group));
        int p = Win98.dp(ctx, 6);
        group.setPadding(p, p, p, p);
        for (int i = 0; i < group.getChildCount(); i++) {
            View c = group.getChildAt(i);
            if (!(c instanceof TextView)) continue;
            TextView t = (TextView) c;
            styleOption(ctx, t, Win98.d(R.drawable.w98_set_radio));
            ((LinearLayout.LayoutParams) t.getLayoutParams()).setMarginEnd(0);
        }
    }

    private static ColorStateList focusInk() {
        return new ColorStateList(new int[][]{{android.R.attr.state_focused}, {}}, new int[]{Win98.WHITE, Win98.BLACK});
    }

    private static Drawable focusBg() {
        StateListDrawable bg = new StateListDrawable();
        bg.addState(new int[]{android.R.attr.state_focused}, new ColorDrawable(Win98.NAVY));
        bg.addState(new int[]{}, new ColorDrawable(Color.TRANSPARENT));
        return bg;
    }

    /** Option button / checkbox row: sunken indicator on the left, text black; white on navy while focused. */
    private static void styleOption(Context ctx, TextView t, int indicator) {
        t.setTypeface(Win98.regular(ctx));
        t.setTextColor(focusInk());
        t.setBackground(focusBg());
        t.setGravity(Gravity.CENTER_VERTICAL | Gravity.START);
        t.setPaddingRelative(Win98.dp(ctx, 16), 0, Win98.dp(ctx, 12), 0);
        t.setCompoundDrawablePadding(Win98.dp(ctx, 12));
        t.setCompoundDrawablesRelativeWithIntrinsicBounds(indicator, 0, 0, 0);
        t.setCompoundDrawableTintList(null);
    }

    private static void styleCheck(Context ctx, TextView t) {
        styleOption(ctx, t, Win98.d(R.drawable.w98_set_check));
    }

    private static void styleButton(Context ctx, TextView t) {
        t.setBackgroundResource(Win98.d(R.drawable.w98_set_button));
        t.setTypeface(Win98.regular(ctx));
        t.setTextColor(focusInk());
        t.setGravity(Gravity.CENTER);
    }

    /** Quick settings panel: raised silver like the Start menu. */
    static void styleQuickPanel(View panel) {
        Context ctx = panel.getContext();
        panel.setBackgroundResource(Win98.d(R.drawable.w98_raised));
        panel.setElevation(0f);
        int p = Win98.dp(ctx, 4);
        panel.setPadding(p, p, p, p);
        panel.setMinimumWidth(Win98.dp(ctx, 300));
    }

    /** One quick settings row (item_input): black MS Sans Serif, white on navy when focused. */
    static void styleQuickRow(View row) {
        Context ctx = row.getContext();
        row.setBackground(Win98.rowBackground());
        row.getLayoutParams().height = Win98.dp(ctx, 46);
        TextView title = row.findViewById(R.id.title);
        title.setTypeface(Win98.regular(ctx));
        title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18);
        title.setTextColor(Win98.ink());
        ImageView icon = row.findViewById(R.id.icon);
        icon.setImageTintList(Win98.ink());
        icon.getLayoutParams().width = Win98.dp(ctx, 24);
        icon.getLayoutParams().height = Win98.dp(ctx, 24);
        TextView status = row.findViewById(R.id.status);
        status.setTypeface(Win98.regular(ctx));
        status.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13);
        status.setTextColor(new ColorStateList(new int[][]{{android.R.attr.state_focused}, {}},
                new int[]{Win98.WHITE, HINT}));
    }
}
