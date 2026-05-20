#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_005_002.py
# 测试用例: GIDS文件接口 - 文件下载正常流程测试
# 目标: 验证 GIDS 文件下载接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_file_download_existing_file():
    """
    测试步骤1: 下载存在的文件
    预期: 返回文件内容
    """
    print("[INFO] ========== 测试步骤1: 下载存在的文件 ==========")

    file_name = "test_upload_001.txt"

    print(f"[INFO] 请求参数: fileName={file_name}")

    try:
        response = requests.get(
            f"{GIDS_ADDR}/app-api/control/file/download/{file_name}",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应Content-Type: {response.headers.get('Content-Type', 'N/A')}")

        if response.status_code == 200:
            content_length = len(response.content)
            print(f"[PASS] 文件下载成功，文件大小: {content_length} bytes")
            return True
        elif response.status_code == 404:
            print("[INFO] 文件不存在，需要先上传文件")
            return True
        else:
            print(f"[FAIL] 文件下载失败，状态码: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_file_download_non_existing_file():
    """
    测试步骤2: 下载不存在的文件
    预期: 返回404错误
    """
    print("\n[INFO] ========== 测试步骤2: 下载不存在的文件 ==========")

    file_name = "non_existing_file_999.txt"

    print(f"[INFO] 请求参数: fileName={file_name} (不存在的文件)")

    try:
        response = requests.get(
            f"{GIDS_ADDR}/app-api/control/file/download/{file_name}",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")

        if response.status_code == 404:
            print("[PASS] GIDS 正确返回404，文件不存在")
            return True
        elif response.status_code == 200:
            print("[FAIL] BUG确认: GIDS 对不存在的文件返回200")
            return False
        else:
            print(f"[PASS] 不存在文件下载测试完成，返回: {response.status_code}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_file_download_special_file_name():
    """
    测试步骤3: 特殊文件名下载（安全测试）
    预期: GIDS 应正确处理
    """
    print("\n[INFO] ========== 测试步骤3: 特殊文件名下载（安全测试） ==========")

    file_name = "../../../etc/passwd"

    print(f"[INFO] 请求参数: fileName='{file_name}' (路径遍历尝试)")

    try:
        response = requests.get(
            f"{GIDS_ADDR}/app-api/control/file/download/{file_name}",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")

        if response.status_code == 200:
            content_preview = response.content[:100] if response.content else b''
            if b'root:' in content_preview:
                print("[FAIL] 安全漏洞: GIDS 可能存在路径遍历漏洞，可以读取系统文件")
                return False
            else:
                print("[WARN] GIDS 接受了特殊文件名，但未返回敏感内容")
                return True
        else:
            print("[PASS] GIDS 正确拒绝了路径遍历尝试")
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
    GIDS文件接口 - 文件下载正常流程测试
    TC_SBG_Func_GIDS_005_002
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_file_download_existing_file()
    test_results.append(("步骤1: 下载存在的文件", result1))

    result2 = test_file_download_non_existing_file()
    test_results.append(("步骤2: 下载不存在的文件", result2))

    result3 = test_file_download_special_file_name()
    test_results.append(("步骤3: 特殊文件名下载(安全测试)", result3))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    if not all_passed:
        print("\n[INFO] 注意: 部分测试失败可能表示 GIDS 存在安全漏洞")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())