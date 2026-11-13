package com.gathin.tvhome;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.LayerDrawable;
import android.graphics.drawable.StateListDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.TextView;

/**
 * glass_style win98: the popups over Home (tile menu, inputs/settings menus, module cards list and prompt, hints)
 * dressed as Windows 98 context menus and dialogs. Every helper only changes looks of views that MainActivity has
 * already built from the glass layouts; behaviour, focus and key handling stay where they were.
 */
final class Win98Menus {
    private Win98Menus() {}

    /** The popup's outer panel (popup_inputs / popup_cards): raised silver, flat, no shadow. */
    static void panel(View panel) {
        Context ctx = panel.getContext();
        panel.setBackgroundResource(Win98.d(R.drawable.w98_raised));
        int p = Win98.dp(ctx, 5);
        panel.setPadding(p, p, p, p);
        panel.setElevation(0f);
    }

    /** Etched menu separator: a dark grey line over a white line. */
    static View separator(Context ctx, LinearLayout rows) {
        View line = new View(ctx);
        line.setBackground(new LayerDrawable(new android.graphics.drawable.Drawable[]{
                new ColorDrawable(Win98.GREY_DARK), new ColorDrawable(Win98.WHITE)}));
        ((LayerDrawable) line.getBackground()).setLayerInset(0, 0, 0, 0, Win98.dp(ctx, 1));
        ((LayerDrawable) line.getBackground()).setLayerInset(1, 0, Win98.dp(ctx, 1), 0, 0);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 2 * Win98.dp(ctx, 1));
        int m = Win98.dp(ctx, 3), h = Win98.dp(ctx, 2);
        lp.setMargins(h, m, h, m);
        rows.addView(line, lp);
        return line;
    }

    /** A row of item_input (icon, title, connected dot, status): black on silver, white on navy when focused. */
    static void inputRow(View row) {
        Context ctx = row.getContext();
        row.setBackground(Win98.rowBackground());
        ViewGroup.LayoutParams rlp = row.getLayoutParams();
        if (rlp != null) rlp.height = Win98.dp(ctx, 36);
        row.setPaddingRelative(Win98.dp(ctx, 8), 0, Win98.dp(ctx, 10), 0);
        ImageView icon = row.findViewById(R.id.icon);
        icon.setImageTintList(Win98.ink());
        ViewGroup.LayoutParams ilp = icon.getLayoutParams();
        ilp.width = ilp.height = Win98.dp(ctx, 18);
        TextView title = row.findViewById(R.id.title);
        title.setTypeface(Win98.regular(ctx));
        title.setTextColor(Win98.ink());
        title.setTextSize(18);
        title.setLetterSpacing(0f);
        TextView status = row.findViewById(R.id.status);
        status.setTypeface(Win98.regular(ctx));
        status.setTextColor(Win98.ink());
        status.setTextSize(15);
        status.setLetterSpacing(0f);
        View dot = row.findViewById(R.id.dot);
        StateListDrawable green = new StateListDrawable();
        green.addState(new int[]{android.R.attr.state_focused}, new ColorDrawable(0xFF00FF00));
        green.addState(new int[]{}, new ColorDrawable(0xFF008000));
        dot.setBackground(green);
        dot.setDuplicateParentStateEnabled(true);
    }

    /** The Module cards popup: the small caps header becomes a navy title bar. */
    static void cardsTitle(View panel, int titleRes) {
        Context ctx = panel.getContext();
        if (!(panel instanceof LinearLayout) || ((LinearLayout) panel).getChildCount() == 0) return;
        LinearLayout box = (LinearLayout) panel;
        box.removeViewAt(0);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, Win98.dp(ctx, 30));
        lp.bottomMargin = Win98.dp(ctx, 3);
        box.addView(Win98.titleBar(ctx, ctx.getString(titleRes), true), 0, lp);
    }

    /** A row of item_card_row: the label and the small print all follow the row's focus colours. */
    static void cardRow(View row) {
        Context ctx = row.getContext();
        row.setBackground(Win98.rowBackground());
        int[] ids = {R.id.title, R.id.state, R.id.app, R.id.pkg, R.id.digest};
        float[] sizes = {17, 14, 13, 13, 12};
        for (int i = 0; i < ids.length; i++) {
            TextView t = row.findViewById(ids[i]);
            t.setTypeface(Win98.regular(ctx));
            t.setTextColor(Win98.ink());
            t.setTextSize(sizes[i]);
            t.setLetterSpacing(0f);
        }
    }

    /**
     * The module card prompt: a Windows 98 dialog. The glass panel's own title goes into the navy title bar,
     * the texts turn black and the two buttons raised silver. Returns the view to put in the Dialog.
     */
    static View prompt(View panel, boolean rtl) {
        Context ctx = panel.getContext();
        TextView title = panel.findViewById(R.id.title);
        String text = String.valueOf(title.getText());
        title.setVisibility(View.GONE);
        panel.setBackground(null);
        panel.setElevation(0f);
        int h = Win98.dp(ctx, 12);
        panel.setPadding(h, Win98.dp(ctx, 6), h, Win98.dp(ctx, 8));
        int[] ids = {R.id.body, R.id.names, R.id.hint, R.id.identity};
        float[] sizes = {17, 17, 15, 14};
        for (int i = 0; i < ids.length; i++) {
            TextView t = panel.findViewById(ids[i]);
            t.setTypeface(Win98.regular(ctx));
            t.setTextColor(Win98.BLACK);
            t.setTextSize(sizes[i]);
            t.setLetterSpacing(0f);
        }
        for (int id : new int[]{R.id.btnKeep, R.id.btnShow}) {
            TextView b = panel.findViewById(id);
            Win98.styleButton(b);
            b.setTextSize(17);
            b.setLetterSpacing(0f);
            b.setMinWidth(Win98.dp(ctx, 110));
            ViewGroup.LayoutParams lp = b.getLayoutParams();
            lp.height = Win98.dp(ctx, 36);
            if (lp instanceof ViewGroup.MarginLayoutParams) ((ViewGroup.MarginLayoutParams) lp).setMarginStart(Win98.dp(ctx, 8));
        }
        LinearLayout win = Win98.window(ctx, text, panel);
        if (rtl) win.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        return win;
    }

    /** A tooltip-like hint (pale yellow, thin black border) standing in for a Toast; not focusable, not touchable. */
    static PopupWindow hint(View root, CharSequence message) {
        Context ctx = root.getContext();
        TextView t = new TextView(ctx);
        t.setText(message);
        t.setTypeface(Win98.regular(ctx));
        t.setTextColor(Win98.BLACK);
        t.setTextSize(17);
        t.setGravity(Gravity.CENTER);
        t.setMaxWidth(Win98.dp(ctx, 640));
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(0xFFFFFFE1);
        bg.setStroke(Win98.dp(ctx, 1), Win98.BLACK);
        t.setBackground(bg);
        int ph = Win98.dp(ctx, 10), pv = Win98.dp(ctx, 6);
        t.setPadding(ph, pv, ph, pv);
        PopupWindow w = new PopupWindow(t, ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, false);
        w.setTouchable(false);
        w.setAnimationStyle(0);
        w.setElevation(0f);
        w.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        return w;
    }
}
