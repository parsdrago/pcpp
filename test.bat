@echo off

set TESTDIR=.test

call:testcase "return 12" 12
call:testcase "return 42" 42
call:testcase "return 1+2" 3
call:testcase "return 1 + 2" 3
call:testcase "return 3-1" 2
call:testcase "return 3*2" 6
call:testcase "return 3//2" 1
call:testcase "return 5-2*2" 1
call:testcase "return 3+4//2" 5
call:testcase "return (5-2)*2" 6
call:testcase "return 3 if 1 == 1 else 5" 3
call:testcase "return 4 if(1==2)else 1" 1
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
