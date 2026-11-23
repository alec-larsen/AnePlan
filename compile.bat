@echo off

python -m nuitka --onefile --windows-console-mode=disable --enable-plugin=tk-inter --include-data-files=aneplan_setup.sql=aneplan_setup.sql main.py

pause
