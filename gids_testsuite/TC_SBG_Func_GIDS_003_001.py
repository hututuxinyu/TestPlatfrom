#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_003_001.py
# 测试用例: 客户端事件上报接口测试

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://127.0.0.1:9090')
DEVICE_WHITE_IMEI = os.getenv('DEVICE_WHITE_IMEI', '6258412454025411')

def test_send_client_event_success():
    """步骤1: 正常上报客户端事件"""
    print("[INFO] ========== 测试步骤1: 正常上报客户端事件 ==========")
    print(f"[INFO] 接口: /app-api/center/public/client/sendClientEvent")
    
    test_data = {
        "hsman": "test_manufacturer",
        "hstype": "test_model",
        "appType": "1",
        "imei": DEVICE_WHITE_IMEI,
        "imsi": "685101555652111",
        "type": "login"
    }
    
    url = f"{GIDS_ADDR}/app-api/center/public/client/sendClientEvent"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        resp_json = response.json()
        
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 客户端事件上报成功")
            return True
        else:
            print(f"[FAIL] 事件上报失败: {resp_json.get('message', 'N/A')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_send_client_event_missing_fields():
    """步骤2: 缺失必选字段"""
    print("\n[INFO] ========== 测试步骤2: 缺失IMEI字段 ==========")
    
    test_data = {
        "hsman": "test_manufacturer",
        "hstype": "test_model",
        "appType": "1",
        "imsi": "685101555652111",
        "type": "login"
    }
    
    url = f"{GIDS_ADDR}/app-api/center/public/client/sendClientEvent"
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

def test_send_app_use_times_event():
    """步骤3: 应用使用时长事件上报"""
    print("\n[INFO] ========== 测试步骤3: 应用使用时长事件上报 ==========")
    print(f"[INFO] 接口: /app-api/center/public/client/sendAppUseTimesEvent")
    
    test_data = {
        "useTimes": "3600",
        "hsman": "test_manufacturer",
        "hstype": "test_model",
        "exttype": "default",
        "appType": "1",
        "appId": "test_app_001",
        "scheight": "1920",
        "scwidth": "1080",
        "imei": DEVICE_WHITE_IMEI,
        "imsi": "685101555652111",
        "playMode": "1"
    }
    
    url = f"{GIDS_ADDR}/app-api/center/public/client/sendAppUseTimesEvent"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        resp_json = response.json()
        
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 应用使用时长事件上报成功")
            return True
        else:
            print(f"[FAIL] 事件上报失败")
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
    客户端事件上报接口测试
    TC_SBG_Func_GIDS_003_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")
    
    test_results = []
    
    result1 = test_send_client_event_success()
    test_results.append(("步骤1: 正常上报客户端事件", result1))
    
    result2 = test_send_client_event_missing_fields()
    test_results.append(("步骤2: 缺失IMEI字段", result2))
    
    result3 = test_send_app_use_times_event()
    test_results.append(("步骤3: 应用使用时长事件", result3))
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")
    
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())