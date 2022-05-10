@echo off

set TESTDIR=.test
set TEST_SCRIPTS=test_scripts

call:test_script test1.py 42
call:test_script test2.py 1
call:test_script test3.py 3
call:test_script test4.py 42
call:test_script test5.py 42
call:test_script test6.py 42
call:test_script test7.py 42
call:test_script test8.py 42
call:test_script test9.py 42
call:test_script test10.py 42
call:test_script test11.py 42
call:test_script test12.py 144
call:test_script test13.py 0
call:test_script test14.py 0
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
call:testcase "3+2;return 1" 1
call:testcase "a=4;return a" 4
call:testcase "hoge=4;return hoge" 4
call:testcase "hoge=4;hoge=hoge+1;return hoge" 5
call:testcase "hoge=4;fuga=hoge+1;return fuga" 5


exit /b 0

:testcase
mkdir %TESTDIR%

set TEMP_FILE=%TESTDIR%\test.py

echo %~1 > %TEMP_FILE%

python py2c/py2c.py %TEMP_FILE% --template > %TESTDIR%\test.cpp
clang++ %TESTDIR%\test.cpp -o %TESTDIR%\test.exe
%TESTDIR%\test.exe
set ret=%errorlevel%
if %ret% == %2 (
    echo [ PASS ] input %1, expected %2, get %ret%
) else (
    echo [FAILED] input %1, expected %2, get %ret%
)

rm -rf %TESTDIR%
exit /b

:test_script
mkdir %TESTDIR%

python py2c/py2c.py %TEST_SCRIPTS%\%1 > %TESTDIR%\test.cpp
clang++ -std=c++20 %TESTDIR%\test.cpp -o %TESTDIR%\test.exe
%TESTDIR%\test.exe
set ret=%errorlevel%
if %ret% == %2 (
    echo [ PASS ] input %1, expected %2, get %ret%
) else (
    echo [FAILED] input %1, expected %2, get %ret%
)

rm -rf %TESTDIR%
exit /b
