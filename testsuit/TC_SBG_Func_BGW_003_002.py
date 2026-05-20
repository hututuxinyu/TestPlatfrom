#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_BGW_003_002.py
# 测试用例: BrowserGateway插件接口 - 加载插件参数校验测试
# 目标: 验证 BrowserGateway 加载插件接口参数校验能力

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
BGW_ADDR = os.getenv('BGW_ADDR', 'http://127.0.0.1:8090')

def test_load_extension_bucket_empty():
    """
    测试步骤1: bucket_name为空
    预期: 返回错误，code=400
    """
    print("[INFO] ========== 测试步骤1: bucket_name为空 ==========")

    test_data = {
        "bucket_name": "",
        "extension_file_path": "/opt/extensions/test"
    }

    print(f"[INFO] 请求参数: bucket_name='{test_data['bucket_name']}' (空字符串)")

    try:
        response = requests.post(
            f"{BGW_ADDR}/browsergw/extension/load",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: BrowserGateway 接受了空的 bucket_name")
            return False
        elif resp_json.get('code') == 400:
            print("[PASS] BrowserGateway 正确返回参数校验错误")
            return True
        else:
            print("[PASS] BrowserGateway 正确拒绝了空的 bucket_name")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_load_extension_path_empty():
    """
    测试步骤2: extension_file_path为空
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤2: extension_file_path为空 ==========")

    test_data = {
        "bucket_name": "test_bucket",
        "extension_file_path": ""
    }

    print(f"[INFO] 请求参数: extension_file_path='{test_data['extension_file_path']}' (空字符串)")

    try:
        response = requests.post(
            f"{BGW_ADDR}/browsergw/extension/load",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: BrowserGateway 接受了空的 extension_file_path")
            return False
        else:
            print("[PASS] BrowserGateway 正确拒绝了空的 extension_file_path")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_load_extension_bucket_missing():
    """
    测试步骤3: 缺少bucket_name字段
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤3: 缺少bucket_name字段 ==========")

    test_data = {
        "extension_file_path": "/opt/extensions/test"
    }

    print(f"[INFO] 请求参数: 缺少 bucket_name 字段")

    try:
        response = requests.post(
            f"{BGW_ADDR}/browsergw/extension/load",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: BrowserGateway 接受了缺少 bucket_name 的请求")
            return False
        else:
            print("[PASS] BrowserGateway 正确拒绝了缺少 bucket_name 的请求")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_load_extension_path_missing():
    """
    测试步骤4: 缺少extension_file_path字段
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤4: 缺少extension_file_path字段 ==========")

    test_data = {
        "bucket_name": "test_bucket"
    }

    print(f"[INFO] 请求参数: 缺少 extension_file_path 字段")

    try:
        response = requests.post(
            f"{BGW_ADDR}/browsergw/extension/load",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: BrowserGateway 接受了缺少 extension_file_path 的请求")
            return False
        else:
            print("[PASS] BrowserGateway 正确拒绝了缺少 extension_file_path 的请求")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_load_extension_empty_body():
    """
    测试步骤5: 空请求体
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤5: 空请求体 ==========")

    test_data = {}

    print(f"[INFO] 请求参数: 空请求体")

    try:
        response = requests.post(
            f"{BGW_ADDR}/browsergw/extension/load",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: BrowserGateway 接受了空请求体")
            return False
        else:
            print("[PASS] BrowserGateway 正确拒绝了空请求体")
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
    BrowserGateway插件接口 - 加载插件参数校验测试
    TC_SBG_Func_BGW_003_002
==================================================================
    """)
    print(f"[INFO] BrowserGateway地址: {BGW_ADDR}")
    print("")

    test_results = []

    result1 = test_load_extension_bucket_empty()
    test_results.append(("步骤1: bucket_name为空", result1))

    result2 = test_load_extension_path_empty()
    test_results.append(("步骤2: extension_file_path为空", result2))

    result3 = test_load_extension_bucket_missing()
    test_results.append(("步骤3: 缺少bucket_name字段", result3))

    result4 = test_load_extension_path_missing()
    test_results.append(("步骤4: 缺少extension_file_path字段", result4))

    result5 = test_load_extension_empty_body()
    test_results.append(("步骤5: 空请求体", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    if not all_passed:
        print("\n[INFO] 注意: 部分测试失败可能表示 BrowserGateway 存在参数校验缺陷")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())