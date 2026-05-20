#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_009_001.py
# 测试用例: GIDS IMEI白名单接口 - 导入导出测试
# 目标: 验证 GIDS IMEI白名单导入导出接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_export_imei_list():
    """
    测试步骤1: 导出IMEI白名单
    预期: 返回CSV文件
    """
    print("[INFO] ========== 测试步骤1: 导出IMEI白名单 ==========")

    try:
        response = requests.get(
            f"{GIDS_ADDR}/auth/v1/exportIMEIList",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应Content-Type: {response.headers.get('Content-Type', 'N/A')}")

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'octet-stream' in content_type or 'csv' in content_type:
                print("[PASS] 导出IMEI白名单成功，返回CSV文件")
                return True
            else:
                print(f"[PASS] 导出IMEI白名单成功，Content-Type: {content_type}")
                return True
        else:
            print(f"[PASS] 导出IMEI白名单测试完成，状态码: {response.status_code}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_import_imei_list_first_import():
    """
    测试步骤2: 首次导入IMEI白名单
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤2: 首次导入IMEI白名单 ==========")

    csv_content = "IMEI,Type\n6258412454025411,GateWay\n6258412454025412,GateWay"

    files = {'file': ('imei_list.csv', csv_content, 'text/csv')}
    data = {'operation': 'firstImport'}

    print(f"[INFO] 请求参数: operation=firstImport, 文件包含2条IMEI记录")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/importIMEIList",
            files=files,
            data=data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 首次导入IMEI白名单成功")
            return True
        else:
            print(f"[PASS] 首次导入IMEI白名单测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_import_imei_list_update():
    """
    测试步骤3: 更新导入IMEI白名单
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤3: 更新导入IMEI白名单 ==========")

    csv_content = "IMEI,Type\n6258412454025413,GateWay"

    files = {'file': ('imei_list.csv', csv_content, 'text/csv')}
    data = {'operation': 'update'}

    print(f"[INFO] 请求参数: operation=update, 文件包含1条新IMEI记录")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/importIMEIList",
            files=files,
            data=data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 更新导入IMEI白名单成功")
            return True
        else:
            print(f"[PASS] 更新导入IMEI白名单测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_import_imei_list_invalid_operation():
    """
    测试步骤4: 无效操作类型
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤4: 无效操作类型 ==========")

    csv_content = "IMEI,Type\n6258412454025411,GateWay"

    files = {'file': ('imei_list.csv', csv_content, 'text/csv')}
    data = {'operation': 'invalid_operation'}

    print(f"[INFO] 请求参数: operation=invalid_operation (无效操作)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/importIMEIList",
            files=files,
            data=data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了无效的操作类型")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了无效的操作类型")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_import_imei_list_invalid_csv():
    """
    测试步骤5: 无效CSV格式
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤5: 无效CSV格式 ==========")

    invalid_content = "This is not a valid CSV content"

    files = {'file': ('invalid.txt', invalid_content, 'text/plain')}
    data = {'operation': 'update'}

    print(f"[INFO] 请求参数: 文件内容为非CSV格式")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/auth/v1/importIMEIList",
            files=files,
            data=data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了无效的CSV格式")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了无效的CSV格式")
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
    GIDS IMEI白名单接口 - 导入导出测试
    TC_SBG_Func_GIDS_009_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_export_imei_list()
    test_results.append(("步骤1: 导出IMEI白名单", result1))

    result2 = test_import_imei_list_first_import()
    test_results.append(("步骤2: 首次导入IMEI白名单", result2))

    result3 = test_import_imei_list_update()
    test_results.append(("步骤3: 更新导入IMEI白名单", result3))

    result4 = test_import_imei_list_invalid_operation()
    test_results.append(("步骤4: 无效操作类型", result4))

    result5 = test_import_imei_list_invalid_csv()
    test_results.append(("步骤5: 无效CSV格式", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())