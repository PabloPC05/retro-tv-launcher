package com.gathin.tvhome;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.Toast;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

/**
 * Switches the launcher's skin (tema del piso): Windows 98, Windows XP / Frutiger Aero or 8-bit. Each skin is kept on
 * the TV in the theme folder under skins/<name>/ (config.json, wallpaper.jpg, banners/, icons/); this copies it over
 * the live theme and restarts Home. Reached through three launcher entries named "Windows 98", "Frutiger Aero" and
 * "8 bits" (activity-alias with a "skin" meta-data), so the remote's voice button can open them by name
 * ("abre Windows 98"), or with an extra: am start -n com.gathin.tvhome/.SkinActivity --es skin xp
 */
public class SkinActivity extends Activity {
    static final List<String> SKINS = Arrays.asList("win98", "xp", "8bit");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        String skin = getIntent().getStringExtra("skin");
        if (skin == null) {
            try {
                ActivityInfo ai = getPackageManager().getActivityInfo(getComponentName(), PackageManager.GET_META_DATA);
                if (ai.metaData != null) skin = ai.metaData.getString("skin");
            } catch (PackageManager.NameNotFoundException ignored) {
            }
        }
        File dir = Config.dir(this);
        File src = skin == null || dir == null ? null : new File(dir, "skins/" + skin);
        if (!SKINS.contains(skin) || src == null || !new File(src, Config.FILE_NAME).isFile()) {
            Toast.makeText(this, "Esa skin no está en la tele", Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        try {
            copy(new File(src, Config.FILE_NAME), new File(dir, Config.FILE_NAME));
            File wall = new File(src, "wallpaper.jpg");
            if (wall.isFile()) copy(wall, new File(dir, "wallpaper.jpg"));
            else //noinspection ResultOfMethodCallIgnored
                new File(dir, "wallpaper.jpg").delete();
            for (String sub : new String[]{"banners", "icons"}) {
                File to = new File(dir, sub);
                File[] old = to.listFiles();
                if (old != null) for (File f : old) //noinspection ResultOfMethodCallIgnored
                    f.delete();
                //noinspection ResultOfMethodCallIgnored
                to.mkdirs();
                File[] fresh = new File(src, sub).listFiles();
                if (fresh != null) for (File f : fresh) if (f.isFile()) copy(f, new File(to, f.getName()));
            }
            try (OutputStream out = new FileOutputStream(new File(dir, "theme_revision"))) {
                out.write(UUID.randomUUID().toString().replace("-", "").getBytes());
            }
        } catch (IOException e) {
            Toast.makeText(this, "No se pudo cambiar la skin: " + e.getMessage(), Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        String name = "win98".equals(skin) ? "Windows 98" : "xp".equals(skin) ? "Frutiger Aero" : "8 bits";
        Toast.makeText(this, "Skin: " + name, Toast.LENGTH_SHORT).show();
        // Restart the whole process: the skin (palette, fonts, banners) is read once per process.
        Intent home = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME).setPackage(getPackageName())
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(home);
        finish();
        new Handler(Looper.getMainLooper()).postDelayed(() -> android.os.Process.killProcess(android.os.Process.myPid()), 600);
    }

    private static void copy(File from, File to) throws IOException {
        try (InputStream in = new FileInputStream(from); OutputStream out = new FileOutputStream(to)) {
            byte[] buf = new byte[65536];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
        }
    }
}
