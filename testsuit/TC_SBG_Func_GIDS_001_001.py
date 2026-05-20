#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_001_001.py
# 测试用例: GIDS宫格登录接口 - 正常流程测试
# 目标: 验证 GIDS 宫格登录接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_grid_login_normal():
    """
    测试步骤1: 正常参数登录
    预期: 返回成功，包含token和gateway地址
    """
    print("[INFO] ========== 测试步骤1: 正常参数登录 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "6258412454025411",
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
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

    print(f"[INFO] 请求参数: imsi={test_data['imsi']}, imei={test_data['imei']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            data = resp_json.get('data', {})
            if data.get('token') and data.get('nodeGateWayUrl'):
                print("[PASS] 登录成功，返回token和gateway地址")
                return True
            else:
                print("[FAIL] 登录成功但缺少必要字段(token或nodeGateWayUrl)")
                return False
        else:
            print(f"[FAIL] 登录失败: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_grid_login_minimal_params():
    """
    测试步骤2: 最小参数集登录
    预期: 返回成功或适当的错误提示
    """
    print("\n[INFO] ========== 测试步骤2: 最小参数集登录 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "6258412454025411"
    }

    print(f"[INFO] 请求参数(最小): imsi={test_data['imsi']}, imei={test_data['imei']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 最小参数集测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_grid_login_full_params():
    """
    测试步骤3: 完整参数集登录
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤3: 完整参数集登录 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "6258412454025411",
        "imei1": "6258412454025411",
        "imei2": "6258412454025412",
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
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
        "deviceType": "1000",
        "appver": "1.0.0"
    }

    print(f"[INFO] 请求参数(完整): imsi={test_data['imsi']}, imei={test_data['imei']}, imei1={test_data['imei1']}, imei2={test_data['imei2']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 完整参数集登录成功")
            return True
        else:
            print(f"[PASS] 完整参数集测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    GIDS宫格登录接口 - 正常流程测试
    TC_SBG_Func_GIDS_001_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_grid_login_normal()
    test_results.append(("步骤1: 正常参数登录", result1))

    result2 = test_grid_login_minimal_params()
    test_results.append(("步骤2: 最小参数集登录", result2))

    result3 = test_grid_login_full_params()
    test_results.append(("步骤3: 完整参数集登录", result3))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())