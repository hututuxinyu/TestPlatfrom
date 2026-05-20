#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_012_002.py
# 测试用例: GIDS插件管理接口 - 参数校验测试
# 目标: 验证 GIDS 插件接口参数校验能力

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_upload_plugin_no_file():
    """
    测试步骤1: 上传插件包缺少文件
    预期: 返回参数校验错误
    """
    print("[INFO] ========== 测试步骤1: 上传插件包缺少文件 ==========")

    data = {'filename': 'test.zip'}

    print(f"[INFO] 请求参数: 缺少 file 字段")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/plugin/v1/upload",
            data=data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG: GIDS 接受了缺少文件的请求")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了缺少文件的请求")
            return True

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_upload_plugin_empty_file():
    """
    测试步骤2: 上传空文件
    预期: 返回参数校验错误
    """
    print("\n[INFO] ========== 测试步骤2: 上传空文件 ==========")

    files = {'file': ('empty.zip', b"", 'application/zip')}
    data = {'filename': 'empty.zip'}

    print(f"[INFO] 请求参数: 空文件 (0 bytes)")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG: GIDS 接受了空文件")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空文件")
            return True

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_load_plugin_empty_name():
    """
    测试步骤3: 加载插件名称为空
    预期: 返回参数校验错误
    """
    print("\n[INFO] ========== 测试步骤3: 加载插件名称为空 ==========")

    test_data = {
        "name": "",
        "type": "record",
        "version": "1.0.0"
    }

    print(f"[INFO] 请求参数: name='' (空字符串)")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG: GIDS 接受了空的插件名称")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的插件名称")
            return True

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_load_plugin_missing_version():
    """
    测试步骤4: 加载插件缺少版本号
    预期: 返回参数校验错误
    """
    print("\n[INFO] ========== 测试步骤4: 加载插件缺少版本号 ==========")

    test_data = {
        "name": "TestPlugin",
        "type": "record"
    }

    print(f"[INFO] 请求参数: 缺少 version 字段")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG: GIDS 接受了缺少版本号的请求")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了缺少版本号的请求")
            return True

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_delete_plugin_empty_body():
    """
    测试步骤5: 删除插件包空请求体
    预期: 返回参数校验错误
    """
    print("\n[INFO] ========== 测试步骤5: 删除插件包空请求体 ==========")

    test_data = {}

    print(f"[INFO] 请求参数: 空请求体")

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

        if resp_json.get('code') == 200:
            print("[FAIL] BUG: GIDS 接受了空请求体")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空请求体")
            return True

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    GIDS插件管理接口 - 参数校验测试
    TC_SBG_Func_GIDS_012_002
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_upload_plugin_no_file()
    test_results.append(("步骤1: 上传插件包缺少文件", result1))

    result2 = test_upload_plugin_empty_file()
    test_results.append(("步骤2: 上传空文件", result2))

    result3 = test_load_plugin_empty_name()
    test_results.append(("步骤3: 加载插件名称为空", result3))

    result4 = test_load_plugin_missing_version()
    test_results.append(("步骤4: 加载插件缺少版本号", result4))

    result5 = test_delete_plugin_empty_body()
    test_results.append(("步骤5: 删除插件包空请求体", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    if not all_passed:
        print("\n[INFO] 部分测试失败表示 GIDS 存在参数校验缺陷")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())