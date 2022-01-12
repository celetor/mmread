python -m nuitka --standalone --mingw64 ^
--show-memory --show-progress ^
--nofollow-imports --follow-import-to=src ^
--include-data-dir=resource=resource ^
--windows-icon-from-ico=resource/ic_launcher.ico ^
--plugin-enable=qt-plugins ^
--include-qt-plugins=sensible,styles ^
--windows-company-name="Github Celeter" ^
--windows-product-name=mmread-download ^
--windows-file-version=1.6.0.0 ^
--windows-product-version=1.6.0.0 ^
--windows-file-description="微信读书下载工具" ^
--output-dir=output ^
--windows-disable-console ^
app.py