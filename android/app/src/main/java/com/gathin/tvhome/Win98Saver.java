package com.gathin.tvhome;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.Choreographer;
import android.view.View;

import java.util.Random;

/**
 * The Windows 98 "Starfield Simulation" screensaver: white stars fly out of the middle of a black screen. The
 * same view also drifts the clock window (a view above it) around the screen, bouncing off the edges, so
 * nothing stays put long enough to burn in. Drawn in code, no images; fixed arrays, no allocation per frame,
 * and capped at about 30 frames a second to go easy on a weak GPU. Only runs between start() and stop().
 */
final class Win98Saver extends View implements Choreographer.FrameCallback {
    private static final int STARS = 140;
    private static final long FRAME_MS = 33L;
    /** Window drift in pixels per second at 1920x1080. */
    private static final float DRIFT = 55f;
    private static final float DEPTH = 1000f;

    private final float[] sx = new float[STARS], sy = new float[STARS], sz = new float[STARS];
    private final Random random = new Random();
    private final Paint paint = new Paint();
    private final float density;
    private View window;
    private float vx, vy;
    private boolean running, placed;
    private long last;

    Win98Saver(Context ctx) {
        super(ctx);
        density = ctx.getResources().getDisplayMetrics().density;
        paint.setColor(0xFFFFFFFF);
        paint.setAntiAlias(false);
        setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
        for (int i = 0; i < STARS; i++) respawn(i, true);
    }

    /** The view to drift around (the clock window); its first spot is picked on the first frame. */
    void setWindow(View w) {
        window = w;
        placed = false;
        float a = (random.nextBoolean() ? 1 : -1) * DRIFT * density / 2f;
        float b = (random.nextBoolean() ? 1 : -1) * DRIFT * density / 2f * 0.7f;
        vx = a;
        vy = b;
    }

    void start() {
        if (running) return;
        running = true;
        last = 0;
        Choreographer.getInstance().postFrameCallback(this);
    }

    void stop() {
        running = false;
        Choreographer.getInstance().removeFrameCallback(this);
    }

    private void respawn(int i, boolean anywhere) {
        sx[i] = random.nextFloat() - 0.5f;
        sy[i] = random.nextFloat() - 0.5f;
        sz[i] = anywhere ? 0.05f * DEPTH + random.nextFloat() * 0.95f * DEPTH : DEPTH;
    }

    @Override
    public void doFrame(long nanos) {
        if (!running) return;
        Choreographer.getInstance().postFrameCallback(this);
        long ms = nanos / 1_000_000L;
        if (last != 0 && ms - last < FRAME_MS - 4) return;
        float dt = last == 0 ? 0f : Math.min((ms - last) / 1000f, 0.1f);
        last = ms;
        for (int i = 0; i < STARS; i++) {
            sz[i] -= 400f * dt;
            if (sz[i] < 20f) respawn(i, false);
        }
        moveWindow(dt);
        invalidate();
    }

    private void moveWindow(float dt) {
        View w = window;
        int pw = getWidth(), ph = getHeight();
        if (w == null || pw == 0 || w.getWidth() == 0) return;
        float maxX = pw - w.getWidth(), maxY = ph - w.getHeight();
        if (maxX < 0 || maxY < 0) return;
        if (!placed) {
            placed = true;
            w.setX(maxX * (0.1f + 0.8f * random.nextFloat()));
            w.setY(maxY * (0.1f + 0.8f * random.nextFloat()));
            return;
        }
        float x = w.getX() + vx * dt, y = w.getY() + vy * dt;
        if (x < 0) { x = 0; vx = Math.abs(vx); } else if (x > maxX) { x = maxX; vx = -Math.abs(vx); }
        if (y < 0) { y = 0; vy = Math.abs(vy); } else if (y > maxY) { y = maxY; vy = -Math.abs(vy); }
        w.setX(x);
        w.setY(y);
    }

    @Override
    protected void onDraw(Canvas c) {
        float w = getWidth(), h = getHeight();
        float cx = w / 2f, cy = h / 2f, k = h * 0.9f;
        for (int i = 0; i < STARS; i++) {
            float z = sz[i];
            float px = cx + sx[i] * k / z * DEPTH * 0.5f;
            float py = cy + sy[i] * k / z * DEPTH * 0.5f;
            if (px < 0 || px >= w || py < 0 || py >= h) {
                respawn(i, false);
                continue;
            }
            float s = (1.2f + 3.2f * (1f - z / DEPTH)) * density * 0.8f;
            int g = 110 + (int) (145 * (1f - z / DEPTH));
            paint.setColor(0xFF000000 | g << 16 | g << 8 | g);
            if (Win98.bit) {
                // 8-bit: chunky square stars snapped to a pixel grid, in white, light blue and yellow
                float u = 4f * density;
                px = (float) Math.floor(px / u) * u;
                py = (float) Math.floor(py / u) * u;
                s = s > 3f * density ? 2 * u : u;
                paint.setColor(i % 7 == 0 ? 0xFFFCE020 : i % 3 == 0 ? 0xFFA4E4FC : 0xFFFCFCFC);
            }
            c.drawRect(px, py, px + s, py + s, paint);
        }
    }
}
