python -m nuitka --standalone --mingw64 ^
--show-memory --show-progress ^
--nofollow-imports --follow-import-to=src ^
--include-data-dir=resource=resource ^
--windows-icon-from-ico=resource/ic_launcher.ico ^
--output-dir=output ^
app.py