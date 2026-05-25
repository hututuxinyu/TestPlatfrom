#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_001_003.py
# 测试用例: GIDS宫格登录接口必选参数缺失测试

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://127.0.0.1:9090')
DEVICE_WHITE_IMEI = os.getenv('DEVICE_WHITE_IMEI', '6258412454025411')

FULL_DATA = {
    "imsi": "685101555652111",
    "imei": "6258412454025411",
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

def test_missing_imsi():
    """步骤1: 缺失IMSI参数"""
    print("[INFO] ========== 测试步骤1: 缺失IMSI参数 ==========")
    
    test_data = FULL_DATA.copy()
    del test_data['imsi']
    
    print(f"[INFO] 请求参数(无imsi): {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        resp_json = response.json()
        
        if response.status_code == 400 or resp_json.get('code') != 200:
            print("[PASS] 正确拒绝缺失IMSI的请求")
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

def test_missing_imei():
    """步骤2: 缺失IMEI参数"""
    print("\n[INFO] ========== 测试步骤2: 缺失IMEI参数 ==========")
    
    test_data = FULL_DATA.copy()
    del test_data['imei']
    
    print(f"[INFO] 请求参数(无imei)")
    
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        resp_json = response.json()
        
        if response.status_code == 400 or resp_json.get('code') != 200:
            print("[PASS] 正确拒绝缺失IMEI的请求")
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

def test_missing_both_imsi_imei():
    """步骤3: 缺失IMSI和IMEI参数"""
    print("\n[INFO] ========== 测试步骤3: 缺失IMSI和IMEI参数 ==========")
    
    test_data = FULL_DATA.copy()
    del test_data['imsi']
    del test_data['imei']
    
    print(f"[INFO] 请求参数(无imsi和imei)")
    
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data,
            timeout=30,
            verify=False
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        resp_json = response.json()
        
        if response.status_code == 400 or resp_json.get('code') != 200:
            print("[PASS] 正确拒绝缺失必选参数的请求")
            return True
        else:
            print("[FAIL] BUG: 缺失必选参数居然成功了")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_empty_body():
    """步骤4: 空请求体"""
    print("\n[INFO] ========== 测试步骤4: 空请求体 ==========")
    
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json={},
            timeout=30,
            verify=False
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        if response.status_code >= 400:
            print("[PASS] 正确拒绝空请求体")
            return True
        else:
            resp_json = response.json()
            if resp_json.get('code') != 200:
                print("[PASS] 正确拒绝空请求体")
                return True
            else:
                print("[FAIL] BUG: 空请求体居然成功了")
                return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 连接失败")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_full_params():
    """步骤5: 全量参数正常请求"""
    print("\n[INFO] ========== 测试步骤5: 全量参数正常请求 ==========")
    
    print(f"[INFO] 请求参数: 全量参数")
    
    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=FULL_DATA,
            timeout=30,
            verify=False
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        resp_json = response.json()
        
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 全量参数请求成功")
            return True
        else:
            print("[FAIL] 全量参数请求失败")
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
    GIDS宫格登录接口必选参数缺失测试
    TC_SBG_Func_GIDS_001_003
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")
    
    test_results = []
    
    result1 = test_missing_imsi()
    test_results.append(("步骤1: 缺失IMSI", result1))
    
    result2 = test_missing_imei()
    test_results.append(("步骤2: 缺失IMEI", result2))
    
    result3 = test_missing_both_imsi_imei()
    test_results.append(("步骤3: 缺失IMSI+IMEI", result3))
    
    result4 = test_empty_body()
    test_results.append(("步骤4: 空请求体", result4))
    
    result5 = test_full_params()
    test_results.append(("步骤5: 全量参数", result5))
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")
    
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())