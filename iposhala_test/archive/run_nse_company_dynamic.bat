@echo off
cd /d C:\Users\Dell\Desktop\Rusaka-Technologies\Iposhala\iposhala_test

call .venv\Scripts\activate

python -m iposhala_test.scripts.jobs.update_nse_company_dynamic
pause
