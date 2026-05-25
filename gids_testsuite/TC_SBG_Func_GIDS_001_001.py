#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_001_001.py
# 测试用例: GIDS宫格登录接口正常流程测试

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://127.0.0.1:9090')
DEVICE_WHITE_IMEI = os.getenv('DEVICE_WHITE_IMEI', '625841245402541')

TEST_DATA_VALID = {
    "imsi": "685101555652111",
    "imei": "625841245402541",
    "manufacturer": "test_manufacturer",
    "model": "test_model",
    "appType": "1",
    "extendModel": "default",
    "country": "CN",
    "platform": "android",
    "width": "1080",
    "height": "1920",
    "mcc": "460",
    "mnc": "00",
    "lac": "10000",
    "ci": "12345",
    "rxlev": "-75",
    "totalKb": "1024000",
    "freeKb": "512000",
    "clientLanguage": "zh",
    "deviceType": "1000"
}

def test_grid_login_auth():
    """步骤1: 测试 gridLoginAuth 接口"""
    print("[INFO] ========== 测试步骤1: gridLoginAuth 接口 ==========")
    
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuth"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(TEST_DATA_VALID, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=TEST_DATA_VALID, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        if response.status_code in [200, 201]:
            resp_json = response.json()
            if resp_json.get('code') == 200:
                print("[PASS] gridLoginAuth 接口调用成功")
                print(f"[INFO] 响应Message: {resp_json.get('message', 'N/A')}")
                return True
            else:
                print(f"[FAIL] 返回错误码: {resp_json.get('code')}")
                print(f"[FAIL] 错误信息: {resp_json.get('message', 'N/A')}")
                return False
        else:
            print(f"[FAIL] HTTP状态码异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except requests.exceptions.Timeout:
        print(f"[ERROR] 请求超时")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_grid_login_auth_open_browser():
    """步骤2: 测试 gridLoginAuthOpenBrowser 接口"""
    print("\n[INFO] ========== 测试步骤2: gridLoginAuthOpenBrowser 接口 ==========")
    
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(TEST_DATA_VALID, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=TEST_DATA_VALID, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        if response.status_code in [200, 201]:
            resp_json = response.json()
            if resp_json.get('code') == 200:
                print("[PASS] gridLoginAuthOpenBrowser 接口调用成功")
                data = resp_json.get('data', {})
                print(f"[INFO] Token: {data.get('token', 'N/A')}")
                print(f"[INFO] NodeGateWayURL: {data.get('nodeGateWayUrl', 'N/A')}")
                return True
            else:
                print(f"[FAIL] 返回错误码: {resp_json.get('code')}")
                return False
        else:
            print(f"[FAIL] HTTP状态码异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_device_login_auth():
    """步骤3: 测试 deviceLoginAuth 接口"""
    print("\n[INFO] ========== 测试步骤3: deviceLoginAuth 接口 ==========")
    
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/deviceLoginAuth"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(TEST_DATA_VALID, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=TEST_DATA_VALID, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        if response.status_code in [200, 201]:
            resp_json = response.json()
            if resp_json.get('code') == 200:
                print("[PASS] deviceLoginAuth 接口调用成功")
                return True
            else:
                print(f"[FAIL] 返回错误码: {resp_json.get('code')}")
                return False
        else:
            print(f"[FAIL] HTTP状态码异常: {response.status_code}")
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
    GIDS宫格登录接口正常流程测试
    TC_SBG_Func_GIDS_001_001
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")
    
    test_results = []
    
    result1 = test_grid_login_auth()
    test_results.append(("步骤1: gridLoginAuth", result1))
    
    result2 = test_grid_login_auth_open_browser()
    test_results.append(("步骤2: gridLoginAuthOpenBrowser", result2))
    
    result3 = test_device_login_auth()
    test_results.append(("步骤3: deviceLoginAuth", result3))
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")
    
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())