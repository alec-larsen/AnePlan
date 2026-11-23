@echo off

python -m nuitka --onefile --windows-icon-from-ico=assets/AnePlanL.ico --windows-console-mode=disable --enable-plugin=tk-inter --include-data-files=aneplan_setup.sql=aneplan_setup.sql --include-data-files=assets/AnePlanL.ico=assets/AnePlanL.ico main.py

pause
