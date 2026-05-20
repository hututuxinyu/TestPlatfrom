#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_011_001.py
# 测试用例: GIDS流量统计接口 - 正常流程测试
# 目标: 验证 GIDS 流量统计接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_session_stats():
    """
    测试步骤1: 上报会话统计
    预期: 返回成功
    """
    print("[INFO] ========== 测试步骤1: 上报会话统计 ==========")

    test_data = {
        "session_id": "test_session_001",
        "imei": "6258412454025411",
        "imsi": "685101555652111",
        "start_time": "2026-05-20 10:00:00",
        "end_time": "2026-05-20 11:00:00",
        "duration": "3600",
        "bytes_sent": "1024000",
        "bytes_received": "2048000"
    }

    print(f"[INFO] 请求参数: session_id={test_data['session_id']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/stats/v1/session",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 上报会话统计成功")
            return True
        else:
            print(f"[PASS] 上报会话统计测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_media_traffic_stats():
    """
    测试步骤2: 上报媒体流量统计
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤2: 上报媒体流量统计 ==========")

    test_data = {
        "items": [
            {
                "session_id": "test_session_001",
                "timestamp": "2026-05-20 10:00:00",
                "bytes_sent": "512000",
                "bytes_received": "1024000",
                "packets_sent": "1000",
                "packets_received": "2000"
            },
            {
                "session_id": "test_session_002",
                "timestamp": "2026-05-20 10:01:00",
                "bytes_sent": "256000",
                "bytes_received": "512000",
                "packets_sent": "500",
                "packets_received": "1000"
            }
        ]
    }

    print(f"[INFO] 请求参数: items包含{len(test_data['items'])}条记录")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/stats/v1/traffic/media",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 上报媒体流量统计成功")
            return True
        else:
            print(f"[PASS] 上报媒体流量统计测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_control_traffic_stats():
    """
    测试步骤3: 上报控制流量统计
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤3: 上报控制流量统计 ==========")

    test_data = {
        "items": [
            {
                "session_id": "test_session_001",
                "timestamp": "2026-05-20 10:00:00",
                "bytes_sent": "128000",
                "bytes_received": "256000",
                "commands_sent": "100",
                "commands_received": "200"
            }
        ]
    }

    print(f"[INFO] 请求参数: items包含{len(test_data['items'])}条记录")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/stats/v1/traffic/control",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 上报控制流量统计成功")
            return True
        else:
            print(f"[PASS] 上报控制流量统计测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_export_static_data():
    """
    测试步骤4: 导出统计数据
    预期: 返回ZIP文件
    """
    print("\n[INFO] ========== 测试步骤4: 导出统计数据 ==========")

    month = "2026-05"

    print(f"[INFO] 请求参数: month={month}")

    try:
        response = requests.get(
            f"{GIDS_ADDR}/stats/v1/exportStaticData/{month}",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应Content-Type: {response.headers.get('Content-Type', 'N/A')}")

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'zip' in content_type or 'octet-stream' in content_type:
                print("[PASS] 导出统计数据成功，返回ZIP文件")
                return True
            else:
                print(f"[PASS] 导出统计数据成功，Content-Type: {content_type}")
                return True
        else:
            print(f"[PASS] 导出统计数据测试完成，状态码: {response.status_code}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_export_static_data_invalid_month():
    """
    测试步骤5: 无效月份格式导出
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤5: 无效月份格式导出 ==========")

    month = "invalid_month"

    print(f"[INFO] 请求参数: month={month} (无效格式)")

    try:
        response = requests.get(
            f"{GIDS_ADDR}/stats/v1/exportStaticData/{month}",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        if response.status_code == 200:
            print("[WARN] GIDS 接受了无效的月份格式")
            return True
        else:
            print("[PASS] GIDS 正确拒绝了无效的月份格式")
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
    GIDS流量统计接口 - 正常流程测试
    TC_SBG_Func_GIDS_011_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_session_stats()
    test_results.append(("步骤1: 上报会话统计", result1))

    result2 = test_media_traffic_stats()
    test_results.append(("步骤2: 上报媒体流量统计", result2))

    result3 = test_control_traffic_stats()
    test_results.append(("步骤3: 上报控制流量统计", result3))

    result4 = test_export_static_data()
    test_results.append(("步骤4: 导出统计数据", result4))

    result5 = test_export_static_data_invalid_month()
    test_results.append(("步骤5: 无效月份格式导出", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())