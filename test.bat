@echo off

set TESTDIR=.test

call:testcase 12 12
call:testcase 42 42
call:testcase 1+2 3
call:testcase "1 + 2" 3
call:testcase "3-1" 2
call:testcase "3*2" 6
call:testcase "3//2" 1
exit /b 0

:testcase
mkdir %TESTDIR%

python py2c/py2c.py %1 > %TESTDIR%\test.c
clang %TESTDIR%\test.c -o %TESTDIR%\test.exe
%TESTDIR%\test.exe
set ret=%errorlevel%
if %ret% == %2 (
    echo [ PASS ] input %1, expected %2, get %ret%
) else (
    echo [FAILED] input %1, expected %2, get %ret%
)

rm -rf %TESTDIR%
exit /b
