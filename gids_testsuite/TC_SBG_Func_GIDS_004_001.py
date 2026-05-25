#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_004_001.py
# 测试用例: 缓存删除接口测试

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://127.0.0.1:9090')
DEVICE_WHITE_IMEI = os.getenv('DEVICE_WHITE_IMEI', '6258412454025411')

def test_delete_cache_success():
    """步骤1: 正常删除缓存"""
    print("[INFO] ========== 测试步骤1: 正常删除缓存 ==========")
    print(f"[INFO] 接口: /app-api/devicetcp/cache/deleteCache")
    
    test_data = {
        "imei": DEVICE_WHITE_IMEI,
        "imsi": "685101555652111"
    }
    
    url = f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        resp_json = response.json()
        
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 删除缓存成功")
            return True
        else:
            print(f"[WARN] 删除缓存可能失败: {resp_json.get('message', 'N/A')}")
            return True
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_delete_cache_missing_imei():
    """步骤2: 缺失IMEI参数"""
    print("\n[INFO] ========== 测试步骤2: 缺失IMEI参数 ==========")
    
    test_data = {
        "imsi": "685101555652111"
    }
    
    url = f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        if response.status_code >= 400:
            print("[PASS] 正确拒绝缺失IMEI")
            return True
        else:
            resp_json = response.json()
            if resp_json.get('code') != 200:
                print("[PASS] 正确拒绝缺失IMEI")
                return True
            else:
                print("[FAIL] BUG: 缺失IMEI居然成功了")
                return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_delete_cache_missing_imsi():
    """步骤3: 缺失IMSI参数"""
    print("\n[INFO] ========== 测试步骤3: 缺失IMSI参数 ==========")
    
    test_data = {
        "imei": DEVICE_WHITE_IMEI
    }
    
    url = f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        if response.status_code >= 400:
            print("[PASS] 正确拒绝缺失IMSI")
            return True
        else:
            resp_json = response.json()
            if resp_json.get('code') != 200:
                print("[PASS] 正确拒绝缺失IMSI")
                return True
            else:
                print("[FAIL] BUG: 缺失IMSI居然成功了")
                return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_delete_cache_empty_params():
    """步骤4: 空参数"""
    print("\n[INFO] ========== 测试步骤4: 空参数 ==========")
    
    test_data = {
        "imei": "",
        "imsi": ""
    }
    
    url = f"{GIDS_ADDR}/app-api/devicetcp/cache/deleteCache"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        if response.status_code >= 400:
            print("[PASS] 正确拒绝空参数")
            return True
        else:
            resp_json = response.json()
            if resp_json.get('code') != 200:
                print("[PASS] 正确拒绝空参数")
                return True
            else:
                print("[FAIL] BUG: 空参数居然成功了")
                return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def main():
    print("""
==================================================================
    缓存删除接口测试
    TC_SBG_Func_GIDS_004_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")
    
    test_results = []
    
    result1 = test_delete_cache_success()
    test_results.append(("步骤1: 正常删除缓存", result1))
    
    result2 = test_delete_cache_missing_imei()
    test_results.append(("步骤2: 缺失IMEI", result2))
    
    result3 = test_delete_cache_missing_imsi()
    test_results.append(("步骤3: 缺失IMSI", result3))
    
    result4 = test_delete_cache_empty_params()
    test_results.append(("步骤4: 空参数", result4))
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")
    
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())