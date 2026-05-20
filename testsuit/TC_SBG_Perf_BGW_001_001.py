#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Perf_BGW_001_001.py
# 测试用例: BrowserGateway性能测试 - HTTP接口响应时间测试
# 目标: 验证 BrowserGateway HTTP接口在不同负载下的响应时间

import requests
import json
import sys
import os
import time
import statistics
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
BGW_ADDR = os.getenv('BGW_ADDR', 'http://127.0.0.1:8090')
REQUEST_COUNT = int(os.getenv('REQUEST_COUNT', '100'))
CONCURRENT_USERS = int(os.getenv('CONCURRENT_USERS', '10'))
DURATION_SECONDS = int(os.getenv('DURATION_SECONDS', '30'))  # 持续压测时间

# ========== 性能阈值配置 ==========
RT_THRESHOLD_MS = 1000  # HTTP接口响应时间阈值
SUCCESS_RATE_THRESHOLD = 95

def test_health_check_performance():
    """
    测试步骤1: 健康检查接口性能测试
    预期: 响应时间 < 阈值
    """
    print("[INFO] ========== 测试步骤1: 健康检查接口性能测试 ==========")
    
    rt_list = []
    success_count = 0
    
    for i in range(REQUEST_COUNT):
        start_time = time.time()
        try:
            response = requests.get(
                f"{BGW_ADDR}/actuator/health",
                timeout=10,
                verify=False
            )
            end_time = time.time()
            rt_ms = (end_time - start_time) * 1000
            rt_list.append(rt_ms)
            
            if response.status_code == 200:
                success_count += 1
        except Exception as e:
            rt_list.append(10000)  # 超时计为10秒
    
    avg_rt = statistics.mean(rt_list)
    success_rate = (success_count / REQUEST_COUNT) * 100
    
    print(f"[INFO] 请求次数: {REQUEST_COUNT}")
    print(f"[INFO] 平均响应时间: {avg_rt:.2f} ms")
    print(f"[INFO] 成功率: {success_rate:.2f}%")
    
    if avg_rt < RT_THRESHOLD_MS and success_rate >= SUCCESS_RATE_THRESHOLD:
        print("[PASS] 健康检查接口性能测试通过")
        return True
    else:
        print("[FAIL] 健康检查接口性能测试失败")
        return False

def test_delete_userdata_performance():
    """
    测试步骤2: 删除用户数据接口性能测试
    预期: 响应时间 < 阈值
    """
    print("\n[INFO] ========== 测试步骤2: 删除用户数据接口性能测试 ==========")
    
    rt_list = []
    success_count = 0
    
    for i in range(REQUEST_COUNT):
        test_data = {
            "imei": f"6258412454025{i:04d}",
            "imsi": f"68510155565{i:04d}"
        }
        
        start_time = time.time()
        try:
            response = requests.delete(
                f"{BGW_ADDR}/browsergw/browser/userdata/delete",
                json=test_data,
                timeout=10,
                verify=False
            )
            end_time = time.time()
            rt_ms = (end_time - start_time) * 1000
            rt_list.append(rt_ms)
            
            if response.status_code == 200:
                success_count += 1
        except Exception as e:
            rt_list.append(10000)
    
    avg_rt = statistics.mean(rt_list)
    p95_rt = sorted(rt_list)[int(len(rt_list) * 0.95)] if len(rt_list) > 20 else max(rt_list)
    success_rate = (success_count / REQUEST_COUNT) * 100
    
    print(f"[INFO] 请求次数: {REQUEST_COUNT}")
    print(f"[INFO] 平均响应时间: {avg_rt:.2f} ms")
    print(f"[INFO] P95响应时间: {p95_rt:.2f} ms")
    print(f"[INFO] 成功率: {success_rate:.2f}%")
    
    if avg_rt < RT_THRESHOLD_MS * 2 and success_rate >= SUCCESS_RATE_THRESHOLD:
        print("[PASS] 删除用户数据接口性能测试通过")
        return True
    else:
        print("[FAIL] 删除用户数据接口性能测试失败")
        return False

def test_plugin_info_performance():
    """
    测试步骤3: 获取插件信息接口性能测试
    预期: 响应时间 < 阈值
    """
    print("\n[INFO] ========== 测试步骤3: 获取插件信息接口性能测试 ==========")
    
    rt_list = []
    success_count = 0
    
    for i in range(REQUEST_COUNT):
        start_time = time.time()
        try:
            response = requests.get(
                f"{BGW_ADDR}/browsergw/extension/pluginInfo",
                timeout=10,
                verify=False
            )
            end_time = time.time()
            rt_ms = (end_time - start_time) * 1000
            rt_list.append(rt_ms)
            
            if response.status_code == 200 and response.json().get('code') == 200:
                success_count += 1
        except Exception as e:
            rt_list.append(10000)
    
    avg_rt = statistics.mean(rt_list)
    success_rate = (success_count / REQUEST_COUNT) * 100
    
    print(f"[INFO] 请求次数: {REQUEST_COUNT}")
    print(f"[INFO] 平均响应时间: {avg_rt:.2f} ms")
    print(f"[INFO] 成功率: {success_rate:.2f}%")
    
    if avg_rt < RT_THRESHOLD_MS and success_rate >= SUCCESS_RATE_THRESHOLD:
        print("[PASS] 获取插件信息接口性能测试通过")
        return True
    else:
        print("[FAIL] 获取插件信息接口性能测试失败")
        return False

def test_concurrent_stress():
    """
    测试步骤4: 并发压力测试
    预期: 系统在高并发下稳定运行
    """
    print("\n[INFO] ========== 测试步骤4: 并发压力测试 ==========")
    print(f"[INFO] 并发数: {CONCURRENT_USERS}, 持续时间: {DURATION_SECONDS}s")
    
    total_requests = 0
    success_count = 0
    fail_count = 0
    rt_list = []
    
    def stress_request():
        nonlocal total_requests, success_count, fail_count
        
        test_data = {
            "imei": f"6258412454025{total_requests:06d}",
            "imsi": f"68510155565{total_requests:06d}"
        }
        
        start_time = time.time()
        try:
            response = requests.delete(
                f"{BGW_ADDR}/browsergw/browser/userdata/delete",
                json=test_data,
                timeout=5,
                verify=False
            )
            end_time = time.time()
            rt_ms = (end_time - start_time) * 1000
            
            total_requests += 1
            if response.status_code == 200:
                success_count += 1
                return rt_ms, True
            else:
                fail_count += 1
                return rt_ms, False
        except Exception as e:
            total_requests += 1
            fail_count += 1
            return 5000, False
    
    start_time = time.time()
    end_time = start_time + DURATION_SECONDS
    
    while time.time() < end_time:
        with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
            futures = [executor.submit(stress_request) for _ in range(CONCURRENT_USERS)]
            for future in as_completed(futures):
                rt_ms, success = future.result()
                rt_list.append(rt_ms)
        
        # 打印进度
        elapsed = time.time() - start_time
        print(f"[INFO] 已运行 {elapsed:.1f}s, 请求数: {total_requests}, 成功: {success_count}, 失败: {fail_count}")
    
    actual_duration = time.time() - start_time
    avg_rt = statistics.mean(rt_list) if rt_list else 0
    success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
    qps = total_requests / actual_duration
    
    print("\n[INFO] ========== 压力测试统计 ==========")
    print(f"[INFO] 总请求数: {total_requests}")
    print(f"[INFO] 成功数: {success_count}")
    print(f"[INFO] 失败数: {fail_count}")
    print(f"[INFO] 实际QPS: {qps:.2f} req/s")
    print(f"[INFO] 平均响应时间: {avg_rt:.2f} ms")
    print(f"[INFO] 成功率: {success_rate:.2f}%")
    
    # 性能判定
    pass_qps = qps > 10  # QPS大于10
    pass_success_rate = success_rate >= 90  # 压测成功率放宽到90%
    
    if pass_qps and pass_success_rate:
        print("[PASS] 并发压力测试通过")
        return True
    else:
        print("[FAIL] 并发压力测试失败")
        return False

def main():
    print("""
==================================================================
    BrowserGateway性能测试 - HTTP接口响应时间测试
    TC_SBG_Perf_BGW_001_001
==================================================================
    """)
    print(f"[INFO] 测试配置:")
    print(f"[INFO]   BGW地址: {BGW_ADDR}")
    print(f"[INFO]   请求次数: {REQUEST_COUNT}")
    print(f"[INFO]   并发用户数: {CONCURRENT_USERS}")
    print(f"[INFO]   压测时长: {DURATION_SECONDS}s")
    print(f"[INFO]   RT阈值: {RT_THRESHOLD_MS}ms")
    print("")
    
    test_results = []
    
    result1 = test_health_check_performance()
    test_results.append(("步骤1: 健康检查接口性能", result1))
    
    result2 = test_delete_userdata_performance()
    test_results.append(("步骤2: 删除用户数据接口性能", result2))
    
    result3 = test_plugin_info_performance()
    test_results.append(("步骤3: 获取插件信息接口性能", result3))
    
    result4 = test_concurrent_stress()
    test_results.append(("步骤4: 并发压力测试", result4))
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")
    
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 性能测试完成 ==========")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())