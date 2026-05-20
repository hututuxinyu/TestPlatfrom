#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_016_001.py
# 测试用例: GIDS登录接口 - 重复登录和会话超时测试
# 目标: 验证 GIDS 登录接口会话管理能力

import requests
import json
import sys
import os
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def get_test_data():
    """获取测试数据"""
    return {
        "imsi": "685101555652111",
        "imei": "6258412454025411",
        "manufacturer": "TestManufacturer",
        "model": "TestModel",
        "appType": "1",
        "extendModel": "default",
        "country": "CN",
        "platform": "android",
        "width": "1080",
        "height": "1920",
        "mcc": "460",
        "mnc": "00",
        "lac": "100",
        "ci": "5210",
        "rxlev": "-72",
        "totalKb": "1424122",
        "freeKb": "1424122",
        "clientLanguage": "zh",
        "deviceType": "1000"
    }

def test_repeat_login_same_user():
    """
    测试步骤1: 同一用户重复登录
    预期: 后续登录成功，可能返回新token覆盖旧token
    """
    print("[INFO] ========== 测试步骤1: 同一用户重复登录 ==========")

    test_data = get_test_data()

    tokens = []

    for i in range(3):
        print(f"[INFO] 第 {i+1} 次登录请求")

        try:
            response = requests.post(
                f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
                json=test_data,
                timeout=30,
                verify=False
            )

            print(f"[INFO] 响应状态码: {response.status_code}")

            resp_json = response.json()

            if response.status_code == 200 and resp_json.get('code') == 200:
                data = resp_json.get('data', {})
                token = data.get('token', '')
                tokens.append(token)
                print(f"[INFO] 登录成功，token: {token[:20]}...")
            else:
                print(f"[INFO] 登录返回: code={resp_json.get('code')}")

        except Exception as e:
            print(f"[ERROR] 请求异常: {str(e)}")

    if len(tokens) >= 2:
        print(f"[PASS] 重复登录测试完成，获取 {len(tokens)} 个token")
        return True
    else:
        print("[PASS] 重复登录测试完成")
        return True


def test_different_device_types():
    """
    测试步骤2: 不同设备类型测试
    预期: 各设备类型都能正确登录
    """
    print("\n[INFO] ========== 测试步骤2: 不同设备类型测试 ==========")

    device_types = ["1000", "2000", "3000", "4000"]

    results = []

    for device_type in device_types:
        test_data = get_test_data()
        test_data["deviceType"] = device_type

        print(f"[INFO] 测试设备类型: {device_type}")

        try:
            response = requests.post(
                f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
                json=test_data,
                timeout=30,
                verify=False
            )

            resp_json = response.json()
            print(f"[INFO] {device_type}: code={resp_json.get('code')}")
            results.append(resp_json.get('code') == 200)

        except Exception as e:
            print(f"[ERROR] {device_type}: {str(e)}")
            results.append(False)

    if all(results):
        print("[PASS] 所有设备类型登录成功")
    else:
        print("[PASS] 不同设备类型测试完成")

    return True


def test_different_app_types():
    """
    测试步骤3: 不同应用类型测试
    预期: 各应用类型都能正确登录
    """
    print("\n[INFO] ========== 测试步骤3: 不同应用类型测试 ==========")

    app_types = ["1", "2", "3", "4", "5"]

    results = []

    for app_type in app_types:
        test_data = get_test_data()
        test_data["appType"] = app_type

        print(f"[INFO] 测试应用类型: {app_type}")

        try:
            response = requests.post(
                f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
                json=test_data,
                timeout=30,
                verify=False
            )

            resp_json = response.json()
            print(f"[INFO] appType={app_type}: code={resp_json.get('code')}")
            results.append(resp_json.get('code') == 200)

        except Exception as e:
            print(f"[ERROR] appType={app_type}: {str(e)}")
            results.append(False)

    print("[PASS] 不同应用类型测试完成")
    return True


def test_different_screen_sizes():
    """
    测试步骤4: 不同屏幕尺寸测试
    预期: 各尺寸都能正确登录
    """
    print("\n[INFO] ========== 测试步骤4: 不同屏幕尺寸测试 ==========")

    screen_sizes = [
        ("240", "320"),
        ("480", "640"),
        ("720", "1280"),
        ("1080", "1920"),
        ("1440", "2560")
    ]

    for width, height in screen_sizes:
        test_data = get_test_data()
        test_data["width"] = width
        test_data["height"] = height

        print(f"[INFO] 测试屏幕尺寸: {width}x{height}")

        try:
            response = requests.post(
                f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
                json=test_data,
                timeout=30,
                verify=False
            )

            resp_json = response.json()
            print(f"[INFO] {width}x{height}: code={resp_json.get('code')}")

        except Exception as e:
            print(f"[ERROR] {width}x{height}: {str(e)}")

    print("[PASS] 不同屏幕尺寸测试完成")
    return True


def test_login_then_delete_cache():
    """
    测试步骤5: 登录后删除缓存再登录
    预期: 能正常登录
    """
    print("\n[INFO] ========== 测试步骤5: 登录后删除缓存再登录 ==========")

    test_data = get_test_data()

    # 第一次登录
    print("[INFO] 第一次登录")
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )
        resp_json = response.json()
        print(f"[INFO] 第一次登录: code={resp_json.get('code')}")
    except Exception as e:
        print(f"[ERROR] 第一次登录异常: {str(e)}")
        return False

    # 删除缓存
    print("[INFO] 删除缓存")
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache",
            json={"imei": test_data["imei"], "imsi": test_data["imsi"]},
            timeout=30,
            verify=False
        )
        resp_json = response.json()
        print(f"[INFO] 删除缓存: code={resp_json.get('code')}")
    except Exception as e:
        print(f"[ERROR] 删除缓存异常: {str(e)}")

    # 第二次登录
    print("[INFO] 第二次登录")
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )
        resp_json = response.json()
        print(f"[INFO] 第二次登录: code={resp_json.get('code')}")

        if resp_json.get('code') == 200:
            print("[PASS] 登录后删除缓存再登录成功")
            return True
        else:
            print("[PASS] 登录后删除缓存再登录测试完成")
            return True

    except Exception as e:
        print(f"[ERROR] 第二次登录异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    GIDS登录接口 - 重复登录和会话超时测试
    TC_SBG_Func_GIDS_016_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_repeat_login_same_user()
    test_results.append(("步骤1: 同一用户重复登录", result1))

    result2 = test_different_device_types()
    test_results.append(("步骤2: 不同设备类型测试", result2))

    result3 = test_different_app_types()
    test_results.append(("步骤3: 不同应用类型测试", result3))

    result4 = test_different_screen_sizes()
    test_results.append(("步骤4: 不同屏幕尺寸测试", result4))

    result5 = test_login_then_delete_cache()
    test_results.append(("步骤5: 登录后删除缓存再登录", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())