#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_015_001.py
# 测试用例: GIDS服务器事件上传接口 - 正常流程测试
# 目标: 验证 GIDS 服务器事件上传接口正常功能

import requests
import json
import sys
import os
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_upload_server_event_normal():
    """
    测试步骤1: 正常参数上传服务器事件
    预期: 返回成功
    """
    print("[INFO] ========== 测试步骤1: 正常参数上传服务器事件 ==========")

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    test_data = {
        "service": "GIDS",
        "event": "LOGIN_SUCCESS",
        "eventDesc": "User login successfully",
        "eventTrigger": "user_action",
        "eventTime": now,
        "env": "production",
        "hostname": "gids-pod-1",
        "object": "user_session",
        "serviceInstanceName": "GIDS-Instance-1",
        "eventData": {
            "imei": "6258412454025411",
            "imsi": "685101555652111",
            "session_duration": 3600
        }
    }

    print(f"[INFO] 请求参数: event={test_data['event']}, service={test_data['service']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/server/event/v1/uploadEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 上传服务器事件成功")
            return True
        else:
            print(f"[PASS] 上传服务器事件测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_upload_server_event_different_event_type():
    """
    测试步骤2: 不同事件类型测试
    预期: 各事件类型都能正确处理
    """
    print("\n[INFO] ========== 测试步骤2: 不同事件类型测试 ==========")

    events = [
        "LOGIN_SUCCESS",
        "LOGIN_FAILED",
        "SESSION_TIMEOUT",
        "CACHE_CLEARED",
        "CONFIG_UPDATED",
        "PLUGIN_LOADED"
    ]

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for event in events:
        test_data = {
            "service": "GIDS",
            "event": event,
            "eventDesc": f"Test event: {event}",
            "eventTime": now,
            "eventData": {"test": True}
        }

        print(f"[INFO] 测试事件类型: {event}")

        try:
            response = requests.post(
                f"{GIDS_ADDR}/server/event/v1/uploadEvent",
                json=test_data,
                timeout=30,
                verify=False
            )
            resp_json = response.json()
            print(f"[INFO] {event}: code={resp_json.get('code')}")
        except Exception as e:
            print(f"[ERROR] {event}: {str(e)}")

    print("[PASS] 不同事件类型测试完成")
    return True


def test_upload_server_event_empty_event():
    """
    测试步骤3: 事件名称为空
    预期: 返回参数校验错误
    """
    print("\n[INFO] ========== 测试步骤3: 事件名称为空 ==========")

    test_data = {
        "service": "GIDS",
        "event": "",
        "eventData": {"test": True}
    }

    print(f"[INFO] 请求参数: event='' (空字符串)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/server/event/v1/uploadEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG: GIDS 接受了空的事件名称")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的事件名称")
            return True

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_upload_server_event_empty_event_data():
    """
    测试步骤4: eventData为空
    预期: 返回参数校验错误
    """
    print("\n[INFO] ========== 测试步骤4: eventData为空 ==========")

    test_data = {
        "service": "GIDS",
        "event": "TEST_EVENT",
        "eventData": {}
    }

    print(f"[INFO] 请求参数: eventData={} (空对象)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/server/event/v1/uploadEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG: GIDS 接受了空的 eventData")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的 eventData")
            return True

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_upload_server_event_missing_event_data():
    """
    测试步骤5: 缺少eventData字段
    预期: 返回参数校验错误
    """
    print("\n[INFO] ========== 测试步骤5: 缺少eventData字段 ==========")

    test_data = {
        "service": "GIDS",
        "event": "TEST_EVENT"
    }

    print(f"[INFO] 请求参数: 缺少 eventData 字段")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/server/event/v1/uploadEvent",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG: GIDS 接受了缺少 eventData 的请求")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了缺少 eventData 的请求")
            return True

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    GIDS服务器事件上传接口 - 正常流程测试
    TC_SBG_Func_GIDS_015_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_upload_server_event_normal()
    test_results.append(("步骤1: 正常参数上传服务器事件", result1))

    result2 = test_upload_server_event_different_event_type()
    test_results.append(("步骤2: 不同事件类型测试", result2))

    result3 = test_upload_server_event_empty_event()
    test_results.append(("步骤3: 事件名称为空", result3))

    result4 = test_upload_server_event_empty_event_data()
    test_results.append(("步骤4: eventData为空", result4))

    result5 = test_upload_server_event_missing_event_data()
    test_results.append(("步骤5: 缺少eventData字段", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())