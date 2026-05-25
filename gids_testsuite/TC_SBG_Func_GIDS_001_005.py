#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_GIDS_001_005.py
# 测试用例: GIDS宫格登录接口 - IMSI格式异常值测试
# 目标: 验证 GIDS 对 IMSI 格式异常的检测能力

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 参数配置 (支持环境变量) ==========
GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://127.0.0.1:9090')

def test_imsi_with_letters():
    """
    测试步骤1: IMSI 包含字母字符（异常值）
    预期: GIDS 应返回错误，提示 IMSI 格式不正确
    """
    print("[INFO] ========== 测试步骤1: IMSI 包含字母字符 ==========")

    test_data = {
        "imsi": "68510155565ABC",
        "imei": "625841245402541",
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

    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)

        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")

        resp_json = response.json()

        # 预期: 应该返回错误，因为 IMSI 包含非数字字符
        # 但由于 GIDS BUG，会返回 code=200 成功
        if response.status_code == 200 and resp_json.get('code') == 200:
            # GIDS BUG: 没有对 IMSI 格式进行校验，直接返回成功
            print("[FAIL] BUG确认: GIDS 对包含字母的 IMSI 没有进行校验，直接返回成功")
            print("[FAIL] 预期: 应返回错误，提示 IMSI 格式不正确")
            return False
        else:
            # 正确行为: 返回错误
            print("[PASS] GIDS 正确返回错误")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_imsi_empty():
    """
    测试步骤2: IMSI 为空字符串（异常值）
    预期: GIDS 应返回错误，提示 IMSI 不能为空
    """
    print("\n[INFO] ========== 测试步骤2: IMSI 为空字符串 ==========")

    test_data = {
        "imsi": "",
        "imei": "625841245402541",
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

    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)

        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")

        resp_json = response.json()

        # 预期: 应该返回错误，因为 IMSI 为空
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 对空的 IMSI 没有进行校验，直接返回成功")
            print("[FAIL] 预期: 应返回错误，提示 IMSI 不能为空")
            return False
        else:
            print("[PASS] GIDS 正确返回错误")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_imsi_too_short():
    """
    测试步骤3: IMSI 长度过短（异常值）
    预期: GIDS 应返回错误，提示 IMSI 长度不正确
    """
    print("\n[INFO] ========== 测试步骤3: IMSI 长度过短 ==========")

    test_data = {
        "imsi": "12345",
        "imei": "625841245402541",
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

    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)

        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")

        resp_json = response.json()

        # 预期: 应该返回错误，因为 IMSI 长度不正确
        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[FAIL] BUG确认: GIDS 对长度过短的 IMSI 没有进行校验，直接返回成功")
            print("[FAIL] 预期: 应返回错误，提示 IMSI 长度应为15位")
            return False
        else:
            print("[PASS] GIDS 正确返回错误")
            return True

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def test_valid_params():
    """
    测试步骤4: 正常参数（验证正常流程仍然有效）
    """
    print("\n[INFO] ========== 测试步骤4: 正常参数验证 ==========")

    test_data = {
        "imsi": "685101555652111",
        "imei": "625841245402541",
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

    url = f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
    print(f"[REQUEST] URL: POST {url}")
    print(f"[REQUEST] Body: {json.dumps(test_data, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=test_data, timeout=30, verify=False)

        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")

        resp_json = response.json()

        if response.status_code == 200 and resp_json.get('code') == 200:
            print("[PASS] 正常参数请求成功")
            return True
        else:
            print("[FAIL] 正常参数请求失败")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 连接失败: 无法连接到 {GIDS_ADDR}")
        return False
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    GIDS宫格登录接口 - IMSI格式异常值测试
    TC_SBG_Func_GIDS_001_005
==================================================================
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print("")

    # 执行测试步骤
    test_results = []

    # 步骤1: IMSI 包含字母
    result1 = test_imsi_with_letters()
    test_results.append(("步骤1: IMSI包含字母", result1))

    # 步骤2: IMSI 为空
    result2 = test_imsi_empty()
    test_results.append(("步骤2: IMSI为空", result2))

    # 步骤3: IMSI 长度过短
    result3 = test_imsi_too_short()
    test_results.append(("步骤3: IMSI长度过短", result3))

    # 步骤4: 正常参数
    result4 = test_valid_params()
    test_results.append(("步骤4: 正常参数", result4))

    # 汇总结果
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    # 判断整体结果
    # 注意: 由于当前 GIDS 有 BUG，前3个测试会 FAIL，这是预期的
    # 修复 GIDS 后，所有测试应该 PASS
    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    if not all_passed:
        print("\n[INFO] 注意: 如果前3个测试失败，说明 GIDS 存在 BUG - 缺少对 IMSI 格式的校验")
        print("[INFO] 需要修复 GIDS 的 gridLoginAuthOpenBrowser 接口")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())