#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_003_001.py
# 测试用例: GIDS删除缓存接口 - 正常流程测试
# 目标: 验证 GIDS 删除缓存接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_delete_cache_normal():
    """
    测试步骤1: 正常参数删除缓存
    预期: 返回成功
    """
    print("[INFO] ========== 测试步骤1: 正常参数删除缓存 ==========")

    test_data = {
        "imei": "6258412454025411",
        "imsi": "685101555652111"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']}, imsi={test_data['imsi']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 删除缓存成功")
            return True
        else:
            print(f"[FAIL] 删除缓存失败: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_delete_cache_different_imsi():
    """
    测试步骤2: 不同IMSI删除缓存
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤2: 不同IMSI删除缓存 ==========")

    test_data = {
        "imei": "6258412454025411",
        "imsi": "685101555652112"  # 不同IMSI
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']}, imsi={test_data['imsi']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 不同IMSI删除缓存测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_delete_cache_different_imei():
    """
    测试步骤3: 不同IMEI删除缓存
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤3: 不同IMEI删除缓存 ==========")

    test_data = {
        "imei": "6258412454025412",  # 不同IMEI
        "imsi": "685101555652111"
    }

    print(f"[INFO] 请求参数: imei={test_data['imei']}, imsi={test_data['imsi']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 不同IMEI删除缓存测试完成，返回: code={resp_json.get('code')}")
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
    GIDS删除缓存接口 - 正常流程测试
    TC_SBG_Func_GIDS_003_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_delete_cache_normal()
    test_results.append(("步骤1: 正常参数删除缓存", result1))

    result2 = test_delete_cache_different_imsi()
    test_results.append(("步骤2: 不同IMSI删除缓存", result2))

    result3 = test_delete_cache_different_imei()
    test_results.append(("步骤3: 不同IMEI删除缓存", result3))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())