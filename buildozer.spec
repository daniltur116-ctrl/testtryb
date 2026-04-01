[app]

title = Трубомер
package.name = tubomer
package.domain = org.tubomer

version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json
source.exclude_dirs = tests,bin,.git,__pycache__

icon.filename = icon.png

# Убираем speechrecognition, оставляем только kivy и cython
requirements = python3==3.9.7,kivy==2.1.0,cython==0.29.36

android.permissions = INTERNET,RECORD_AUDIO
android.api = 30
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

fullscreen = 0
orientation = portrait

kivy_version = 2.1.0

build_dir = .buildozer
dist_dir = bin

[buildozer]
log_level = 2
