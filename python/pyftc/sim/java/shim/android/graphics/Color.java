/*
 * The packed-int colour helpers of android.graphics.Color that FTC SDK classes use
 * (NormalizedRGBA.toColor, sensor argb()). Pure bit arithmetic, as documented for
 * Android: 0xAARRGGBB.
 */
package android.graphics;

public class Color {
    public static final int BLACK = 0xFF000000;
    public static final int WHITE = 0xFFFFFFFF;

    public static int alpha(int color) { return color >>> 24; }
    public static int red(int color) { return (color >> 16) & 0xFF; }
    public static int green(int color) { return (color >> 8) & 0xFF; }
    public static int blue(int color) { return color & 0xFF; }
    public static int rgb(int red, int green, int blue) { return 0xff000000 | (red << 16) | (green << 8) | blue; }
    public static int argb(int alpha, int red, int green, int blue) { return (alpha << 24) | (red << 16) | (green << 8) | blue; }

    public static void RGBToHSV(int red, int green, int blue, float[] hsv) {
        float r = red / 255f, g = green / 255f, b = blue / 255f;
        float max = Math.max(r, Math.max(g, b)), min = Math.min(r, Math.min(g, b));
        float d = max - min;
        float h;
        if (d == 0) h = 0;
        else if (max == r) h = 60 * (((g - b) / d) % 6);
        else if (max == g) h = 60 * (((b - r) / d) + 2);
        else h = 60 * (((r - g) / d) + 4);
        if (h < 0) h += 360;
        hsv[0] = h;
        hsv[1] = max == 0 ? 0 : d / max;
        hsv[2] = max;
    }

    public static void colorToHSV(int color, float[] hsv) {
        RGBToHSV(red(color), green(color), blue(color), hsv);
    }
}
