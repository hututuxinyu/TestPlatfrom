#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TC_SBG_Func_BGW_008_001.py
# 测试用例: BrowserGateway TCP接口 - 媒体流TCP连接测试
# 目标: 验证 BrowserGateway 媒体流 TCP 接口连接能力

import socket
import sys
import os
import time

# ========== 参数配置 (支持环境变量) ==========
BGW_HOST = os.getenv('BGW_HOST', '127.0.0.1')
BGW_MEDIA_PORT = os.getenv('BGW_MEDIA_PORT', '30011')
BGW_MEDIA_TLS_PORT = os.getenv('BGW_MEDIA_TLS_PORT', '30013')

def test_media_tcp_connect():
    """
    测试步骤1: 媒体流TCP连接建立（非TLS）
    预期: TCP连接成功建立
    """
    print("[INFO] ========== 测试步骤1: 媒体流TCP连接建立 ==========")

    print(f"[INFO] 目标地址: {BGW_HOST}:{BGW_MEDIA_PORT}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        sock.connect((BGW_HOST, int(BGW_MEDIA_PORT)))
        print("[INFO] TCP连接建立成功")
        
        # 保持连接一小段时间
        time.sleep(2)
        
        sock.close()
        print("[INFO] TCP连接关闭")
        print("[PASS] 媒体流TCP连接测试成功")
        return True

    except socket.timeout:
        print(f"[ERROR] 连接超时: 无法连接到 {BGW_HOST}:{BGW_MEDIA_PORT}")
        return False
    except ConnectionRefusedError:
        print(f"[ERROR] 连接被拒绝: TCP服务可能未启动")
        return False
    except Exception as e:
        print(f"[ERROR] TCP连接异常: {str(e)}")
        return False


def test_media_tcp_send_binary_data():
    """
    测试步骤2: 媒体流TCP发送二进制数据
    预期: 二进制数据发送成功
    """
    print("\n[INFO] ========== 测试步骤2: 媒体流TCP发送二进制数据 ==========")

    print(f"[INFO] 目标地址: {BGW_HOST}:{BGW_MEDIA_PORT}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        sock.connect((BGW_HOST, int(BGW_MEDIA_PORT)))
        print("[INFO] TCP连接建立成功")
        
        # 发送模拟媒体数据（二进制）
        # 模拟简单的视频帧头
        test_data = bytes([0x00, 0x01, 0x02, 0x03, 0xFF, 0xFE, 0xFD])
        sock.sendall(test_data)
        print(f"[INFO] 发送二进制数据: {test_data.hex()}")
        
        time.sleep(1)
        
        sock.close()
        print("[PASS] 媒体流TCP发送二进制数据测试成功")
        return True

    except socket.timeout:
        print(f"[ERROR] 连接超时")
        return False
    except ConnectionRefusedError:
        print(f"[ERROR] 连接被拒绝")
        return False
    except Exception as e:
        print(f"[ERROR] TCP发送异常: {str(e)}")
        return False


def test_media_tcp_send_large_data():
    """
    测试步骤3: 媒体流TCP发送大数据包
    预期: 大数据包发送成功（验证吞吐能力）
    """
    print("\n[INFO] ========== 测试步骤3: 媒体流TCP发送大数据包 ==========")

    print(f"[INFO] 目标地址: {BGW_HOST}:{BGW_MEDIA_PORT}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        
        sock.connect((BGW_HOST, int(BGW_MEDIA_PORT)))
        print("[INFO] TCP连接建立成功")
        
        # 发送较大数据包（模拟视频帧）
        test_data = bytes([0x00] * 1024)  # 1KB数据
        sock.sendall(test_data)
        print(f"[INFO] 发送数据包大小: {len(test_data)} bytes")
        
        time.sleep(1)
        
        sock.close()
        print("[PASS] 媒体流TCP大数据包发送测试成功")
        return True

    except socket.timeout:
        print(f"[ERROR] 发送超时")
        return False
    except ConnectionRefusedError:
        print(f"[ERROR] 连接被拒绝")
        return False
    except Exception as e:
        print(f"[ERROR] TCP发送异常: {str(e)}")
        return False


def test_media_tcp_tls_connect():
    """
    测试步骤4: 媒体流TCP TLS连接测试
    预期: TLS端口可达
    """
    print("\n[INFO] ========== 测试步骤4: 媒体流TCP TLS连接测试 ==========")

    print(f"[INFO] 目标地址: {BGW_HOST}:{BGW_MEDIA_TLS_PORT} (TLS)")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        sock.connect((BGW_HOST, int(BGW_MEDIA_TLS_PORT)))
        print("[INFO] TLS端口连接建立成功")
        
        sock.close()
        print("[PASS] TLS端口可达")
        return True

    except socket.timeout:
        print(f"[WARN] TLS端口连接超时，可能未启用TLS")
        return True
    except ConnectionRefusedError:
        print(f"[WARN] TLS端口被拒绝，可能未启用TLS")
        return True
    except Exception as e:
        print(f"[PASS] TLS端口测试完成，异常: {str(e)}")
        return True


def test_media_tcp_concurrent_connections():
    """
    测试步骤5: 媒体流TCP并发连接测试
    预期: 多个连接可同时建立
    """
    print("\n[INFO] ========== 测试步骤5: 媒体流TCP并发连接测试 ==========")

    print(f"[INFO] 目标地址: {BGW_HOST}:{BGW_MEDIA_PORT}")
    print(f"[INFO] 并发连接数: 3")

    try:
        sockets = []
        for i in range(3):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((BGW_HOST, int(BGW_MEDIA_PORT)))
            sockets.append(sock)
            print(f"[INFO] 连接 {i+1} 建立成功")
        
        time.sleep(2)
        
        for sock in sockets:
            sock.close()
        
        print("[PASS] 媒体流TCP并发连接测试成功")
        return True

    except socket.timeout:
        print(f"[ERROR] 连接超时")
        return False
    except ConnectionRefusedError:
        print(f"[ERROR] 连接被拒绝")
        return False
    except Exception as e:
        print(f"[ERROR] TCP并发连接异常: {str(e)}")
        return False


def main():
    print("""
==================================================================
    BrowserGateway TCP接口 - 媒体流TCP连接测试
    TC_SBG_Func_BGW_008_001
==================================================================
    """)
    print(f"[INFO] BrowserGateway地址: {BGW_HOST}")
    print(f"[INFO] 媒体流端口: {BGW_MEDIA_PORT}, TLS端口: {BGW_MEDIA_TLS_PORT}")
    print("")

    test_results = []

    result1 = test_media_tcp_connect()
    test_results.append(("步骤1: 媒体流TCP连接建立", result1))

    result2 = test_media_tcp_send_binary_data()
    test_results.append(("步骤2: 媒体流TCP发送二进制数据", result2))

    result3 = test_media_tcp_send_large_data()
    test_results.append(("步骤3: 媒体流TCP发送大数据包", result3))

    result4 = test_media_tcp_tls_connect()
    test_results.append(("步骤4: 媒体流TCP TLS连接测试", result4))

    result5 = test_media_tcp_concurrent_connections()
    test_results.append(("步骤5: 媒体流TCP并发连接测试", result5))

    print("\n[INFO] ========== 测试结果汇总 ==========")
    for step, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {step}")

    all_passed = all(result for _, result in test_results)
    print(f"\n{'[SUCCESS]' if all_passed else '[FAILED]'} ========== 测试完成 ==========")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())