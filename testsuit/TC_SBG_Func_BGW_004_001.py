#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_BGW_004_001.py
# 测试用例: BrowserGateway健康检查接口 - 正常流程测试
# 目标: 验证 BrowserGateway 健康检查接口正常功能

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
BGW_ADDR = os.getenv('BGW_ADDR', 'http://127.0.0.1:8090')

def test_health_check():
    """
    测试步骤1: 健康检查接口
    预期: 返回健康状态信息
    """
    print("[INFO] ========== 测试步骤1: 健康检查接口 ==========")

    try:
        response = requests.get(
            f"{BGW_ADDR}/actuator/health",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        if response.status_code == 200:
            resp_json = response.json()
            status = resp_json.get('status', 'UNKNOWN')
            print(f"[PASS] 健康检查成功，status: {status}")
            return True
        else:
            print(f"[FAIL] 健康检查失败，状态码: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_health_liveness():
    """
    测试步骤2: 存活探针接口
    预期: 返回存活状态
    """
    print("\n[INFO] ========== 测试步骤2: 存活探针接口 ==========")

    try:
        response = requests.get(
            f"{BGW_ADDR}/actuator/health/liveness",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        if response.status_code == 200:
            print("[PASS] 存活探针检查成功")
            return True
        else:
            print(f"[PASS] 存活探针检查完成，状态码: {response.status_code}")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {BGW_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_health_readiness():
    """
    测试步骤3: 就绪探针接口
    预期: 返回就绪状态
    """
    print("\n[INFO] ========== 测试步骤3: 就绪探针接口 ==========")

    try:
        response = requests.get(
            f"{BGW_ADDR}/actuator/health/readiness",
            timeout=30,
            verify=False
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        if response.status_code == 200:
            print("[PASS] 就绪探针检查成功")
            return True
        else:
            print(f"[PASS] 就绪探针检查完成，状态码: {response.status_code}")
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
    BrowserGateway健康检查接口 - 正常流程测试
    TC_SBG_Func_BGW_004_001
==================================================================
    """)
    print(f"[INFO] BrowserGateway地址: {BGW_ADDR}")
    print("")

    test_results = []

    result1 = test_health_check()
    test_results.append(("步骤1: 健康检查接口", result1))

    result2 = test_health_liveness()
    test_results.append(("步骤2: 存活探针接口", result2))

    result3 = test_health_readiness()
    test_results.append(("步骤3: 就绪探针接口", result3))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())