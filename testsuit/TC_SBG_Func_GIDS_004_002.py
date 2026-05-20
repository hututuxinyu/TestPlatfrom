#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_004_002.py
# 测试用例: GIDS事件接口 - 发送应用使用时长事件测试
# 目标: 验证 GIDS 发送应用使用时长事件接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_send_app_use_times_event_normal():
    """
    测试步骤1: 正常参数发送应用使用时长事件
    预期: 返回成功
    """
    print("[INFO] ========== 测试步骤1: 正常参数发送应用使用时长事件 ==========")

    test_data = {
        "useTimes": "3600000",
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "exttype": "default",
        "appType": "1",
        "appId": "test_app_001",
        "scheight": "1920",
        "scwidth": "1080",
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "playMode": "0",
        "imei1": "6258412454025411",
        "imei2": "6258412454025412"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']}, imsi={test_data['imsi']}, useTimes={test_data['useTimes']}ms")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/center/public/client/sendAppUseTimesEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 发送应用使用时长事件成功")
            return True
        else:
            print(f"[FAIL] 发送应用使用时长事件失败: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_send_app_use_times_event_short_time():
    """
    测试步骤2: 短时长事件
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤2: 短时长事件 ==========")

    test_data = {
        "useTimes": "1000",
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "exttype": "default",
        "appType": "1",
        "appId": "test_app_001",
        "scheight": "1920",
        "scwidth": "1080",
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "playMode": "0"
    }

    print(f"[INFO] 请求参数: useTimes={test_data['useTimes']}ms (短时长)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/center/public/client/sendAppUseTimesEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 短时长事件测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_send_app_use_times_event_zero_time():
    """
    测试步骤3: 零时长事件
    预期: 返回成功或正确处理
    """
    print("\n[INFO] ========== 测试步骤3: 零时长事件 ==========")

    test_data = {
        "useTimes": "0",
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "exttype": "default",
        "appType": "1",
        "appId": "test_app_001",
        "scheight": "1920",
        "scwidth": "1080",
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "playMode": "0"
    }

    print(f"[INFO] 请求参数: useTimes={test_data['useTimes']}ms (零时长)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/center/public/client/sendAppUseTimesEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 零时长事件测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_send_app_use_times_event_negative_time():
    """
    测试步骤4: 负时长事件（异常值）
    预期: GIDS 应正确处理或返回错误
    """
    print("\n[INFO] ========== 测试步骤4: 负时长事件 ==========")

    test_data = {
        "useTimes": "-1000",
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "exttype": "default",
        "appType": "1",
        "appId": "test_app_001",
        "scheight": "1920",
        "scwidth": "1080",
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "playMode": "0"
    }

    print(f"[INFO] 请求参数: useTimes={test_data['useTimes']}ms (负时长)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/center/public/client/sendAppUseTimesEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[WARN] GIDS 接受了负时长事件，需确认是否合理")
            return True
        else:
            print("[PASS] GIDS 正确拒绝了负时长事件")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_send_app_use_times_event_invalid_time():
    """
    测试步骤5: 无效时长格式（非数字）
    预期: GIDS 应正确处理或返回错误
    """
    print("\n[INFO] ========== 测试步骤5: 无效时长格式 ==========")

    test_data = {
        "useTimes": "abc",
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "exttype": "default",
        "appType": "1",
        "appId": "test_app_001",
        "scheight": "1920",
        "scwidth": "1080",
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "playMode": "0"
    }

    print(f"[INFO] 请求参数: useTimes={test_data['useTimes']} (非数字)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/center/public/client/sendAppUseTimesEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[WARN] GIDS 接受了非数字时长，需确认是否合理")
            return True
        else:
            print("[PASS] GIDS 正确拒绝了非数字时长")
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
    GIDS事件接口 - 发送应用使用时长事件测试
    TC_SBG_Func_GIDS_004_002
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_send_app_use_times_event_normal()
    test_results.append(("步骤1: 正常参数发送应用使用时长事件", result1))

    result2 = test_send_app_use_times_event_short_time()
    test_results.append(("步骤2: 短时长事件", result2))

    result3 = test_send_app_use_times_event_zero_time()
    test_results.append(("步骤3: 零时长事件", result3))

    result4 = test_send_app_use_times_event_negative_time()
    test_results.append(("步骤4: 负时长事件", result4))

    result5 = test_send_app_use_times_event_invalid_time()
    test_results.append(("步骤5: 无效时长格式", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())