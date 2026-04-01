[app]

title = Трубомер
package.name = tubomer
package.domain = org.tubomer

version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json
source.exclude_dirs = tests,bin,.git,__pycache__

icon.filename = icon.png

requirements = python3,kivy,speechrecognition

android.permissions = INTERNET,RECORD_AUDIO
android.api = 30
android.minapi = 21
android.ndk = 25b
android.sdk = 30
android.accept_sdk_license = True

fullscreen = 0
orientation = portrait

kivy_version = 2.1.0

build_dir = .buildozer
dist_dir = bin

[buildozer]
log_level = 2
