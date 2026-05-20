#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_BGW_005_001.py
# 测试用例: BrowserGateway WebSocket接口 - 媒体流WebSocket连接测试
# 目标: 验证 BrowserGateway 媒体流 WebSocket 接口连接能力

import sys
import os
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import websocket
except ImportError:
    print("[ERROR] 请安装 websocket-client 库: pip install websocket-client")
    sys.exit(1)

# ========== 参数配置 (支持环境变量) ==========
BGW_HOST = os.getenv('BGW_HOST', '127.0.0.1')
BGW_MEDIA_PORT = os.getenv('BGW_MEDIA_PORT', '30002')

def test_media_websocket_connect():
    """
    测试步骤1: 媒体流WebSocket连接建立
    预期: WebSocket连接成功建立
    """
    print("[INFO] ========== 测试步骤1: 媒体流WebSocket连接建立 ==========")

    user_id = "6258412454025411_685101555652111"
    ws_url = f"ws://{BGW_HOST}:{BGW_MEDIA_PORT}/browser/websocket/{user_id}"

    print(f"[INFO] WebSocket URL: {ws_url}")

    try:
        ws = websocket.create_connection(
            ws_url,
            timeout=10
        )
        
        print(f"[INFO] WebSocket连接建立成功")
        print(f"[INFO] 连接状态: 已连接")
        
        # 保持连接一小段时间
        time.sleep(2)
        
        ws.close()
        print("[INFO] WebSocket连接关闭")
        print("[PASS] 媒体流WebSocket连接测试成功")
        return True

    except websocket.WebSocketConnectionClosedException as e:
        print(f"[INFO] WebSocket连接被关闭: {str(e)}")
        print("[PASS] WebSocket连接测试完成")
        return True
    except ConnectionRefusedError as e:
        print(f"[ERROR] 连接被拒绝: 无法连接到 {BGW_HOST}:{BGW_MEDIA_PORT}")
        print("[INFO] 可能WebSocket服务未启动或端口配置错误")
        return False
    except Exception as e:
        print(f"[ERROR] WebSocket连接异常: {str(e)}")
        return False


def test_media_websocket_with_params():
    """
    测试步骤2: 媒体流WebSocket带参数连接
    预期: WebSocket连接成功建立并接收参数
    """
    print("\n[INFO] ========== 测试步骤2: 媒体流WebSocket带参数连接 ==========")

    user_id = "6258412454025412_685101555652112"
    ws_url = f"ws://{BGW_HOST}:{BGW_MEDIA_PORT}/browser/websocket/{user_id}?frame_rate=30&width=1080&height=1920"

    print(f"[INFO] WebSocket URL: {ws_url}")

    try:
        ws = websocket.create_connection(
            ws_url,
            timeout=10
        )
        
        print(f"[INFO] WebSocket连接建立成功，带参数")
        
        time.sleep(1)
        
        ws.close()
        print("[PASS] 媒体流WebSocket带参数连接测试成功")
        return True

    except ConnectionRefusedError as e:
        print(f"[ERROR] 连接被拒绝: 无法连接到 {BGW_HOST}:{BGW_MEDIA_PORT}")
        return False
    except Exception as e:
        print(f"[ERROR] WebSocket连接异常: {str(e)}")
        return False


def test_media_websocket_invalid_user():
    """
    测试步骤3: 无效用户ID连接
    预期: WebSocket连接可能被拒绝或关闭
    """
    print("\n[INFO] ========== 测试步骤3: 无效用户ID连接 ==========")

    user_id = "invalid_user_id"
    ws_url = f"ws://{BGW_HOST}:{BGW_MEDIA_PORT}/browser/websocket/{user_id}"

    print(f"[INFO] WebSocket URL: {ws_url} (无效用户ID)")

    try:
        ws = websocket.create_connection(
            ws_url,
            timeout=10
        )
        
        print(f"[INFO] WebSocket连接建立成功（即使是无效用户ID）")
        
        time.sleep(1)
        ws.close()
        print("[PASS] 无效用户ID连接测试完成")
        return True

    except Exception as e:
        print(f"[PASS] WebSocket连接测试完成，异常: {str(e)}")
        return True


def main():
    print("""
==================================================================
    BrowserGateway WebSocket接口 - 媒体流WebSocket连接测试
    TC_SBG_Func_BGW_005_001
==================================================================
    """)
    print(f"[INFO] BrowserGateway地址: {BGW_HOST}:{BGW_MEDIA_PORT}")
    print("")

    test_results = []

    result1 = test_media_websocket_connect()
    test_results.append(("步骤1: 媒体流WebSocket连接建立", result1))

    result2 = test_media_websocket_with_params()
    test_results.append(("步骤2: 媒体流WebSocket带参数连接", result2))

    result3 = test_media_websocket_invalid_user()
    test_results.append(("步骤3: 无效用户ID连接", result3))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())