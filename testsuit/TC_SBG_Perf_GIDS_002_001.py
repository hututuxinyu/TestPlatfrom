#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Perf_GIDS_002_001.py
# 测试用例: GIDS稳定性测试 - 长时间运行测试
# 目标: 验证 GIDS 在长时间运行下的稳定性

import requests
import json
import sys
import os
import time
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')
TEST_DURATION_MINUTES = int(os.getenv('TEST_DURATION_MINUTES', '5'))  # 测试时长（分钟）
REQUEST_INTERVAL_SECONDS = int(os.getenv('REQUEST_INTERVAL_SECONDS', '10'))  # 请求间隔

def get_test_data(index):
    """生成测试数据"""
    return {
        "imsi": f"68510155565{index:04d}",
        "imei": f"62584124540{index:04d}",
        "manufacturer": "StabilityTest",
        "model": "TestModel",
        "appType": "1",
        "extendModel": "default",
        "country": "CN",
        "platform": "android",
        "width": "1080",
        "height": "1920",
        "mcc": "460",
        "mnc": "00",
        "lac": "100",
        "ci": "5210",
        "rxlev": "-72",
        "totalKb": "1424122",
        "freeKb": "1424122",
        "clientLanguage": "zh",
        "deviceType": "1000"
    }

def test_stability_long_running():
    """
    测试步骤1: 长时间运行稳定性测试
    预期: 系统在测试期间稳定运行，无异常中断
    """
    print("[INFO] ========== 测试步骤1: 长时间运行稳定性测试 ==========")
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print(f"[INFO] 测试时长: {TEST_DURATION_MINUTES} 分钟")
    print(f"[INFO] 请求间隔: {REQUEST_INTERVAL_SECONDS} 秒")
    
    total_requests = 0
    success_count = 0
    fail_count = 0
    rt_list = []
    error_list = []
    
    start_time = time.time()
    end_time = start_time + TEST_DURATION_MINUTES * 60
    request_index = 0
    
    print(f"[INFO] 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[INFO] 预计结束时间: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
    
    while time.time() < end_time:
        test_data = get_test_data(request_index)
        request_start = time.time()
        
        try:
            response = requests.post(
                f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
                json=test_data,
                timeout=30,
                verify=False
            )
            request_end = time.time()
            rt_ms = (request_end - request_start) * 1000
            
            total_requests += 1
            rt_list.append(rt_ms)
            
            if response.status_code == 200 and response.json().get('code') == 200:
                success_count += 1
                status = "SUCCESS"
            else:
                fail_count += 1
                status = f"FAIL(code={response.json().get('code')})"
                error_list.append(response.json().get('message', 'unknown'))
        except requests.exceptions.Timeout:
            total_requests += 1
            fail_count += 1
            rt_list.append(30000)
            status = "TIMEOUT"
            error_list.append("timeout")
        except requests.exceptions.ConnectionError as e:
            total_requests += 1
            fail_count += 1
            rt_list.append(0)
            status = "CONN_ERROR"
            error_list.append(str(e))
        except Exception as e:
            total_requests += 1
            fail_count += 1
            rt_list.append(0)
            status = f"ERROR({str(e)[:50]})"
            error_list.append(str(e))
        
        elapsed = time.time() - start_time
        remaining = end_time - time.time()
        
        print(f"[INFO] [{datetime.now().strftime('%H:%M:%S')}] "
              f"请求#{total_requests}: RT={rt_list[-1]:.0f}ms, {status} | "
              f"已运行{elapsed:.0f}s, 剩余{remaining:.0f}s")
        
        request_index += 1
        time.sleep(REQUEST_INTERVAL_SECONDS)
    
    # 统计结果
    actual_duration = time.time() - start_time
    avg_rt = sum(rt_list) / len(rt_list) if rt_list else 0
    max_rt = max(rt_list) if rt_list else 0
    min_rt = min(rt_list) if rt_list else 0
    success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
    
    print("\n[INFO] ========== 稳定性测试统计 ==========")
    print(f"[INFO] 实际运行时长: {actual_duration:.1f} 秒 ({actual_duration/60:.1f} 分钟)")
    print(f"[INFO] 总请求数: {total_requests}")
    print(f"[INFO] 成功数: {success_count}")
    print(f"[INFO] 失败数: {fail_count}")
    print(f"[INFO] 成功率: {success_rate:.2f}%")
    print(f"[INFO] 平均响应时间: {avg_rt:.2f} ms")
    print(f"[INFO] 最小响应时间: {min_rt:.2f} ms")
    print(f"[INFO] 最大响应时间: {max_rt:.2f} ms")
    
    if error_list:
        print(f"[INFO] 错误类型统计:")
        unique_errors = set(error_list)
        for err in unique_errors:
            count = error_list.count(err)
            print(f"[INFO]   - {err[:50]}: {count}次")
    
    # 判定标准
    pass_no_crash = total_requests > 0  # 系统未崩溃
    pass_success_rate = success_rate >= 90  # 成功率 >= 90%
    pass_rt_stable = max_rt < 30000  # 最大RT < 30秒
    
    print("\n[INFO] ========== 测试判定 ==========")
    if pass_no_crash:
        print("[PASS] 系统持续运行，未崩溃")
    else:
        print("[FAIL] 系统崩溃或无法连接")
    
    if pass_success_rate:
        print(f"[PASS] 成功率 {success_rate:.2f}% >= 90%")
    else:
        print(f"[FAIL] 成功率 {success_rate:.2f}% < 90%")
    
    if pass_rt_stable:
        print(f"[PASS] 最大响应时间 {max_rt:.0f}ms < 30s，响应稳定")
    else:
        print(f"[FAIL] 最大响应时间 {max_rt:.0f}ms >= 30s，存在超时")
    
    return pass_no_crash and pass_success_rate and pass_rt_stable

def main():
    print("""
==================================================================
    GIDS稳定性测试 - 长时间运行测试
    TC_SBG_Perf_GIDS_002_001
==================================================================
    """)
    
    test_results = []
    
    result1 = test_stability_long_running()
    test_results.append(("步骤1: 长时间运行稳定性测试", result1))
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")
    
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 稳定性测试完成 ==========")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())