[app]
title = Трубомер
package.name = tubomer
package.domain = org.tubomer
version = 1.0.0
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json
icon.filename = icon.png
requirements = python3,kivy,speechrecognition
android.permissions = INTERNET,RECORD_AUDIO
android.api = 30
android.minapi = 21
android.ndk = 25b
fullscreen = 0
orientation = portrait

[buildozer]
log_level = 2