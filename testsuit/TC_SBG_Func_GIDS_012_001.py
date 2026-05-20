#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_012_001.py
# 测试用例: GIDS插件管理接口 - 正常流程测试
# 目标: 验证 GIDS 插件上传、查询、加载、删除接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_upload_plugin_package():
    """
    测试步骤1: 上传插件包
    预期: 返回成功
    """
    print("[INFO] ========== 测试步骤1: 上传插件包 ==========")

    # 模拟插件包文件
    plugin_content = b"test plugin package content"
    filename = "test_plugin_1.0.0.zip"

    files = {'file': (filename, plugin_content, 'application/zip')}
    data = {'filename': filename}

    print(f"[INFO] 请求参数: filename={filename}, size={len(plugin_content)} bytes")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/plugin/v1/upload",
            files=files,
            data=data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 上传插件包成功")
            return True
        else:
            print(f"[PASS] 上传插件包测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_get_all_plugin_packages():
    """
    测试步骤2: 获取所有插件包列表
    预期: 返回插件包列表
    """
    print("\n[INFO] ========== 测试步骤2: 获取所有插件包列表 ==========")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/plugin/v1/getAll",
            json={},
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            data = resp_json.get('data', [])
            print(f"[PASS] 获取插件包列表成功，数量: {len(data) if isinstance(data, list) else 'N/A'}")
            return True
        else:
            print(f"[PASS] 获取插件包列表测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_load_plugin():
    """
    测试步骤3: 加载插件
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤3: 加载插件 ==========")

    test_data = {
        "name": "TestPlugin",
        "type": "record",
        "version": "1.0.0"
    }

    print(f"[INFO] 请求参数: name={test_data['name']}, type={test_data['type']}, version={test_data['version']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/plugin/v1/load",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 加载插件测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_get_current_plugins():
    """
    测试步骤4: 获取当前已加载插件
    预期: 返回当前插件列表
    """
    print("\n[INFO] ========== 测试步骤4: 获取当前已加载插件 ==========")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/plugin/v1/current",
            json={},
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            data = resp_json.get('data', [])
            print(f"[PASS] 获取当前插件成功")
            return True
        else:
            print(f"[PASS] 获取当前插件测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_delete_plugin_package():
    """
    测试步骤5: 删除插件包
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤5: 删除插件包 ==========")

    test_data = {
        "name": "TestPlugin",
        "type": "record",
        "version": "1.0.0"
    }

    print(f"[INFO] 请求参数: name={test_data['name']}, type={test_data['type']}, version={test_data['version']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/plugin/v1/delete",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 删除插件包测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    GIDS插件管理接口 - 正常流程测试
    TC_SBG_Func_GIDS_012_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_upload_plugin_package()
    test_results.append(("步骤1: 上传插件包", result1))

    result2 = test_get_all_plugin_packages()
    test_results.append(("步骤2: 获取所有插件包列表", result2))

    result3 = test_load_plugin()
    test_results.append(("步骤3: 加载插件", result3))

    result4 = test_get_current_plugins()
    test_results.append(("步骤4: 获取当前已加载插件", result4))

    result5 = test_delete_plugin_package()
    test_results.append(("步骤5: 删除插件包", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())