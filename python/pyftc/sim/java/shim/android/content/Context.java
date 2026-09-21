/*
 * Type-only stand-in for android.content.Context so real SDK classes whose
 * signatures mention it (HardwareMap's constructor, RobotLog) link on a plain
 * JVM. The simulator always passes null; any real use fails with an
 * AbstractMethodError/NoSuchMethodError instead of silently doing something.
 */
package android.content;

public abstract class Context {
}
