#!/bin/bash
# 实时监听夜神模拟器 logcat，过滤游戏网络请求 (ToUrl)
"/c/Program Files/Nox/bin/nox_adb.exe" -s 127.0.0.1:62001 logcat -v time Unity:W *:S | grep --line-buffered -A3 "ToUrl"
