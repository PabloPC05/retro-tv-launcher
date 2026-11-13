package com.gathin.tvhome;

import java.util.List;
import java.util.regex.Pattern;

/** The files ThemeProvider may write or delete under Config.dir, by the URI's path segments. */
final class ThemeFiles {
    static final String WALLPAPERS = "wallpapers";
    /** The names tools/theme.sh accepts for a collection image, and the types WallpaperRotation reads. */
    private static final Pattern IMAGE = Pattern.compile("[A-Za-z0-9_.-]+\\.(jpg|jpeg|png|webp)",
            Pattern.CASE_INSENSITIVE);

    private ThemeFiles() {}

    /** The path relative to the theme directory, e.g. "config.json" or "wallpapers/dusk.jpg", or null if refused. */
    static String path(List<String> segments) {
        if (segments == null) return null;
        if (segments.size() == 1) {
            String name = segments.get(0);
            return Config.FILE_NAME.equals(name) || "wallpaper.jpg".equals(name) || "theme_revision".equals(name)
                    ? name : null;
        }
        // win98 (tema del piso): banners/<package>.png and banners/<package>_on.png, the tiles' own art.
        // The three skins kept on the TV, for SkinActivity to switch between them by voice.
        if (segments.size() >= 3 && "skins".equals(segments.get(0)) && SkinActivity.SKINS.contains(segments.get(1))) {
            String base = "skins/" + segments.get(1) + "/";
            if (segments.size() == 3 && (Config.FILE_NAME.equals(segments.get(2)) || "wallpaper.jpg".equals(segments.get(2))))
                return base + segments.get(2);
            if (segments.size() == 4 && ("banners".equals(segments.get(2)) || "icons".equals(segments.get(2)))
                    && collectionImage(segments.get(3)))
                return base + segments.get(2) + "/" + segments.get(3);
            return null;
        }
        if (segments.size() == 2 && ("banners".equals(segments.get(0)) || "icons".equals(segments.get(0)))
                && collectionImage(segments.get(1))) {
            return segments.get(0) + "/" + segments.get(1);
        }
        if (segments.size() == 2 && WALLPAPERS.equals(segments.get(0))
                && (collectionImage(segments.get(1)) || WallpaperCaptions.FILE_NAME.equals(segments.get(1)))) {
            return WALLPAPERS + "/" + segments.get(1);
        }
        return null;
    }

    /** True for "wallpapers" alone: a delete of it clears the collection's images. */
    static boolean isCollection(List<String> segments) {
        return segments != null && segments.size() == 1 && WALLPAPERS.equals(segments.get(0));
    }

    static boolean collectionImage(String name) {
        return name != null && !name.startsWith(".") && IMAGE.matcher(name).matches();
    }
}
