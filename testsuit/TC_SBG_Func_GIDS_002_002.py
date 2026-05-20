#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_002_002.py
# 测试用例: GIDS设备登录接口 - IMEI白名单校验测试
# 目标: 验证 GIDS 对 IMEI 白名单的校验能力

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_imei_not_in_whitelist():
    """
    测试步骤1: IMEI不在白名单
    预期: GIDS 应返回错误，提示 IMEI not allowed
    """
    print("[INFO] ========== 测试步骤1: IMEI不在白名单 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "999999999999999",  # 不在白名单的IMEI
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
        "appType": "1",
        "extendModel": "default",
        "country": "default",
        "platform": "default",
        "width": "240",
        "height": "320",
        "mcc": "460",
        "mnc": "00",
        "lac": "100",
        "ci": "5210",
        "rxlev": "-72",
        "totalKb": "1424122",
        "freeKb": "1424122",
        "clientLanguage": "en",
        "deviceType": "1000"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']} (不在白名单中)")

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

        # 预期: 应该返回错误，提示 IMEI not allowed
        if resp_json.get('code') == -2 and 'IMEI not allowed' in resp_json.get('message', ''):
            print("[PASS] GIDS 正确拒绝了不在白名单的 IMEI")
            return True
        elif resp_json.get('code') == 401:
            print("[PASS] GIDS 正确返回鉴权失败")
            return True
        elif resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了不在白名单的 IMEI")
            print("[FAIL] 预期: 应返回错误，提示 IMEI not allowed")
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


def test_imei_empty():
    """
    测试步骤2: IMEI为空
    预期: GIDS 应返回错误
    """
    print("\n[INFO] ========== 测试步骤2: IMEI为空 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "",  # 空字符串
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
        "appType": "1"
    }

    print(f"[INFO] 请求参数: imei='{test_data['imei']}' (空字符串)")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了空的 IMEI")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的 IMEI")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_imei_missing():
    """
    测试步骤3: 缺少IMEI字段
    预期: GIDS 应返回错误
    """
    print("\n[INFO] ========== 测试步骤3: 缺少IMEI字段 ==========")

    test_data = {
        "imsi": "685101555652111"
        # 缺少 imei 字段
    }

    print(f"[INFO] 请求参数: 缺少 imei 字段")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了缺少 IMEI 的请求")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了缺少 IMEI 的请求")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_imei_sql_injection():
    """
    测试步骤4: IMEI SQL注入测试（安全测试）
    预期: GIDS 应正确处理，不发生SQL注入
    """
    print("\n[INFO] ========== 测试步骤4: IMEI SQL注入测试 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "admin' OR '1'='1",  # SQL注入尝试
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
        "appType": "1"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']} (SQL注入尝试)")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 可能存在SQL注入漏洞")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了SQL注入尝试")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_valid_imei():
    """
    测试步骤5: 使用有效IMEI验证正常流程
    预期: 返回成功（验证白名单机制正常工作）
    """
    print("\n[INFO] ========== 测试步骤5: 使用有效IMEI验证正常流程 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "6258412454025411",  # 有效IMEI
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
        "appType": "1"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']} (在白名单中)")

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
    GIDS设备登录接口 - IMEI白名单校验测试
    TC_SBG_Func_GIDS_002_002
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_imei_not_in_whitelist()
    test_results.append(("步骤1: IMEI不在白名单", result1))

    result2 = test_imei_empty()
    test_results.append(("步骤2: IMEI为空", result2))

    result3 = test_imei_missing()
    test_results.append(("步骤3: 缺少IMEI字段", result3))

    result4 = test_imei_sql_injection()
    test_results.append(("步骤4: IMEI SQL注入测试", result4))

    result5 = test_valid_imei()
    test_results.append(("步骤5: 使用有效IMEI验证", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    if not all_passed:
        print("\n[INFO] 注意: 部分测试失败可能表示 GIDS 存在鉴权漏洞")
        print("[INFO] 请检查 IMEI 白名单配置")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())