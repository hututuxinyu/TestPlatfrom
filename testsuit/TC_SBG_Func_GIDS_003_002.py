#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_003_002.py
# 测试用例: GIDS删除缓存接口 - 参数校验测试
# 目标: 验证 GIDS 删除缓存接口参数校验能力

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_delete_cache_imei_empty():
    """
    测试步骤1: IMEI为空
    预期: GIDS 应返回错误，提示 IMEI 不能为空
    """
    print("[INFO] ========== 测试步骤1: IMEI为空 ==========")

    test_data = {
        "imei": "",  # 空字符串
        "imsi": "685101555652111"
    }

    print(f"[INFO] 请求参数: imei='{test_data['imei']}' (空字符串)")

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


def test_delete_cache_imsi_empty():
    """
    测试步骤2: IMSI为空
    预期: GIDS 应返回错误，提示 IMSI 不能为空
    """
    print("\n[INFO] ========== 测试步骤2: IMSI为空 ==========")

    test_data = {
        "imei": "6258412454025411",
        "imsi": ""  # 空字符串
    }

    print(f"[INFO] 请求参数: imsi='{test_data['imsi']}' (空字符串)")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了空的 IMSI")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的 IMSI")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_delete_cache_imei_missing():
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
            f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache",
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


def test_delete_cache_imsi_missing():
    """
    测试步骤4: 缺少IMSI字段
    预期: GIDS 应返回错误
    """
    print("\n[INFO] ========== 测试步骤4: 缺少IMSI字段 ==========")

    test_data = {
        "imei": "6258412454025411"
        # 缺少 imsi 字段
    }

    print(f"[INFO] 请求参数: 缺少 imsi 字段")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了缺少 IMSI 的请求")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了缺少 IMSI 的请求")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_delete_cache_empty_body():
    """
    测试步骤5: 空请求体
    预期: GIDS 应返回错误
    """
    print("\n[INFO] ========== 测试步骤5: 空请求体 ==========")

    test_data = {}

    print(f"[INFO] 请求参数: 空请求体")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了空请求体")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空请求体")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_valid_params():
    """
    测试步骤6: 正常参数（验证正常流程仍然有效）
    """
    print("\n[INFO] ========== 测试步骤6: 正常参数验证 ==========")

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
            print("[PASS] 正常参数请求成功")
            return True
        else:
            print("[FAIL] 正常参数请求失败")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    GIDS删除缓存接口 - 参数校验测试
    TC_SBG_Func_GIDS_003_002
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_delete_cache_imei_empty()
    test_results.append(("步骤1: IMEI为空", result1))

    result2 = test_delete_cache_imsi_empty()
    test_results.append(("步骤2: IMSI为空", result2))

    result3 = test_delete_cache_imei_missing()
    test_results.append(("步骤3: 缺少IMEI字段", result3))

    result4 = test_delete_cache_imsi_missing()
    test_results.append(("步骤4: 缺少IMSI字段", result4))

    result5 = test_delete_cache_empty_body()
    test_results.append(("步骤5: 空请求体", result5))

    result6 = test_valid_params()
    test_results.append(("步骤6: 正常参数", result6))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    if not all_passed:
        print("\n[INFO] 注意: 如果前5个测试失败，说明 GIDS 存在参数校验缺陷")
        print("[INFO] 需要修复 GIDS 的 deleteCache 接口")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())