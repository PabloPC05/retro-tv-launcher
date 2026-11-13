package com.gathin.tvhome;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Shader;
import android.util.AttributeSet;
import android.view.View;

/**
 * A translucent glass slab: soft sheen fill, bright top specular, crisp rim and a faint outer glow.
 * One instance floats over the grid and is moved with spring animations between tiles.
 */
public class GlassView extends View {

    private final Paint fill = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint specular = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint rim = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint glow = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF rect = new RectF();
    private final float density;
    private float radius;
    /** Glow colour as 0xRRGGBB: white normally, a festival's accent (diya gold) while a festive skin is on. */
    private int glowRgb = 0xFFFFFF;
    /** Glow strength: the white glow stays faint, a coloured one needs more alpha to read as warm light. */
    private int glowAlpha = 0x30;
    /** glass_style rim or halo: no sheen and no fill, only the crisp rim (and, for halo, a lighter outer glow). */
    private boolean flat;
    private boolean halo;
    /** glass_style win98: a square dotted focus rectangle, like a focused icon or button in Windows 98. */
    private boolean win98;
    /** glass_style xp: a clear, glossy Frutiger Aero bubble: faint tint, white sheen on the top half, bright rim, cyan glow. */
    private boolean aero;
    /** glass_style 8bit: a chunky yellow pixel frame with notched corners (the tile art draws its own ▶). */
    private boolean pix;
    private final Paint dots = new Paint();

    public GlassView(Context context, AttributeSet attrs) {
        super(context, attrs);
        density = getResources().getDisplayMetrics().density;
        radius = 20f * density;
        rim.setStyle(Paint.Style.STROKE);
        rim.setStrokeWidth(1.5f * density);
        rim.setColor(0xCCFFFFFF);
        glow.setStyle(Paint.Style.STROKE);
        // Cache the slab as a texture. The spring only changes translation, so the GPU can
        // move it without replaying clipPath and the glow on every frame. That path is
        // software-rendered on the MT5895 and is what makes the highlight crawl.
        setLayerType(LAYER_TYPE_HARDWARE, null);
    }

    /** Tints the rim and the outer glow; 0 restores the plain white glass. */
    void setAccent(int argb) {
        if (argb == 0) {
            glowRgb = 0xFFFFFF;
            glowAlpha = 0x30;
            rim.setColor(0xCCFFFFFF);
        } else {
            glowRgb = argb & 0xFFFFFF;
            glowAlpha = 0x70;
            // The rim is the accent lifted towards white, so the edge still reads as glass, not paint.
            int r = (((glowRgb >> 16) & 0xFF) + 255 * 2) / 3, g = (((glowRgb >> 8) & 0xFF) + 255 * 2) / 3,
                    b = ((glowRgb & 0xFF) + 255 * 2) / 3;
            rim.setColor(0xE6000000 | (r << 16) | (g << 8) | b);
        }
        invalidate();
    }

    /** One of Config's GLASS_* styles. */
    void setStyle(String style) {
        flat = Config.GLASS_RIM.equals(style) || Config.GLASS_HALO.equals(style);
        halo = Config.GLASS_HALO.equals(style);
        win98 = Config.GLASS_WIN98.equals(style);
        aero = Config.GLASS_XP.equals(style);
        pix = Config.GLASS_8BIT.equals(style);
        dots.setStyle(Paint.Style.STROKE);
        dots.setStrokeWidth(Math.max(2f, 2f * density));
        dots.setPathEffect(new android.graphics.DashPathEffect(new float[]{2f * density, 2f * density}, 0));
        rim.setStrokeWidth((flat ? 2f : 1.5f) * density);
        invalidate();
    }

    void setRadius(float px) {
        radius = px;
        invalidate();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        fill.setShader(new LinearGradient(0, 0, 0, h, 0x3DFFFFFF, 0x12FFFFFF, Shader.TileMode.CLAMP));
        specular.setShader(new LinearGradient(0, 0, 0, h * 0.45f, 0x66FFFFFF, 0x00FFFFFF, Shader.TileMode.CLAMP));
    }

    @Override
    protected void onDraw(Canvas canvas) {
        float inset = 6f * density;   // room for the glow
        rect.set(inset, inset, getWidth() - inset, getHeight() - inset);
        if (pix) return;   // 8bit: each tile draws its own yellow frame and ▶ cursor when focused
        if (aero) {
            float rr = 12f * density, g = 3f * density;
            RectF o = new RectF(rect.left - g, rect.top - g, rect.right + g, rect.bottom + g);
            // soft cyan glow around
            for (int i = 0; i < 8; i++) {
                float e = i * 1.2f * density;
                dots.setPathEffect(null);
                dots.setStrokeWidth(1.6f * density);
                dots.setColor(((int) (70 * (1f - i / 8f)) << 24) | 0x7FDBFF);
                canvas.drawRoundRect(o.left - e, o.top - e, o.right + e, o.bottom + e, rr + e, rr + e, dots);
            }
            Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
            p.setShader(new LinearGradient(0, o.top, 0, o.bottom, 0x38BFE9FF, 0x1478C8FF, Shader.TileMode.CLAMP));
            canvas.drawRoundRect(o, rr, rr, p);
            p.setShader(new LinearGradient(0, o.top, 0, o.top + o.height() * 0.48f, 0x8CFFFFFF, 0x10FFFFFF, Shader.TileMode.CLAMP));
            canvas.save();
            canvas.clipRect(o.left, o.top, o.right, o.top + o.height() * 0.48f);
            canvas.drawRoundRect(o, rr, rr, p);
            canvas.restore();
            p.setShader(null);
            p.setStyle(Paint.Style.STROKE);
            p.setStrokeWidth(2f * density);
            p.setColor(0xE6FFFFFF);
            canvas.drawRoundRect(o, rr, rr, p);
            return;
        }
        if (win98) {
            // Black dots over a white line: readable over the teal desktop and over a grey window alike.
            dots.setPathEffect(null);
            dots.setColor(0xFFFFFFFF);
            canvas.drawRect(rect.left - 2 * density, rect.top - 2 * density, rect.right + 2 * density, rect.bottom + 2 * density, dots);
            dots.setPathEffect(new android.graphics.DashPathEffect(new float[]{2f * density, 2f * density}, 0));
            dots.setColor(0xFF000000);
            canvas.drawRect(rect.left - 2 * density, rect.top - 2 * density, rect.right + 2 * density, rect.bottom + 2 * density, dots);
            return;
        }

        // Outer glow: thin rings across the inset, each a little fainter, so it fades out smoothly. Three wide
        // strokes left visible bands once the glow took an app's colour at a stronger alpha. The hardware layer
        // caches the result, so the rings cost one draw, not one per frame of the spring.
        if (!flat || halo) {
            int rings = 12;
            float step = inset / rings;
            int alpha = flat ? glowAlpha / 2 : glowAlpha;
            glow.setStrokeWidth(step + 0.5f);
            for (int i = 0; i < rings; i++) {
                float o = step * (i + 0.5f);
                float t = 1f - (float) i / rings;
                glow.setColor(Math.round(alpha * t) << 24 | glowRgb);
                canvas.drawRoundRect(rect.left - o, rect.top - o, rect.right + o, rect.bottom + o, radius + o, radius + o, glow);
            }
        }
        if (flat) {
            canvas.drawRoundRect(rect, radius, radius, rim);
            return;
        }

        canvas.drawRoundRect(rect, radius, radius, fill);

        // Sheen across the top 45%: clipRect stays on the GPU (clipPath did not on the MT5895) and
        // the round rect under it keeps the top corners rounded with a flat bottom edge.
        canvas.save();
        canvas.clipRect(rect.left, rect.top, rect.right, rect.top + rect.height() * 0.45f);
        canvas.drawRoundRect(rect, radius, radius, specular);
        canvas.restore();

        canvas.drawRoundRect(rect, radius, radius, rim);
    }
}
