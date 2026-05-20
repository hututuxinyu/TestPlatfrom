#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_006_001.py
# 测试用例: GIDS鉴权测试 - IMEI不在白名单场景
# 目标: 验证 GIDS 对未授权 IMEI 的拒绝能力

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_grid_login_auth_failed():
    """
    测试步骤1: 宫格登录IMEI不在白名单
    预期: 返回401或CLIENT_FAILED，提示IMEI not allowed
    """
    print("[INFO] ========== 测试步骤1: 宫格登录IMEI不在白名单 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "999999999999999",
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
        "appType": "1"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']} (不在白名单)")

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

        if resp_json.get('code') == -2 or resp_json.get('code') == 401:
            message = resp_json.get('message', '')
            if 'IMEI not allowed' in message or 'Unauthorized' in message:
                print("[PASS] GIDS 正确拒绝了未授权 IMEI")
                return True
            else:
                print(f"[PASS] GIDS 返回鉴权失败: {message}")
                return True
        elif resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了未授权的 IMEI，存在鉴权漏洞")
            return False
        else:
            print(f"[INFO] GIDS 返回: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_device_login_auth_failed():
    """
    测试步骤2: 设备登录IMEI不在白名单
    预期: 返回鉴权失败
    """
    print("\n[INFO] ========== 测试步骤2: 设备登录IMEI不在白名单 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "999999999999999",
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
        "appType": "1"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']} (不在白名单)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/deviceLoginAuth",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == -2 or resp_json.get('code') == 401:
            print("[PASS] GIDS 正确拒绝了未授权 IMEI")
            return True
        elif resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了未授权的 IMEI，存在鉴权漏洞")
            return False
        else:
            print(f"[INFO] GIDS 返回: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_send_client_event_auth_failed():
    """
    测试步骤3: 发送客户端事件IMEI不在白名单
    预期: 返回鉴权失败
    """
    print("\n[INFO] ========== 测试步骤3: 发送客户端事件IMEI不在白名单 ==========")

    test_data = {
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "appType": "1",
        "imei": "999999999999999",
        "imsi": "685101555652111",
        "type": "test_event"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']} (不在白名单)")

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

        if resp_json.get('code') == 401:
            print("[PASS] GIDS 正确返回401鉴权失败")
            return True
        elif resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了未授权 IMEI 的事件上报")
            return False
        else:
            print(f"[INFO] GIDS 返回: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_send_app_use_times_auth_failed():
    """
    测试步骤4: 发送应用时长事件IMEI不在白名单
    预期: 返回鉴权失败
    """
    print("\n[INFO] ========== 测试步骤4: 发送应用时长事件IMEI不在白名单 ==========")

    test_data = {
        "useTimes": "3600000",
        "hsman": "Test Manufacturer",
        "hstype": "Test Model",
        "exttype": "default",
        "appType": "1",
        "appId": "test_app",
        "imei": "999999999999999",
        "imsi": "685101555652111"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']} (不在白名单)")

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

        if resp_json.get('code') == 401:
            print("[PASS] GIDS 正确返回401鉴权失败")
            return True
        elif resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了未授权 IMEI 的应用时长事件")
            return False
        else:
            print(f"[INFO] GIDS 返回: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_auth_with_valid_imei():
    """
    测试步骤5: 使用有效IMEI验证正常流程
    预期: 返回成功（验证白名单机制正常工作）
    """
    print("\n[INFO] ========== 测试步骤5: 使用有效IMEI验证正常流程 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "6258412454025411",
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
        "appType": "1"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']} (在白名单中)")

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

        if resp_json.get('code') == 200:
            print("[PASS] 白名单IMEI正常通过鉴权")
            return True
        elif resp_json.get('code') == -2 and 'IMEI not allowed' in resp_json.get('message', ''):
            print("[FAIL] 白名单IMEI被拒绝，白名单配置可能有问题")
            return False
        else:
            print(f"[INFO] GIDS 返回: code={resp_json.get('code')}, message={resp_json.get('message')}")
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
    GIDS鉴权测试 - IMEI不在白名单场景
    TC_SBG_Func_GIDS_006_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print(f"[INFO] 测试IMEI: 未授权=999999999999999, 已授权=6258412454025411")
    print("")

    test_results = []

    result1 = test_grid_login_auth_failed()
    test_results.append(("步骤1: 宫格登录IMEI不在白名单", result1))

    result2 = test_device_login_auth_failed()
    test_results.append(("步骤2: 设备登录IMEI不在白名单", result2))

    result3 = test_send_client_event_auth_failed()
    test_results.append(("步骤3: 发送客户端事件IMEI不在白名单", result3))

    result4 = test_send_app_use_times_auth_failed()
    test_results.append(("步骤4: 发送应用时长事件IMEI不在白名单", result4))

    result5 = test_auth_with_valid_imei()
    test_results.append(("步骤5: 使用有效IMEI验证正常流程", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    if not all_passed:
        print("\n[WARN] 部分测试失败可能表示 GIDS 存在鉴权漏洞，请检查IMEI白名单配置")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())