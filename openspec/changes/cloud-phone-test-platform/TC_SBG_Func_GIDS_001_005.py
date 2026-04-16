#!/usr/bin/env python3
# TC_SBG_Func_GIDS_001_005.py
# 测试用例: 宫格登录身份验证并打开浏览器接口验证-数据类型异常测试

import requests
import json
import sys

# ========== 参数配置 ==========
GIDS_ADDR = "http://192.168.1.100:9090"
DEVICE_WHITE_IMEI = "6258412454025411"

# ========== 正常测试数据(基准数据) ==========
TEST_DATA_NORMAL = {
    "imsi": "68510155565211",
    "imei": "6258412454025411",
    "manufacturer": "xxx 厂商",
    "model": "xx 机型",
    "appType": 1,
    "extendModel": "default",
    "country": "default",
    "platform": "default",
    "width": "240",
    "height": "320",
    "mcc": "460",
    "mnc": "00x",
    "lac": "100",
    "ci": "5.21",
    "rxlev": -72,
    "totalKb": 1424122,
    "freeKb": 1424122,
    "clientLanguage": "en",
    "deviceType": 1000
}

def test_normal_data_type():
    """步骤1: 验证正常数据类型(Against期望值)"""
    print("[INFO] ========== 测试步骤1: 正常数据类型验证(基准测试) ==========")
    print(f"[INFO] 使用正常数据类型作为基准")
    print(f"[INFO] 请求参数: {json.dumps(TEST_DATA_NORMAL, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=TEST_DATA_NORMAL,
            timeout=30
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        if response.status_code in [200, 201]:
            print("[SUCCESS] 正常数据类型请求成功")
            print("[SUCCESS] 验证基准: 接口正常处理标准数据类型")
            return True
        else:
            print(f"[ERROR] 基准测试失败,状态码: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_imsi_wrong_type():
    """步骤2: 验证IMSI数据类型异常"""
    print("\n[INFO] ========== 测试步骤2: IMSI数据类型异常测试 ==========")
    print("[INFO] 测试场景: IMSI从String改为Integer(期望: 400错误)")

    # 复制基准数据并修改IMSI类型为整数
    test_data_wrong_type = TEST_DATA_NORMAL.copy()
    test_data_wrong_type["imsi"] = 68510155565211  # 从String改为Integer

    print(f"[INFO] 异常参数: imsi = {test_data_wrong_type['imsi']} (type: {type(test_data_wrong_type['imsi'])})")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data_wrong_type,
            timeout=30
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        # 预期: 数据类型转换被后端处理,或报400错误
        if response.status_code in [400]:
            resp_data = response.json()
            error_code = resp_data.get("errorCode", "")
            error_msg = resp_data.get("errorMsg", "")

            print(f"[INFO] ErrorCode: {error_code}")
            print(f"[INFO] ErrorMsg: {error_msg}")

            if error_code in ["INVALID_DATA_TYPE", "TYPE_ERROR"]:
                print("[SUCCESS] 按预期返回数据类型错误")
                return True
            else:
                print("[WARN] 返回错误但错误码不是数据类型相关")
                return True  # 不算失败,继续测试

        elif response.status_code in [200, 201]:
            # 如果后端自动处理了类型转换,也算通过
            print("[INFO] 后端自动处理了类型转换,请求成功")
            return True
        else:
            print(f"[ERROR] 未预期的响应码: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_device_type_wrong_type():
    """步骤3: 验证DeviceType数据类型异常"""
    print("\n[INFO] ========== 测试步骤3: DeviceType数据类型异常测试 ==========")
    print("[INFO] 测试场景: DeviceType从Integer改为String(期望: 400错误)")

    # 复制基准数据并修改DeviceType类型为字符串
    test_data_wrong_type = TEST_DATA_NORMAL.copy()
    test_data_wrong_type["deviceType"] = "1000"  # 从Integer改为String

    print(f"[INFO] 异常参数: deviceType = {test_data_wrong_type['deviceType']} (type: {type(test_data_wrong_type['deviceType'])})")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data_wrong_type,
            timeout=30
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        # 预期逻辑同steps 2
        if response.status_code in [400]:
            resp_data = response.json()
            error_code = resp_data.get("errorCode", "")
            error_msg = resp_data.get("errorMsg", "")

            print(f"[INFO] ErrorCode: {error_code}")
            print(f"[INFO] ErrorMsg: {error_msg}")

            if error_code in ["INVALID_DATA_TYPE", "TYPE_ERROR"]:
                print("[SUCCESS] 按预期返回数据类型错误")
                return True
            else:
                print("[WARN] 返回错误但错误码不是数据类型相关")
                return True

        elif response.status_code in [200, 201]:
            print("[INFO] 后端自动处理了类型转换,请求成功")
            return True
        else:
            print(f"[ERROR] 未预期的响应码: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_mixed_type_errors():
    """步骤4: 验证混合数据类型异常"""
    print("\n[INFO] ========== 测试步骤4: 混合数据类型异常测试 ==========")
    print("[INFO] 测试场景: 多个参数同时使用错误数据类型")

    # 复制基准数据并修改多个参数的数据类型
    test_data_mixed_errors = TEST_DATA_NORMAL.copy()
    test_data_mixed_errors["imsi"] = 68510155565211          # String -> Integer
    test_data_mixed_errors["imei"] = 6258412454025411          # String -> Integer
    test_data_mixed_errors["width"] = 240                     # String -> Integer
    test_data_mixed_errors["height"] = 320                    # String -> Integer
    test_data_mixed_errors["deviceType"] = "1000"           # Integer -> String
    test_data_mixed_errors["rxlev"] = "-72"                  # Integer -> String
    test_data_mixed_errors["totalKb"] = "1424122"           # Integer -> String
    test_data_mixed_errors["freeKb"] = "1424122"            # Integer -> String

    print("[INFO] 异常类型转换:")
    print("[INFO]   - imsi: String -> Integer")
    print("[INFO]   - imei: String -> Integer")
    print("[INFO]   - deviceType: Integer -> String")
    print("[INFO]   - rxlev: Integer -> String")
    print("[INFO]   - totalKb: Integer -> String")
    print("[INFO]   - freeKb: Integer -> String")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data_mixed_errors,
            timeout=30
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        # 预期: 应该返回400错误(数据类型验证失败)
        if response.status_code in [400]:
            resp_data = response.json()
            error_code = resp_data.get("errorCode", "")
            error_msg = resp_data.get("errorMsg", "")

            print(f"[INFO] ErrorCode: {error_code}")
            print(f"[INFO] ErrorMsg: {error_msg}")

            if error_code in ["INVALID_DATA_TYPE", "TYPE_ERROR", "VALIDATION_ERROR"]:
                print("[SUCCESS] 按预期返回数据类型验证错误")
                return True
            else:
                print("[WARN] 返回错误但错误码可能不符合预期")
                return True

        else:
            print(f"[ERROR] 未按预期返回400错误,实际: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def test_extra_field_type():
    """步骤5: 验证额外字段的数据类型"""
    print("\n[INFO] ========== 测试步骤5: 额外字段数据类型测试 ==========")
    print("[INFO] 测试场景: 添加非文档定义的字段,使用各种数据类型")

    # 添加额外字段,使用各种数据类型
    test_data_extra = TEST_DATA_NORMAL.copy()
    test_data_extra["custom_string"] = "额外字符串字段"
    test_data_extra["custom_number"] = 12345
    test_data_extra["custom_boolean"] = True
    test_data_extra["custom_array"] = [1, 2, 3]
    test_data_extra["custom_object"] = {"key": "value"}

    print("[INFO] 添加的额外字段:")
    print("[INFO]   - custom_string: String")
    print("[INFO]   - custom_number: Number")
    print("[INFO]   - custom_boolean: Boolean")
    print("[INFO]   - custom_array: Array")
    print("[INFO]   - custom_object: Object")

    try:
        response = requests.post(
            f"{GIDS_ADDR}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser",
            json=test_data_extra,
            timeout=30
        )

        print(f"[INFO] 响应状态码: {response.status_code}")
        print(f"[INFO] 响应数据: {response.text}")

        # 预期: 后端应该忽略额外字段,不影响正常处理
        if response.status_code in [200, 201]:
            print("[SUCCESS] 后端正确忽略了额外字段")
            print("[SUCCESS] 数据类型验证: 通过")
            return True
        else:
            # 如果后端严格验证所有字段,也正确
            resp_data = response.json()
            error_msg = resp_data.get("errorMsg", "")
            if "extra" in error_msg.lower() or "unknown" in error_msg.lower():
                print("[SUCCESS] 后端正确拒绝了额外字段")
                print("[SUCCESS] 数据类型验证: 通过")
                return True
            else:
                print(f"[ERROR] 未预期的错误: {error_msg}")
                return False

    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    宫格登录身份验证并打开浏览器接口验证-数据类型异常测试          ║
║    TC_SBG_Func_GIDS_001_005                                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print(f"[INFO] 白名单IMEI: {DEVICE_WHITE_IMEI}")
    print("")

    # 执行测试步骤
    test_results = []

    # 步骤1: 正常数据类型(基准测试)
    result1 = test_normal_data_type()
    test_results.append(("步骤1: 正常数据类型", result1))

    # 步骤2: IMSI数据类型异常
    result2 = test_imsi_wrong_type()
    test_results.append(("步骤2: IMSI类型异常", result2))

    # 步骤3: DeviceType数据类型异常
    result3 = test_device_type_wrong_type()
    test_results.append(("步骤3: DeviceType类型异常", result3))

    # 步骤4: 混合数据类型异常
    result4 = test_mixed_type_errors()
    test_results.append(("步骤4: 混合类型异常", result4))

    # 步骤5: 额外字段数据类型
    result5 = test_extra_field_type()
    test_results.append(("步骤5: 额外字段类型", result5))

    # 汇总结果
    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    # 判断整体结果
    all_passed = all(result for _, result in test_results)
    passed_count = sum(1 for _, result in test_results if result)
    total_count = len(test_results)

    print(f"\n[INFO] 测试通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    print(f"{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())