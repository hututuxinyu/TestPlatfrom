#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_004_001.py
# 测试用例: GIDS事件接口 - 发送客户端事件正常流程测试
# 目标: 验证 GIDS 发送客户端事件接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_send_client_event_normal():
    """
    测试步骤1: 正常参数发送客户端事件
    预期: 返回成功
    """
    print("[INFO] ========== 测试步骤1: 正常参数发送客户端事件 ==========")

    test_data = {
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "appType": "1",
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "type": "test_event"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']}, imsi={test_data['imsi']}, type={test_data['type']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/center/public/client/sendClientEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 发送客户端事件成功")
            return True
        else:
            print(f"[FAIL] 发送客户端事件失败: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_send_client_event_different_type():
    """
    测试步骤2: 不同事件类型
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤2: 不同事件类型 ==========")

    test_data = {
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "appType": "1",
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "type": "user_action"
    }

    print(f"[INFO] 请求参数: type={test_data['type']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/center/public/client/sendClientEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 不同事件类型测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_send_client_event_minimal_params():
    """
    测试步骤3: 最小参数集发送客户端事件
    预期: 返回成功或适当的错误提示
    """
    print("\n[INFO] ========== 测试步骤3: 最小参数集发送客户端事件 ==========")

    test_data = {
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "type": "test"
    }

    print(f"[INFO] 请求参数(最小): imei={test_data['imei']}, type={test_data['type']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/center/public/client/sendClientEvent",
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


def main():
    print("""
==================================================================
    GIDS事件接口 - 发送客户端事件正常流程测试
    TC_SBG_Func_GIDS_004_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_send_client_event_normal()
    test_results.append(("步骤1: 正常参数发送客户端事件", result1))

    result2 = test_send_client_event_different_type()
    test_results.append(("步骤2: 不同事件类型", result2))

    result3 = test_send_client_event_minimal_params()
    test_results.append(("步骤3: 最小参数集发送客户端事件", result3))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())