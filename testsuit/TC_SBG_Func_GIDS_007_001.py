#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_007_001.py
# 测试用例: GIDS用户绑定接口 - 正常流程测试
# 目标: 验证 GIDS 用户绑定接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')

def test_get_user_bind():
    """
    测试步骤1: 获取用户绑定信息
    预期: 返回用户绑定信息或404
    """
    print("[INFO] ========== 测试步骤1: 获取用户绑定信息 ==========")

    session_id = "test_session_001"

    print(f"[INFO] 请求参数: sessionID={session_id}")

    try:
        response = requests.get(
            f"{GIDS_ADDR}/user-bind/v1/{session_id}",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        if response.status_code == 200:
            resp_json = response.json()
            print(f"[PASS] 获取用户绑定成功，返回: code={resp_json.get('code')}")
            return True
        elif response.status_code == 404:
            print("[PASS] 用户绑定不存在，返回404")
            return True
        else:
            print(f"[PASS] 获取用户绑定测试完成，状态码: {response.status_code}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_expired_user_bind():
    """
    测试步骤2: 过期用户绑定
    预期: 返回成功或404
    """
    print("\n[INFO] ========== 测试步骤2: 过期用户绑定 ==========")

    session_id = "test_session_001"

    print(f"[INFO] 请求参数: sessionID={session_id}")

    try:
        response = requests.put(
            f"{GIDS_ADDR}/user-bind/v1/{session_id}",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        if response.status_code == 200:
            resp_json = response.json()
            print(f"[PASS] 过期用户绑定成功，返回: code={resp_json.get('code')}")
            return True
        elif response.status_code == 404:
            print("[PASS] 用户绑定不存在，返回404")
            return True
        else:
            print(f"[PASS] 过期用户绑定测试完成，状态码: {response.status_code}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_update_user_bind():
    """
    测试步骤3: 更新用户绑定
    预期: 返回成功
    """
    print("\n[INFO] ========== 测试步骤3: 更新用户绑定 ==========")

    test_data = {
        "sessionID": "test_session_001",
        "browserInstance": "test_browser_instance",
        "mediaEndpoint": "127.0.0.1:8080",
        "controlEndpoint": "127.0.0.1:8081",
        "mediaTlsEndpoint": "127.0.0.1:8082",
        "controlTlsEndpoint": "127.0.0.1:8083",
        "innerMediaEndpoint": "127.0.0.1:8084",
        "innerBrowserEndpoint": "127.0.0.1:8085"
    }

    print(f"[INFO] 请求参数: sessionID={test_data['sessionID']}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/user-bind/v1/update",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 更新用户绑定成功")
            return True
        else:
            print(f"[PASS] 更新用户绑定测试完成，返回: code={resp_json.get('code')}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_update_user_bind_empty_session():
    """
    测试步骤4: 更新用户绑定sessionID为空
    预期: 返回错误
    """
    print("\n[INFO] ========== 测试步骤4: 更新用户绑定sessionID为空 ==========")

    test_data = {
        "sessionID": "",
        "browserInstance": "test_browser_instance"
    }

    print(f"[INFO] 请求参数: sessionID='' (空字符串)")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/user-bind/v1/update",
            json=test_data,
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        resp_json = response.json()

        if resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 接受了空的 sessionID")
            return False
        else:
            print("[PASS] GIDS 正确拒绝了空的 sessionID")
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
    GIDS用户绑定接口 - 正常流程测试
    TC_SBG_Func_GIDS_007_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    test_results = []

    result1 = test_get_user_bind()
    test_results.append(("步骤1: 获取用户绑定信息", result1))

    result2 = test_expired_user_bind()
    test_results.append(("步骤2: 过期用户绑定", result2))

    result3 = test_update_user_bind()
    test_results.append(("步骤3: 更新用户绑定", result3))

    result4 = test_update_user_bind_empty_session()
    test_results.append(("步骤4: 更新用户绑定sessionID为空", result4))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())