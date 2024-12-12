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

android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.gradle_dependencies = org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.3.50

[buildozer]
log_level = 2
warn_on_root = 1
