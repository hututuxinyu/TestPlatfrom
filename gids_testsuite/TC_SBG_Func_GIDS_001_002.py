#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_001_002.py
# 测试用例: GIDS宫格登录接口IMEI白名单校验测试

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://127.0.0.1:9090')
DEVICE_WHITE_IMEI = os.getenv('DEVICE_WHITE_IMEI', '6258412454025411')
DEVICE_BLACK_IMEI = os.getenv('DEVICE_BLACK_IMEI', '999999999999999')

def get_test_data(imei):
    return {
        "imsi": "685101555652111",
        "imei": imei,
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

def test_whiteimei_login():
    """步骤1: 白名单IMEI登录"""
    print("[INFO] ========== 测试步骤1: 白名单IMEI登录 ==========")
    
    test_data = get_test_data(DEVICE_WHITE_IMEI)
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        resp_json = response.json()
        
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 白名单IMEI登录成功")
            return True
        else:
            print(f"[FAIL] 白名单IMEI登录失败")
            print(f"[INFO] ErrorCode: {resp_json.get('code')}")
            print(f"[INFO] ErrorMessage: {resp_json.get('message', 'N/A')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_blackimei_login():
    """步骤2: 非白名单IMEI登录"""
    print("\n[INFO] ========== 测试步骤2: 非白名单IMEI登录 ==========")
    print(f"[INFO] IMEI: {DEVICE_BLACK_IMEI} (非白名单)")
    
    test_data = get_test_data(DEVICE_BLACK_IMEI)
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        resp_json = response.json()
        
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[FAIL] BUG: 非白名单IMEI居然登录成功!")
            print("[FAIL] 预期: 应拒绝非白名单IMEI")
            return False
        else:
            error_code = resp_json.get('code')
            error_msg = resp_json.get('message', '')
            
            if 'IMEI not allowed' in error_msg or 'not in whitelist' in error_msg.lower():
                print("[PASS] 正确拒绝非白名单IMEI")
                print(f"[INFO] ErrorCode: {error_code}")
                print(f"[INFO] ErrorMessage: {error_msg}")
                return True
            else:
                print(f"[WARN] 返回错误但消息不明确: {error_msg}")
                return True
                
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_emptyimei_login():
    """步骤3: 空IMEI登录"""
    print("\n[INFO] ========== 测试步骤3: 空IMEI登录 ==========")
    print(f"[INFO] IMEI: 空字符串")
    
    test_data = get_test_data("")
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        resp_json = response.json()
        
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[FAIL] BUG: 空IMEI居然登录成功!")
            return False
        else:
            print("[PASS] 正确拒绝空IMEI")
            return True
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_invalidimei_format():
    """步骤4: 格式错误的IMEI登录"""
    print("\n[INFO] ========== 测试步骤4: 格式错误的IMEI登录 ==========")
    print(f"[INFO] IMEI: ABCDEF123456789 (包含字母)")
    
    test_data = get_test_data("ABCDEF123456789")
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        resp_json = response.json()
        
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[FAIL] BUG: 格式错误的IMEI居然登录成功!")
            return False
        else:
            print("[PASS] 正确拒绝格式错误的IMEI")
            return True
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def main():
    print("""
==================================================================
    GIDS宫格登录接口IMEI白名单校验测试
    TC_SBG_Func_GIDS_001_002
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print(f"[INFO] 白名单IMEI: {DEVICE_WHITE_IMEI}")
    print(f"[INFO] 非白名单IMEI: {DEVICE_BLACK_IMEI}")
    print("")
    
    test_results = []
    
    result1 = test_whiteimei_login()
    test_results.append(("步骤1: 白名单IMEI登录", result1))
    
    result2 = test_blackimei_login()
    test_results.append(("步骤2: 非白名单IMEI登录", result2))
    
    result3 = test_emptyimei_login()
    test_results.append(("步骤3: 空IMEI登录", result3))
    
    result4 = test_invalidimei_format()
    test_results.append(("步骤4: 格式错误IMEI登录", result4))
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")
    
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())