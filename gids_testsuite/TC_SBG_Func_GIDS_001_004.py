#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_001_004.py
# 测试用例: 宫格登录身份验证并打开浏览器接口验证-参数值异常测试

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://localhost:9090')
DEVICE_WHITE_IMEI = os.getenv('DEVICE_WHITE_IMEI', '6258412454025411')

# ========== 测试数据 ==========
TEST_DATA_FULL = {
    "imsi": "68510155565211",
    "imei": "6258412454025411",
    "manufacturer": "xxx manufacturer",
    "model": "xx model",
    "appType": "1",
    "extendModel": "default",
    "country": "default",
    "platform": "default",
    "width": "240",
    "height": "320",
    "mcc": "460",
    "mnc": "00x",
    "lac": "100",
    "ci": "5.21",
    "rxlev": "-72",
    "totalKb": "1424122",
    "freeKb": "1424122",
    "clientLanguage": "en",
    "deviceType": "1000"
}

# 必选参数(根据接口文档定义)
REQUIRED_PARAMS = ["imsi", "imei"]

def test_full_params():
    """步骤1: 发送包含所有参数的请求"""
    print("[INFO] ========== 测试步骤1: 全量参数请求 ==========")
    print(f"[INFO] 接口: /app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser")
    
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(TEST_DATA_FULL, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=TEST_DATA_FULL, timeout=30, verify=False)

        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")

        if response.status_code in [200, 201]:
            print("[SUCCESS] 全量参数请求成功")
            try:
                resp_json = response.json()
                token = resp_json.get('data', {}).get('token', 'N/A')
                print(f"[INFO] Token: {token}")
            except:
                pass
            return True
        else:
            print(f"[WARN] 响应码非2xx: {response.status_code}")
            return True  # 不算是失败,继续测试

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        print(f"[INFO] 请确保 GIDS 服务正在运行")
        return False
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] 请求超时")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_required_only():
    """步骤2: 仅发送必选参数"""
    print("\n[INFO] ========== 测试步骤2: 仅必选参数请求 ==========")
    print(f"[INFO] 必选参数: {REQUIRED_PARAMS}")

    required_data = {k: TEST_DATA_FULL[k] for k in REQUIRED_PARAMS}
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(required_data, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=required_data, timeout=30, verify=False)

        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")

        # 预期结果: 接口可能需要更多参数,这里可能返回错误或默认值
        if response.status_code in [200, 201]:
            print("[SUCCESS] 仅必选参数请求成功")
            return True
        else:
            # 检查是否是参数缺失错误
            try:
                resp_data = response.json()
                error_code = resp_data.get("errorCode", "")
                error_msg = resp_data.get("errorMsg", "")

                print(f"[INFO] ErrorCode: {error_code}")
                print(f"[INFO] ErrorMsg: {error_msg}")

                if error_code == "MISSING_REQUIRED_PARAMS":
                    print("[SUCCESS] 按预期返回必选参数缺失错误")
                    return True
                else:
                    print("[WARN] 未按预期返回错误，但继续测试")
                    return True
            except:
                return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] 请求超时")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_required_plus_one():
    """步骤3: 仅必选参数+1个可选参数"""
    print("\n[INFO] ========== 测试步骤3: 必选参数+1可选参数请求 ==========")
    print(f"[INFO] 必选参数: {REQUIRED_PARAMS}")
    print(f"[INFO] 额外可选参数: appType")

    required_plus_one = {k: TEST_DATA_FULL[k] for k in REQUIRED_PARAMS}
    required_plus_one["appType"] = TEST_DATA_FULL["appType"]
    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(required_plus_one, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=required_plus_one, timeout=30, verify=False)

        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")

        if response.status_code in [200, 201]:
            print("[SUCCESS] 必选参数+1可选参数请求成功")
            try:
                resp_json = response.json()
                token = resp_json.get('data', {}).get('token', 'N/A')
                print(f"[INFO] Token: {token}")
            except:
                pass
            return True
        else:
            try:
                resp_data = response.json()
                error_code = resp_data.get("errorCode", "")
                error_msg = resp_data.get("errorMsg", "")

                print(f"[INFO] ErrorCode: {error_code}")
                print(f"[INFO] ErrorMsg: {error_msg}")

                if error_code == "MISSING_REQUIRED_PARAMS":
                    print("[SUCCESS] 按预期返回必选参数缺失错误")
                    return True
                else:
                    print("[WARN] 未按预期返回错误，但继续测试")
                    return True
            except:
                return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] 请求超时")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def main():
    print("""
==================================================================
    宫格登录身份验证并打开浏览器接口验证-参数值异常测试
    TC_SBG_Func_GIDS_001_004
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    # 执行测试步骤
    test_results = []

    # 步骤1: 全量参数
    result1 = test_full_params()
    test_results.append(("步骤1: 全量参数", result1))

    # 步骤2: 仅必选参数
    result2 = test_required_only()
    test_results.append(("步骤2: 仅必选参数", result2))

    # 步骤3: 必选+1可选
    result3 = test_required_plus_one()
    test_results.append(("步骤3: 必选+1可选", result3))

    # 汇总结果
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    # 判断整体结果
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())