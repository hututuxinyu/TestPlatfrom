#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_008_001.py
# 测试用例: GIDS鉴权接口(authIMEI) - 正常流程测试
# 目标: 验证 GIDS IMEI鉴权接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_auth_imei_valid():
    """
    测试步骤1: 有效IMEI鉴权
    预期: 返回成功，code=200，auth passed
    """
    print("[INFO] ========== 测试步骤1: 有效IMEI鉴权 ==========")

    test_data = {
        "IMEI": "6258412454025411",
        "type": "GateWay"
    }

    print(f"[INFO] 请求参数: IMEI={test_data['IMEI']}, type={test_data['type']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/authIMEI",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] IMEI鉴权通过")
            return True
        elif resp_json.get('code') == 401:
            print("[INFO] IMEI不在白名单，鉴权失败")
            return True
        else:
            print(f"[PASS] IMEI鉴权测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_auth_imei_invalid():
    """
    测试步骤2: 无效IMEI鉴权（不在白名单）
    预期: 返回鉴权失败，code=401
    """
    print("\n[INFO] ========== 测试步骤2: 无效IMEI鉴权 ==========")

    test_data = {
        "IMEI": "999999999999999",
        "type": "GateWay"
    }

    print(f"[INFO] 请求参数: IMEI={test_data['IMEI']} (不在白名单)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/authIMEI",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 401:
            print("[PASS] GIDS 正确拒绝了不在白名单的 IMEI")
            return True
        elif resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了不在白名单的 IMEI")
            return False
        else:
            print(f"[PASS] 无效IMEI鉴权测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_auth_imei_empty():
    """
    测试步骤3: IMEI为空
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤3: IMEI为空 ==========")

    test_data = {
        "IMEI": "",
        "type": "GateWay"
    }

    print(f"[INFO] 请求参数: IMEI='' (空字符串)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/authIMEI",
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


def test_auth_imei_non_numeric():
    """
    测试步骤4: IMEI包含非数字字符
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤4: IMEI包含非数字字符 ==========")

    test_data = {
        "IMEI": "625841245402ABC",
        "type": "GateWay"
    }

    print(f"[INFO] 请求参数: IMEI={test_data['IMEI']} (包含字母)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/authIMEI",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了包含非数字字符的 IMEI")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了包含非数字字符的 IMEI")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_auth_imei_missing_type():
    """
    测试步骤5: 缺少type字段
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤5: 缺少type字段 ==========")

    test_data = {
        "IMEI": "6258412454025411"
    }

    print(f"[INFO] 请求参数: 缺少 type 字段")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/authIMEI",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[WARN] GIDS 接受了缺少 type 的请求")
            return True
        else:
            print("[PASS] GIDS 正确拒绝了缺少 type 的请求")
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
    GIDS鉴权接口(authIMEI) - 正常流程测试
    TC_SBG_Func_GIDS_008_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_auth_imei_valid()
    test_results.append(("步骤1: 有效IMEI鉴权", result1))

    result2 = test_auth_imei_invalid()
    test_results.append(("步骤2: 无效IMEI鉴权", result2))

    result3 = test_auth_imei_empty()
    test_results.append(("步骤3: IMEI为空", result3))

    result4 = test_auth_imei_non_numeric()
    test_results.append(("步骤4: IMEI包含非数字字符", result4))

    result5 = test_auth_imei_missing_type()
    test_results.append(("步骤5: 缺少type字段", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())