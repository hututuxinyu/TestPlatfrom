#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Perf_GIDS_001_001.py
# 测试用例: GIDS性能测试 - 登录接口响应时间测试
# 目标: 验证 GIDS 登录接口在不同负载下的响应时间

import requests
import json
import sys
import os
import time
import statistics
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'https://135.27.173.13:40051')
REQUEST_COUNT = int(os.getenv('REQUEST_COUNT', '100'))  # 请求次数
CONCURRENT_USERS = int(os.getenv('CONCURRENT_USERS', '10'))  # 并发用户数

# ========== 性能阈值配置 ==========
RT_THRESHOLD_MS = 2000  # 响应时间阈值（毫秒）
SUCCESS_RATE_THRESHOLD = 95  # 成功率阈值（百分比）

def get_test_data():
    """生成测试数据"""
    return {
        "imsi": "685101555652111",
        "imei": "6258412454025411",
        "manufacturer": "Test Manufacturer",
        "model": "Test Model",
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

def single_request():
    """单次请求测试，返回响应时间（毫秒）和是否成功"""
    test_data = get_test_data()
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )
        end_time = time.time()
        
        rt_ms = (end_time - start_time) * 1000
        
        if response.status_code == 200 and response.json().get('code') == 200:
            return rt_ms, True
        else:
            return rt_ms, False
    except Exception as e:
        end_time = time.time()
        rt_ms = (end_time - start_time) * 1000
        return rt_ms, False

def test_response_time_single():
    """
    测试步骤1: 单次请求响应时间测试
    预期: 响应时间 < 阈值
    """
    print("[INFO] ========== 测试步骤1: 单次请求响应时间测试 ==========")
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    
    rt_ms, success = single_request()
    
    print(f"[INFO] 响应时间: {rt_ms:.2f} ms")
    print(f"[INFO] 请求结果: {'成功' if success else '失败'}")
    
    if rt_ms < RT_THRESHOLD_MS and success:
        print(f"[PASS] 单次请求响应时间测试通过 (阈值: {RT_THRESHOLD_MS}ms)")
        return True
    else:
        print(f"[FAIL] 单次请求响应时间测试失败")
        return False

def test_response_time_multiple():
    """
    测试步骤2: 多次请求响应时间测试
    预期: 平均响应时间 < 阈值，成功率 > 阈值
    """
    print("\n[INFO] ========== 测试步骤2: 多次请求响应时间测试 ==========")
    print(f"[INFO] 请求次数: {REQUEST_COUNT}")
    
    rt_list = []
    success_count = 0
    fail_count = 0
    
    for i in range(REQUEST_COUNT):
        rt_ms, success = single_request()
        rt_list.append(rt_ms)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # 每10次打印进度
        if (i + 1) % 10 == 0:
            print(f"[INFO] 进度: {i + 1}/{REQUEST_COUNT}, 当前RT: {rt_ms:.2f}ms")
    
    # 统计分析
    avg_rt = statistics.mean(rt_list)
    max_rt = max(rt_list)
    min_rt = min(rt_list)
    p50_rt = statistics.median(rt_list)
    p95_rt = sorted(rt_list)[int(len(rt_list) * 0.95)] if len(rt_list) > 20 else max(rt_list)
    success_rate = (success_count / REQUEST_COUNT) * 100
    
    print("\n[INFO] ========== 性能统计结果 ==========")
    print(f"[INFO] 平均响应时间: {avg_rt:.2f} ms")
    print(f"[INFO] 最小响应时间: {min_rt:.2f} ms")
    print(f"[INFO] 最大响应时间: {max_rt:.2f} ms")
    print(f"[INFO] P50响应时间:  {p50_rt:.2f} ms")
    print(f"[INFO] P95响应时间:  {p95_rt:.2f} ms")
    print(f"[INFO] 成功次数: {success_count}/{REQUEST_COUNT}")
    print(f"[INFO] 成功率: {success_rate:.2f}%")
    
    # 判断测试结果
    pass_avg_rt = avg_rt < RT_THRESHOLD_MS
    pass_success_rate = success_rate >= SUCCESS_RATE_THRESHOLD
    
    print("\n[INFO] ========== 测试判定 ==========")
    if pass_avg_rt:
        print(f"[PASS] 平均响应时间 {avg_rt:.2f}ms < 阈值 {RT_THRESHOLD_MS}ms")
    else:
        print(f"[FAIL] 平均响应时间 {avg_rt:.2f}ms >= 阈值 {RT_THRESHOLD_MS}ms")
    
    if pass_success_rate:
        print(f"[PASS] 成功率 {success_rate:.2f}% >= 阈值 {SUCCESS_RATE_THRESHOLD}%")
    else:
        print(f"[FAIL] 成功率 {success_rate:.2f}% < 阈值 {SUCCESS_RATE_THRESHOLD}%")
    
    return pass_avg_rt and pass_success_rate

def test_concurrent_requests():
    """
    测试步骤3: 并发请求测试
    预期: 并发场景下响应时间稳定
    """
    print("\n[INFO] ========== 测试步骤3: 并发请求测试 ==========")
    print(f"[INFO] 并发用户数: {CONCURRENT_USERS}")
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    rt_list = []
    success_count = 0
    
    def concurrent_request(index):
        rt_ms, success = single_request()
        return index, rt_ms, success
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = [executor.submit(concurrent_request, i) for i in range(CONCURRENT_USERS)]
        
        for future in as_completed(futures):
            index, rt_ms, success = future.result()
            rt_list.append(rt_ms)
            if success:
                success_count += 1
            print(f"[INFO] 并发请求 {index + 1}: RT={rt_ms:.2f}ms, 结果={'成功' if success else '失败'}")
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    
    avg_rt = statistics.mean(rt_list)
    success_rate = (success_count / CONCURRENT_USERS) * 100
    qps = CONCURRENT_USERS / (total_time / 1000)
    
    print("\n[INFO] ========== 并发测试统计 ==========")
    print(f"[INFO] 总耗时: {total_time:.2f} ms")
    print(f"[INFO] 平均响应时间: {avg_rt:.2f} ms")
    print(f"[INFO] 成功率: {success_rate:.2f}%")
    print(f"[INFO] 估算QPS: {qps:.2f} req/s")
    
    pass_avg_rt = avg_rt < RT_THRESHOLD_MS * 2  # 并发时阈值放宽
    pass_success_rate = success_rate >= SUCCESS_RATE_THRESHOLD
    
    if pass_avg_rt and pass_success_rate:
        print(f"[PASS] 并发请求测试通过")
        return True
    else:
        print(f"[FAIL] 并发请求测试失败")
        return False

def main():
    print("""
==================================================================
    GIDS性能测试 - 登录接口响应时间测试
    TC_SBG_Perf_GIDS_001_001
==================================================================
    """)
    print(f"[INFO] 测试配置:")
    print(f"[INFO]   GIDS地址: {GIDS_ADDR}")
    print(f"[INFO]   请求次数: {REQUEST_COUNT}")
    print(f"[INFO]   并发用户数: {CONCURRENT_USERS}")
    print(f"[INFO]   RT阈值: {RT_THRESHOLD_MS}ms")
    print(f"[INFO]   成功率阈值: {SUCCESS_RATE_THRESHOLD}%")
    print("")
    
    test_results = []
    
    result1 = test_response_time_single()
    test_results.append(("步骤1: 单次请求响应时间测试", result1))
    
    result2 = test_response_time_multiple()
    test_results.append(("步骤2: 多次请求响应时间测试", result2))
    
    result3 = test_concurrent_requests()
    test_results.append(("步骤3: 并发请求测试", result3))
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")
    
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 性能测试完成 ==========")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())