#!/usr/bin/env bash
# Fetch a JDK 17 and the FTC SDK + android.jar into .cache/javac, then print the
# env vars test_javac.py needs. Usage: eval "$(scripts/javac-env.sh [sdk-version])"
set -euo pipefail
SDK="${1:-11.2.0}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)/.cache/javac"
mkdir -p "$ROOT/sdk-$SDK"
cd "$ROOT"
if ! ls jdk-17*/bin/javac >/dev/null 2>&1; then
  curl -sfL -o jdk.tar.gz 'https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse' >&2
  tar xzf jdk.tar.gz && rm jdk.tar.gz
fi
[ -f android.jar ] || curl -sfL -o android.jar https://repo1.maven.org/maven2/com/google/android/android/4.1.1.4/android-4.1.1.4.jar
CP="$ROOT/android.jar"
for a in RobotCore Hardware FtcCommon OnBotJava RobotServer Blocks Inspection Vision; do
  jar="$ROOT/sdk-$SDK/$a.jar"
  if [ ! -f "$jar" ]; then
    curl -sfL -o "$ROOT/sdk-$SDK/$a.aar" "https://repo1.maven.org/maven2/org/firstinspires/ftc/$a/$SDK/$a-$SDK.aar"
    unzip -p "$ROOT/sdk-$SDK/$a.aar" classes.jar > "$jar" && rm "$ROOT/sdk-$SDK/$a.aar"
  fi
  CP="$CP:$jar"
done
echo "export PYFTC_JAVAC='$(ls -d "$ROOT"/jdk-17*/bin/javac | head -1)'"
echo "export PYFTC_SDK_CLASSPATH='$CP'"
