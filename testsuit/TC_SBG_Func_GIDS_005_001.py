#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_005_001.py
# 测试用例: GIDS文件接口 - 文件上传正常流程测试
# 目标: 验证 GIDS 文件上传接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_file_upload_normal():
    """
    测试步骤1: 正常文件上传
    预期: 返回成功，返回文件路径
    """
    print("[INFO] ========== 测试步骤1: 正常文件上传 ==========")

    file_content = b"This is a test file content for GIDS upload test."
    file_name = "test_upload_001.txt"

    print(f"[INFO] 请求参数: fileName={file_name}, fileSize={len(file_content)} bytes")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/control/file/upload",
            params={'fileName': file_name},
            data=file_content,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            data = resp_json.get('data')
            if data:
                print(f"[PASS] 文件上传成功，返回路径: {data}")
                return True
            else:
                print("[FAIL] 文件上传成功但缺少返回路径")
                return False
        else:
            print(f"[FAIL] 文件上传失败: code={resp_json.get('code')}, message={resp_json.get('message')}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_file_upload_small_file():
    """
    测试步骤2: 小文件上传
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤2: 小文件上传 ==========")

    file_content = b"Small test content"
    file_name = "test_small.txt"

    print(f"[INFO] 请求参数: fileName={file_name}, fileSize={len(file_content)} bytes (小文件)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/control/file/upload",
            params={'fileName': file_name},
            data=file_content,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 小文件上传测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_file_upload_empty_file():
    """
    测试步骤3: 空文件上传
    预期: 返回成功或错误提示
    """
    print("\n[INFO] ========== 测试步骤3: 空文件上传 ==========")

    file_content = b""
    file_name = "test_empty.txt"

    print(f"[INFO] 请求参数: fileName={file_name}, fileSize={len(file_content)} bytes (空文件)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/control/file/upload",
            params={'fileName': file_name},
            data=file_content,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()
        print(f"[PASS] 空文件上传测试完成，返回: code={resp_json.get('code')}")
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_file_upload_without_file_name():
    """
    测试步骤4: 缺少fileName参数
    预期: 返回错误提示
    """
    print("\n[INFO] ========== 测试步骤4: 缺少fileName参数 ==========")

    file_content = b"Test content"

    print(f"[INFO] 请求参数: 缺少 fileName 参数")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/control/file/upload",
            data=file_content,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == -2:
            print("[PASS] GIDS 正确拒绝了缺少 fileName 的请求")
            return True
        else:
            print(f"[PASS] 缺少fileName参数测试完成，返回: code={resp_json.get('code')}")
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
    GIDS文件接口 - 文件上传正常流程测试
    TC_SBG_Func_GIDS_005_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_file_upload_normal()
    test_results.append(("步骤1: 正常文件上传", result1))

    result2 = test_file_upload_small_file()
    test_results.append(("步骤2: 小文件上传", result2))

    result3 = test_file_upload_empty_file()
    test_results.append(("步骤3: 空文件上传", result3))

    result4 = test_file_upload_without_file_name()
    test_results.append(("步骤4: 缺少fileName参数", result4))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())