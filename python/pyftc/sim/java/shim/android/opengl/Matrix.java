/*
 * Pure-Java implementation of the android.opengl.Matrix operations the FTC SDK's
 * OpenGLMatrix uses (Orientation.getRotationMatrix, RevHubOrientationOnRobot,
 * IMU math). On Android several of these are native; the android.jar stub
 * throws, so the simulator supplies the documented behaviour: 4x4 float
 * matrices in column-major order, m[offset + column * 4 + row].
 */
package android.opengl;

public class Matrix {
    public Matrix() {}

    public static void setIdentityM(float[] sm, int smOffset) {
        for (int i = 0; i < 16; i++) sm[smOffset + i] = 0;
        for (int i = 0; i < 16; i += 5) sm[smOffset + i] = 1.0f;
    }

    public static void multiplyMM(float[] result, int resultOffset, float[] lhs, int lhsOffset, float[] rhs, int rhsOffset) {
        float[] tmp = new float[16];
        for (int col = 0; col < 4; col++) {
            for (int row = 0; row < 4; row++) {
                float sum = 0;
                for (int k = 0; k < 4; k++) {
                    sum += lhs[lhsOffset + k * 4 + row] * rhs[rhsOffset + col * 4 + k];
                }
                tmp[col * 4 + row] = sum;
            }
        }
        System.arraycopy(tmp, 0, result, resultOffset, 16);
    }

    public static void multiplyMV(float[] resultVec, int resultVecOffset, float[] lhsMat, int lhsMatOffset, float[] rhsVec, int rhsVecOffset) {
        float[] tmp = new float[4];
        for (int row = 0; row < 4; row++) {
            float sum = 0;
            for (int k = 0; k < 4; k++) sum += lhsMat[lhsMatOffset + k * 4 + row] * rhsVec[rhsVecOffset + k];
            tmp[row] = sum;
        }
        System.arraycopy(tmp, 0, resultVec, resultVecOffset, 4);
    }

    public static void setRotateM(float[] rm, int rmOffset, float a, float x, float y, float z) {
        rm[rmOffset + 3] = 0;
        rm[rmOffset + 7] = 0;
        rm[rmOffset + 11] = 0;
        rm[rmOffset + 12] = 0;
        rm[rmOffset + 13] = 0;
        rm[rmOffset + 14] = 0;
        rm[rmOffset + 15] = 1;
        a *= (float) (Math.PI / 180.0f);
        float s = (float) Math.sin(a);
        float c = (float) Math.cos(a);
        if (1.0f == x && 0.0f == y && 0.0f == z) {
            rm[rmOffset + 5] = c;   rm[rmOffset + 10] = c;
            rm[rmOffset + 6] = s;   rm[rmOffset + 9] = -s;
            rm[rmOffset + 1] = 0;   rm[rmOffset + 2] = 0;
            rm[rmOffset + 4] = 0;   rm[rmOffset + 8] = 0;
            rm[rmOffset + 0] = 1;
        } else if (0.0f == x && 1.0f == y && 0.0f == z) {
            rm[rmOffset + 0] = c;   rm[rmOffset + 10] = c;
            rm[rmOffset + 8] = s;   rm[rmOffset + 2] = -s;
            rm[rmOffset + 1] = 0;   rm[rmOffset + 4] = 0;
            rm[rmOffset + 6] = 0;   rm[rmOffset + 9] = 0;
            rm[rmOffset + 5] = 1;
        } else if (0.0f == x && 0.0f == y && 1.0f == z) {
            rm[rmOffset + 0] = c;   rm[rmOffset + 5] = c;
            rm[rmOffset + 1] = s;   rm[rmOffset + 4] = -s;
            rm[rmOffset + 2] = 0;   rm[rmOffset + 6] = 0;
            rm[rmOffset + 8] = 0;   rm[rmOffset + 9] = 0;
            rm[rmOffset + 10] = 1;
        } else {
            float len = (float) Math.sqrt(x * x + y * y + z * z);
            if (1.0f != len) {
                float recipLen = 1.0f / len;
                x *= recipLen;
                y *= recipLen;
                z *= recipLen;
            }
            float nc = 1.0f - c;
            float xy = x * y;
            float yz = y * z;
            float zx = z * x;
            float xs = x * s;
            float ys = y * s;
            float zs = z * s;
            rm[rmOffset + 0] = x * x * nc + c;
            rm[rmOffset + 4] = xy * nc - zs;
            rm[rmOffset + 8] = zx * nc + ys;
            rm[rmOffset + 1] = xy * nc + zs;
            rm[rmOffset + 5] = y * y * nc + c;
            rm[rmOffset + 9] = yz * nc - xs;
            rm[rmOffset + 2] = zx * nc - ys;
            rm[rmOffset + 6] = yz * nc + xs;
            rm[rmOffset + 10] = z * z * nc + c;
        }
    }

    public static void rotateM(float[] m, int mOffset, float a, float x, float y, float z) {
        float[] r = new float[16];
        setRotateM(r, 0, a, x, y, z);
        multiplyMM(m, mOffset, m, mOffset, r, 0);
    }

    public static void rotateM(float[] rm, int rmOffset, float[] m, int mOffset, float a, float x, float y, float z) {
        float[] r = new float[16];
        setRotateM(r, 0, a, x, y, z);
        multiplyMM(rm, rmOffset, m, mOffset, r, 0);
    }

    public static void scaleM(float[] m, int mOffset, float x, float y, float z) {
        for (int i = 0; i < 4; i++) {
            m[mOffset + i] *= x;
            m[mOffset + 4 + i] *= y;
            m[mOffset + 8 + i] *= z;
        }
    }

    public static void scaleM(float[] sm, int smOffset, float[] m, int mOffset, float x, float y, float z) {
        for (int i = 0; i < 4; i++) {
            sm[smOffset + i] = m[mOffset + i] * x;
            sm[smOffset + 4 + i] = m[mOffset + 4 + i] * y;
            sm[smOffset + 8 + i] = m[mOffset + 8 + i] * z;
            sm[smOffset + 12 + i] = m[mOffset + 12 + i];
        }
    }

    public static void translateM(float[] m, int mOffset, float x, float y, float z) {
        for (int i = 0; i < 4; i++) {
            m[mOffset + 12 + i] += m[mOffset + i] * x + m[mOffset + 4 + i] * y + m[mOffset + 8 + i] * z;
        }
    }

    public static void translateM(float[] tm, int tmOffset, float[] m, int mOffset, float x, float y, float z) {
        for (int i = 0; i < 12; i++) tm[tmOffset + i] = m[mOffset + i];
        for (int i = 0; i < 4; i++) {
            tm[tmOffset + 12 + i] = m[mOffset + i] * x + m[mOffset + 4 + i] * y + m[mOffset + 8 + i] * z + m[mOffset + 12 + i];
        }
    }

    public static boolean invertM(float[] mInv, int mInvOffset, float[] m, int mOffset) {
        double[] a = new double[16];
        for (int i = 0; i < 16; i++) a[i] = m[mOffset + i];
        double[] inv = new double[16];
        inv[0] = a[5]*a[10]*a[15] - a[5]*a[11]*a[14] - a[9]*a[6]*a[15] + a[9]*a[7]*a[14] + a[13]*a[6]*a[11] - a[13]*a[7]*a[10];
        inv[4] = -a[4]*a[10]*a[15] + a[4]*a[11]*a[14] + a[8]*a[6]*a[15] - a[8]*a[7]*a[14] - a[12]*a[6]*a[11] + a[12]*a[7]*a[10];
        inv[8] = a[4]*a[9]*a[15] - a[4]*a[11]*a[13] - a[8]*a[5]*a[15] + a[8]*a[7]*a[13] + a[12]*a[5]*a[11] - a[12]*a[7]*a[9];
        inv[12] = -a[4]*a[9]*a[14] + a[4]*a[10]*a[13] + a[8]*a[5]*a[14] - a[8]*a[6]*a[13] - a[12]*a[5]*a[10] + a[12]*a[6]*a[9];
        inv[1] = -a[1]*a[10]*a[15] + a[1]*a[11]*a[14] + a[9]*a[2]*a[15] - a[9]*a[3]*a[14] - a[13]*a[2]*a[11] + a[13]*a[3]*a[10];
        inv[5] = a[0]*a[10]*a[15] - a[0]*a[11]*a[14] - a[8]*a[2]*a[15] + a[8]*a[3]*a[14] + a[12]*a[2]*a[11] - a[12]*a[3]*a[10];
        inv[9] = -a[0]*a[9]*a[15] + a[0]*a[11]*a[13] + a[8]*a[1]*a[15] - a[8]*a[3]*a[13] - a[12]*a[1]*a[11] + a[12]*a[3]*a[9];
        inv[13] = a[0]*a[9]*a[14] - a[0]*a[10]*a[13] - a[8]*a[1]*a[14] + a[8]*a[2]*a[13] + a[12]*a[1]*a[10] - a[12]*a[2]*a[9];
        inv[2] = a[1]*a[6]*a[15] - a[1]*a[7]*a[14] - a[5]*a[2]*a[15] + a[5]*a[3]*a[14] + a[13]*a[2]*a[7] - a[13]*a[3]*a[6];
        inv[6] = -a[0]*a[6]*a[15] + a[0]*a[7]*a[14] + a[4]*a[2]*a[15] - a[4]*a[3]*a[14] - a[12]*a[2]*a[7] + a[12]*a[3]*a[6];
        inv[10] = a[0]*a[5]*a[15] - a[0]*a[7]*a[13] - a[4]*a[1]*a[15] + a[4]*a[3]*a[13] + a[12]*a[1]*a[7] - a[12]*a[3]*a[5];
        inv[14] = -a[0]*a[5]*a[14] + a[0]*a[6]*a[13] + a[4]*a[1]*a[14] - a[4]*a[2]*a[13] - a[12]*a[1]*a[6] + a[12]*a[2]*a[5];
        inv[3] = -a[1]*a[6]*a[11] + a[1]*a[7]*a[10] + a[5]*a[2]*a[11] - a[5]*a[3]*a[10] - a[9]*a[2]*a[7] + a[9]*a[3]*a[6];
        inv[7] = a[0]*a[6]*a[11] - a[0]*a[7]*a[10] - a[4]*a[2]*a[11] + a[4]*a[3]*a[10] + a[8]*a[2]*a[7] - a[8]*a[3]*a[6];
        inv[11] = -a[0]*a[5]*a[11] + a[0]*a[7]*a[9] + a[4]*a[1]*a[11] - a[4]*a[3]*a[9] - a[8]*a[1]*a[7] + a[8]*a[3]*a[5];
        inv[15] = a[0]*a[5]*a[10] - a[0]*a[6]*a[9] - a[4]*a[1]*a[10] + a[4]*a[2]*a[9] + a[8]*a[1]*a[6] - a[8]*a[2]*a[5];
        double det = a[0]*inv[0] + a[1]*inv[4] + a[2]*inv[8] + a[3]*inv[12];
        if (det == 0) return false;
        det = 1.0 / det;
        for (int i = 0; i < 16; i++) mInv[mInvOffset + i] = (float) (inv[i] * det);
        return true;
    }
}
