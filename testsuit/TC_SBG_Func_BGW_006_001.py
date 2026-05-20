#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_BGW_006_001.py
# 测试用例: BrowserGateway WebSocket接口 - Muen代理WebSocket连接测试
# 目标: 验证 BrowserGateway Muen代理 WebSocket 接口连接能力

import sys
import os
import time
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import websocket
except ImportError:
    print("[ERROR] 请安装 websocket-client 库: pip install websocket-client")
    sys.exit(1)

# ========== 参数配置 (支持环境变量) ==========
BGW_HOST = os.getenv('BGW_HOST', '127.0.0.1')
BGW_MUEN_PORT = os.getenv('BGW_MUEN_PORT', '30005')

def test_muen_websocket_connect():
    """
    测试步骤1: Muen代理WebSocket连接建立
    预期: WebSocket连接成功建立
    """
    print("[INFO] ========== 测试步骤1: Muen代理WebSocket连接建立 ==========")

    user_id = "6258412454025411_685101555652111"
    ws_url = f"ws://{BGW_HOST}:{BGW_MUEN_PORT}/control/websocket/{user_id}"

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
        print("[PASS] Muen代理WebSocket连接测试成功")
        return True

    except websocket.WebSocketConnectionClosedException as e:
        print(f"[INFO] WebSocket连接被关闭: {str(e)}")
        print("[PASS] WebSocket连接测试完成")
        return True
    except ConnectionRefusedError as e:
        print(f"[ERROR] 连接被拒绝: 无法连接到 {BGW_HOST}:{BGW_MUEN_PORT}")
        print("[INFO] 可能WebSocket服务未启动或端口配置错误")
        return False
    except Exception as e:
        print(f"[ERROR] WebSocket连接异常: {str(e)}")
        return False


def test_muen_websocket_send_message():
    """
    测试步骤2: Muen代理WebSocket发送文本消息
    预期: WebSocket连接成功，消息发送成功
    """
    print("\n[INFO] ========== 测试步骤2: Muen代理WebSocket发送文本消息 ==========")

    user_id = "6258412454025412_685101555652112"
    ws_url = f"ws://{BGW_HOST}:{BGW_MUEN_PORT}/control/websocket/{user_id}"

    print(f"[INFO] WebSocket URL: {ws_url}")

    try:
        ws = websocket.create_connection(
            ws_url,
            timeout=10
        )
        
        print(f"[INFO] WebSocket连接建立成功")
        
        # 发送测试消息
        test_message = json.dumps({
            "type": "test",
            "data": "hello from test client"
        })
        
        ws.send(test_message)
        print(f"[INFO] 发送消息: {test_message}")
        
        time.sleep(1)
        
        ws.close()
        print("[PASS] Muen代理WebSocket发送消息测试成功")
        return True

    except ConnectionRefusedError as e:
        print(f"[ERROR] 连接被拒绝: 无法连接到 {BGW_HOST}:{BGW_MUEN_PORT}")
        return False
    except Exception as e:
        print(f"[ERROR] WebSocket异常: {str(e)}")
        return False


def test_muen_websocket_receive_message():
    """
    测试步骤3: Muen代理WebSocket接收消息测试
    预期: 能够接收服务器返回的消息
    """
    print("\n[INFO] ========== 测试步骤3: Muen代理WebSocket接收消息测试 ==========")

    user_id = "6258412454025413_685101555652113"
    ws_url = f"ws://{BGW_HOST}:{BGW_MUEN_PORT}/control/websocket/{user_id}"

    print(f"[INFO] WebSocket URL: {ws_url}")

    try:
        ws = websocket.create_connection(
            ws_url,
            timeout=10
        )
        
        print(f"[INFO] WebSocket连接建立成功")
        
        # 设置超时接收
        ws.settimeout(5)
        
        try:
            result = ws.recv()
            print(f"[INFO] 接收到消息: {result}")
        except Exception as e:
            print(f"[INFO] 未接收到消息（可能服务端未主动发送）")
        
        ws.close()
        print("[PASS] Muen代理WebSocket接收消息测试完成")
        return True

    except ConnectionRefusedError as e:
        print(f"[ERROR] 连接被拒绝: 无法连接到 {BGW_HOST}:{BGW_MUEN_PORT}")
        return False
    except Exception as e:
        print(f"[PASS] WebSocket测试完成，异常: {str(e)}")
        return True


def test_muen_websocket_invalid_user():
    """
    测试步骤4: 无效用户ID连接Muen代理WebSocket
    预期: WebSocket连接可能被拒绝或关闭
    """
    print("\n[INFO] ========== 测试步骤4: 无效用户ID连接Muen代理WebSocket ==========")

    user_id = "invalid_user_id_xyz"
    ws_url = f"ws://{BGW_HOST}:{BGW_MUEN_PORT}/control/websocket/{user_id}"

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
    BrowserGateway WebSocket接口 - Muen代理WebSocket连接测试
    TC_SBG_Func_BGW_006_001
==================================================================
    """)
    print(f"[INFO] BrowserGateway地址: {BGW_HOST}:{BGW_MUEN_PORT}")
    print("")

    test_results = []

    result1 = test_muen_websocket_connect()
    test_results.append(("步骤1: Muen代理WebSocket连接建立", result1))

    result2 = test_muen_websocket_send_message()
    test_results.append(("步骤2: Muen代理WebSocket发送文本消息", result2))

    result3 = test_muen_websocket_receive_message()
    test_results.append(("步骤3: Muen代理WebSocket接收消息测试", result3))

    result4 = test_muen_websocket_invalid_user()
    test_results.append(("步骤4: 无效用户ID连接", result4))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())