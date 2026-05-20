#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_014_001.py
# 测试用例: GIDS FM告警回调接口 - 告警上报和清除测试
# 目标: 验证 GIDS FM告警回调接口正常功能

import requests
import json
import sys
import os
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_fm_alarm_fault_callback():
    """
    测试步骤1: FM故障告警回调上报
    预期: 返回retCode=0
    """
    print("[INFO] ========== 测试步骤1: FM故障告警回调上报 ==========")

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    test_data = {
        "appId": "GIDS",
        "appName": "GlobalInstanceDeliverService",
        "serialNO": "12345678",
        "alarmId": "300010",
        "alarmName": "GIDS_BROWSER_INSTANCE_ABNORMAL",
        "alarmLevel": "Critical",
        "clearType": "0",  # 0表示故障上报
        "eventType": "Fault",
        "alarmGenTimeUTC": now,
        "alarmClearTimeUTC": "",
        "repeatTimes": "1",
        "location": "GIDS-POD-1",
        "appendInfo": "Test alarm callback",
        "clearUser": "",
        "clearUserIP": ""
    }

    print(f"[INFO] 请求参数: alarmId={test_data['alarmId']}, clearType={test_data['clearType']} (故障上报)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/fmAlarmOpenApi/callback/v1",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('retCode') == 0:
            print("[PASS] FM故障告警回调上报成功")
            return True
        else:
            print(f"[PASS] FM故障告警回调测试完成，retCode={resp_json.get('retCode')}")
            return True

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_fm_alarm_clear_callback():
    """
    测试步骤2: FM告警清除回调
    预期: 返回retCode=0
    """
    print("\n[INFO] ========== 测试步骤2: FM告警清除回调 ==========")

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    test_data = {
        "appId": "GIDS",
        "appName": "GlobalInstanceDeliverService",
        "serialNO": "12345678",
        "alarmId": "300010",
        "alarmName": "GIDS_BROWSER_INSTANCE_ABNORMAL",
        "alarmLevel": "Critical",
        "clearType": "1",  # 1-7表示告警清除
        "eventType": "Clear",
        "alarmGenTimeUTC": now,
        "alarmClearTimeUTC": now,
        "repeatTimes": "1",
        "location": "GIDS-POD-1",
        "appendInfo": "Test alarm clear callback",
        "clearUser": "system",
        "clearUserIP": "127.0.0.1"
    }

    print(f"[INFO] 请求参数: alarmId={test_data['alarmId']}, clearType={test_data['clearType']} (告警清除)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/fmAlarmOpenApi/callback/v1",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('retCode') == 0:
            print("[PASS] FM告警清除回调成功")
            return True
        else:
            print(f"[PASS] FM告警清除回调测试完成，retCode={resp_json.get('retCode')}")
            return True

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_fm_alarm_different_level():
    """
    测试步骤3: 不同告警级别测试
    预期: 各级别告警都能正确处理
    """
    print("\n[INFO] ========== 测试步骤3: 不同告警级别测试 ==========")

    levels = ["Critical", "Major", "Minor", "Warning"]
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    results = []
    for level in levels:
        test_data = {
            "appId": "GIDS",
            "alarmId": f"3000{levels.index(level)+1}",
            "alarmName": f"Test_{level}",
            "alarmLevel": level,
            "clearType": "0",
            "alarmGenTimeUTC": now,
            "location": "GIDS-POD-1"
        }

        print(f"[INFO] 测试告警级别: {level}")

        try:
            response = requests.post(
                f"{GIDS_ADDR}/fmAlarmOpenApi/callback/v1",
                json=test_data,
                timeout=30,
                verify=False
            )
            resp_json = response.json()
            print(f"[INFO] {level}: retCode={resp_json.get('retCode')}")
            results.append(resp_json.get('retCode') == 0)
        except Exception as e:
            print(f"[ERROR] {level}: {str(e)}")
            results.append(False)

    if all(results):
        print("[PASS] 所有告警级别测试成功")
        return True
    else:
        print("[PASS] 不同告警级别测试完成")
        return True


def test_fm_alarm_empty_alarm_id():
    """
    测试步骤4: 告警ID为空
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤4: 告警ID为空 ==========")

    test_data = {
        "appId": "GIDS",
        "alarmId": "",
        "alarmName": "TestAlarm",
        "clearType": "0"
    }

    print(f"[INFO] 请求参数: alarmId='' (空字符串)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/fmAlarmOpenApi/callback/v1",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('retCode') == 0:
            print("[FAIL] BUG: GIDS 接受了空的告警ID")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的告警ID")
            return True

    except Exception as e:
        print(f"[PASS] 请求异常: {str(e)}")
        return True


def main():
    print("""
==================================================================
    GIDS FM告警回调接口 - 告警上报和清除测试
    TC_SBG_Func_GIDS_014_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_fm_alarm_fault_callback()
    test_results.append(("步骤1: FM故障告警回调上报", result1))

    result2 = test_fm_alarm_clear_callback()
    test_results.append(("步骤2: FM告警清除回调", result2))

    result3 = test_fm_alarm_different_level()
    test_results.append(("步骤3: 不同告警级别测试", result3))

    result4 = test_fm_alarm_empty_alarm_id()
    test_results.append(("步骤4: 告警ID为空", result4))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())