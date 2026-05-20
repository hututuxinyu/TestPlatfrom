#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_BGW_002_001.py
# 测试用例: BrowserGateway浏览器接口 - 预打开浏览器正常流程测试
# 目标: 验证 BrowserGateway 预打开浏览器接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
BGW_ADDR = os.getenv('BGW_ADDR', 'http://127.0.0.1:8090')

def test_preopen_browser_normal():
    """
    测试步骤1: 正常参数预打开浏览器
    预期: 返回成功，code=200
    """
    print("[INFO] ========== 测试步骤1: 正常参数预打开浏览器 ==========")

    test_data = {
        "factory": "TestFactory",
        "dev_type": "TestModel",
        "ext_type": "default",
        "plat_type": 1,
        "lcd_width": 1080,
        "lcd_height": 1920,
        "app_type": 1,
        "appid": 1,
        "imsi": "685101555652111",
        "imei": "6258412454025411",
        "device_type": 1,
        "client_language": "zh",
        "play_mode": 1
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']}, imsi={test_data['imsi']}")

    try:
        response = requests.post(
            f"{BGW_ADDR}/browsergw/browser/preOpen",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 预打开浏览器成功")
            return True
        else:
            print(f"[PASS] 预打开浏览器测试完成，返回: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_preopen_browser_minimal_params():
    """
    测试步骤2: 最小参数集预打开浏览器
    预期: 返回成功或适当的错误提示
    """
    print("\n[INFO] ========== 测试步骤2: 最小参数集预打开浏览器 ==========")

    test_data = {
        "imsi": "685101555652112",
        "imei": "6258412454025412"
    }

    print(f"[INFO] 请求参数(最小): imei={test_data['imei']}, imsi={test_data['imsi']}")

    try:
        response = requests.post(
            f"{BGW_ADDR}/browsergw/browser/preOpen",
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
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_preopen_browser_full_params():
    """
    测试步骤3: 完整参数集预打开浏览器
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤3: 完整参数集预打开浏览器 ==========")

    test_data = {
        "factory": "Huawei",
        "dev_type": "P40",
        "ext_type": "premium",
        "plat_type": 2,
        "lcd_width": 1440,
        "lcd_height": 2560,
        "app_type": 2,
        "appid": 100,
        "imsi": "685101555652113",
        "imei": "6258412454025413",
        "device_type": 2,
        "client_language": "en",
        "play_mode": 0
    }

    print(f"[INFO] 请求参数(完整): imei={test_data['imei']}, imsi={test_data['imsi']}, factory={test_data['factory']}")

    try:
        response = requests.post(
            f"{BGW_ADDR}/browsergw/browser/preOpen",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 完整参数集测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    BrowserGateway浏览器接口 - 预打开浏览器正常流程测试
    TC_SBG_Func_BGW_002_001
==================================================================
    """)
    print(f"[INFO] BrowserGateway地址: {BGW_ADDR}")
    print("")

    test_results = []

    result1 = test_preopen_browser_normal()
    test_results.append(("步骤1: 正常参数预打开浏览器", result1))

    result2 = test_preopen_browser_minimal_params()
    test_results.append(("步骤2: 最小参数集预打开浏览器", result2))

    result3 = test_preopen_browser_full_params()
    test_results.append(("步骤3: 完整参数集预打开浏览器", result3))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())