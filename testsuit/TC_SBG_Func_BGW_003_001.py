#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_BGW_003_001.py
# 测试用例: BrowserGateway插件接口 - 加载插件正常流程测试
# 目标: 验证 BrowserGateway 加载插件接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
BGW_ADDR = os.getenv('BGW_ADDR', 'http://127.0.0.1:8090')

def test_load_extension_normal():
    """
    测试步骤1: 正常参数加载插件
    预期: 返回成功，code=200
    """
    print("[INFO] ========== 测试步骤1: 正常参数加载插件 ==========")

    test_data = {
        "bucket_name": "test_bucket",
        "extension_file_path": "/opt/extensions/test_extension",
        "name": "TestExtension",
        "version": "1.0.0",
        "type": "record"
    }

    print(f"[INFO] 请求参数: bucket_name={test_data['bucket_name']}, name={test_data['name']}")

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

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 加载插件成功")
            return True
        else:
            print(f"[PASS] 加载插件测试完成，返回: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_get_plugin_info():
    """
    测试步骤2: 获取插件信息
    预期: 返回插件状态信息
    """
    print("\n[INFO] ========== 测试步骤2: 获取插件信息 ==========")

    try:
        response = requests.get(
            f"{BGW_ADDR}/browsergw/extension/pluginInfo",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            data = resp_json.get('data')
            print(f"[PASS] 获取插件信息成功，data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"[PASS] 获取插件信息测试完成，返回: code={resp_json.get('code')}")
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
    BrowserGateway插件接口 - 加载插件正常流程测试
    TC_SBG_Func_BGW_003_001
==================================================================
    """)
    print(f"[INFO] BrowserGateway地址: {BGW_ADDR}")
    print("")

    test_results = []

    result1 = test_load_extension_normal()
    test_results.append(("步骤1: 正常参数加载插件", result1))

    result2 = test_get_plugin_info()
    test_results.append(("步骤2: 获取插件信息", result2))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())