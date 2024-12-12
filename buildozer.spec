[app]
title = Bierwiegen
package.name = bierwiegen
package.domain = org.bierwiegen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy==2.1.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

# Aktualisierte Android-Konfiguration
android.api = 33
android.minapi = 21
android.ndk = r25b
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.build_tools = 33.0.0
android.gradle_dependencies = org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.8.0

[buildozer]
log_level = 2
warn_on_root = 1
