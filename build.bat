python -m nuitka --standalone --mingw64 ^
--show-memory --show-progress ^
--nofollow-imports --follow-import-to=src ^
--include-data-dir=resource=resource ^
--windows-icon-from-ico=resource/ic_launcher.ico ^
--windows-company-name=Celetor ^
--windows-product-name=mmread-download ^
--windows-file-version=1.5.0.0 ^
--windows-product-version=1.5.0.0 ^
--windows-file-description="微信读书epub下载工具" ^
--output-dir=output ^
app.py