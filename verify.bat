@echo off

echo ## PEP 8 Verification ##
echo.

python pep8.py --ignore=E501,W293 appfoogle %*