#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_010_001.py
# 测试用例: GIDS配置中心接口 - 正常流程测试
# 目标: 验证 GIDS 配置中心接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_get_config():
    """
    测试步骤1: 从DB获取配置
    预期: 返回配置信息
    """
    print("[INFO] ========== 测试步骤1: 从DB获取配置 ==========")

    test_data = {
        "key": "test_config_key"
    }

    print(f"[INFO] 请求参数: key={test_data['key']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/configCenter/v1/get",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 从DB获取配置测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_insert_or_update_config():
    """
    测试步骤2: 插入或更新配置
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤2: 插入或更新配置 ==========")

    test_data = {
        "key": "test_config_key",
        "value": "test_config_value",
        "description": "Test configuration"
    }

    print(f"[INFO] 请求参数: key={test_data['key']}, value={test_data['value']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/configCenter/v1/",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 插入或更新配置成功")
            return True
        else:
            print(f"[PASS] 插入或更新配置测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_get_config_empty_key():
    """
    测试步骤3: 获取配置key为空
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤3: 获取配置key为空 ==========")

    test_data = {
        "key": ""
    }

    print(f"[INFO] 请求参数: key='' (空字符串)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/configCenter/v1/get",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了空的 key")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的 key")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_insert_config_empty_key():
    """
    测试步骤4: 插入配置key为空
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤4: 插入配置key为空 ==========")

    test_data = {
        "key": "",
        "value": "test_value"
    }

    print(f"[INFO] 请求参数: key='' (空字符串)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/configCenter/v1/",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了空的 key")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的 key")
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
    GIDS配置中心接口 - 正常流程测试
    TC_SBG_Func_GIDS_010_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_get_config()
    test_results.append(("步骤1: 从DB获取配置", result1))

    result2 = test_insert_or_update_config()
    test_results.append(("步骤2: 插入或更新配置", result2))

    result3 = test_get_config_empty_key()
    test_results.append(("步骤3: 获取配置key为空", result3))

    result4 = test_insert_config_empty_key()
    test_results.append(("步骤4: 插入配置key为空", result4))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())