#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TC_SBG_Func_E2E_002.py
测试用例: 多设备并发登录测试
目标: 验证多设备并发登录的会话隔离和资源管理
覆盖: 并发三步登录 -> 独立会话验证 -> 并发控制操作 -> 资源释放

说明:
- 使用多个虚拟设备同时登录
- 验证每个设备获得独立的 token 和 tcpAddr
- 测试并发控制操作的正确性
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from lib.gids_client import GIDSClient
    from lib.tlv_encoder import TLVEncoder, TLVDecoder, TLV_ID, TLV_TYPE
except ImportError as e:
    print(f"[ERROR] 缺少依赖: {e}")
    sys.exit(1)

GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://127.0.0.1:8090')
DEVICE_COUNT = int(os.getenv('DEVICE_COUNT', '3'))
CONTROL_ADDR = os.getenv('CONTROL_ADDR', '')
MEDIA_ADDR_ENV = os.getenv('MEDIA_ADDR', '')


class DeviceSession:
    """设备会话"""
    
    def __init__(self, device_index: int):
        self.device_index = device_index
        self.imei = f"62584124540254{device_index:02d}"
        self.imsi = f"685101555652{device_index:02d}"
        self.client: GIDSClient = None
        self.control_reader = None
        self.control_writer = None
        self.media_reader = None
        self.media_writer = None
        self.token = None
        self.tcp_addr = None
        self.media_addr = None
        self.login_success = False
        self.test_results = []
    
    def add_assertion(self, name: str, condition: bool, message: str = ""):
        """添加断言结果"""
        prefix = f"[设备{self.device_index}]"
        status = "[PASS]" if condition else "[FAIL]"
        msg = f"{prefix}{status} {name}"
        if message:
            msg += f" - {message}"
        print(msg)
        self.test_results.append((name, condition))
        assert condition, f"断言失败: {prefix}{name} - {message}"


async def device_login(device: DeviceSession, gids_addr: str) -> bool:
    """设备三步登录"""
    print(f"\n[设备{device.device_index}] ========== 开始三步登录 ==========")
    
    client = GIDSClient(gids_addr, device.imei, device.imsi)
    client.create_request(width=240, height=320, device_type=2, app_type=1)
    device.client = client
    
    try:
        resp1 = client.grid_login_auth()
        if resp1.get('code') != 200:
            device.add_assertion("gridLoginAuth", False, f"code={resp1.get('code')}")
            return False
        
        device.add_assertion("gridLoginAuth", True, f"code=200")
        
        resp2 = client.grid_login_auth_open_browser()
        if resp2.get('code') != 200:
            device.add_assertion("gridLoginAuthOpenBrowser", False, f"code={resp2.get('code')}")
            return False
        
        device.add_assertion("gridLoginAuthOpenBrowser", True, f"code=200")
        
        resp3 = client.device_login_auth()
        if resp3.get('code') != 200:
            device.add_assertion("deviceLoginAuth", False, f"code={resp3.get('code')}")
            return False
        
        device.add_assertion("deviceLoginAuth", True, f"code=200")
        
        if client.response:
            device.token = client.response.token
            device.tcp_addr = client.response.tcp_addr
            
            device.add_assertion(
                "token不为空",
                len(device.token) > 0,
                f"token长度={len(device.token)}"
            )
            
            device.add_assertion(
                "tcpAddr格式正确",
                ':' in device.tcp_addr,
                f"tcpAddr={device.tcp_addr}"
            )
        
        device.login_success = True
        return True
        
    except Exception as e:
        device.add_assertion("三步登录", False, f"异常: {str(e)}")
        return False


def parse_addr(addr: str) -> tuple:
    """解析地址字符串为(host, port)"""
    addr = addr.replace('http://', '').replace('https://', '')
    parts = addr.split(':')
    return parts[0], int(parts[1])


async def device_connect_control(device: DeviceSession) -> bool:
    """设备连接控制通道"""
    if not device.login_success:
        device.add_assertion("控制通道连接", False, "未完成登录")
        return False
    
    print(f"\n[设备{device.device_index}] ========== 控制通道连接 ==========")
    
    try:
        if CONTROL_ADDR:
            host, port = parse_addr(CONTROL_ADDR)
            print(f"[设备{device.device_index}] 地址(环境变量): {host}:{port}")
        elif device.tcp_addr:
            host, port = parse_addr(device.tcp_addr)
            print(f"[设备{device.device_index}] 地址(response): {device.tcp_addr}")
        else:
            device.add_assertion("控制通道连接", False, "未配置地址")
            return False
        
        reader, writer = await asyncio.open_connection(host, port)
        device.control_reader = reader
        device.control_writer = writer
        
        device.add_assertion(
            "控制通道TCP连接成功",
            True,
            f"{host}:{port}"
        )
        
        login_packet = TLVEncoder.build_login_packet(
            imei=device.imei,
            imsi=device.imsi,
            token=device.token,
            width=240,
            height=320,
            app_type=1,
        )
        
        writer.write(login_packet)
        await writer.drain()
        
        device.add_assertion(
            "TLV登录报文发送成功",
            True,
            f"报文长度={len(login_packet)}字节"
        )
        
        data = await asyncio.wait_for(reader.read(3145728), timeout=10.0)
        
        if data:
            packet = TLVDecoder.decode_packet(data)
            
            if not packet.get('error'):
                msg_type = TLVDecoder.get_int(packet['fields'], TLV_ID['TYPE'])
                
                device.add_assertion(
                    "收到TLV响应报文",
                    msg_type in [TLV_TYPE['ACK'], TLV_TYPE['RETURN_MEDIA']],
                    f"type={msg_type}"
                )
                
                if msg_type == TLV_TYPE['RETURN_MEDIA']:
                    media_addr = TLVDecoder.get_string(packet['fields'], TLV_ID['TCP_ADDR'])
                    device.media_addr = media_addr
                    
                    device.add_assertion(
                        "收到媒体地址",
                        len(media_addr) > 0,
                        f"mediaAddr={media_addr}"
                    )
                    return True
                
                elif msg_type == TLV_TYPE['ACK']:
                    code = TLVDecoder.get_int(packet['fields'], TLV_ID['CODE'])
                    
                    device.add_assertion(
                        "ACK响应code=200",
                        code == 200,
                        f"code={code}"
                    )
                    
                    if code != 200:
                        device.add_assertion(
                            "控制通道登录失败",
                            False,
                            f"ACK code={code}"
                        )
                        return False
                    
                    await asyncio.sleep(1)
                    data2 = await asyncio.wait_for(reader.read(3145728), timeout=10.0)
                    
                    if data2:
                        packet2 = TLVDecoder.decode_packet(data2)
                        msg_type2 = TLVDecoder.get_int(packet2['fields'], TLV_ID['TYPE'])
                        
                        if msg_type2 == TLV_TYPE['RETURN_MEDIA']:
                            media_addr = TLVDecoder.get_string(packet2['fields'], TLV_ID['TCP_ADDR'])
                            device.media_addr = media_addr
                            
                            device.add_assertion(
                                "收到媒体地址RETURN_MEDIA",
                                len(media_addr) > 0,
                                f"mediaAddr={media_addr}"
                            )
                            return True
                        
                        elif msg_type2 == TLV_TYPE['ACK']:
                            code2 = TLVDecoder.get_int(packet2['fields'], TLV_ID['CODE'])
                            
                            device.add_assertion(
                                "第二个ACK响应code=200",
                                code2 == 200,
                                f"code={code2}"
                            )
                            
                            if code2 != 200:
                                device.add_assertion(
                                    "控制通道登录失败",
                                    False,
                                    f"ACK code={code2}"
                                )
                                return False
                    
                    return True
        
        device.add_assertion("控制通道响应", False, "未收到有效响应")
        return False
        
    except asyncio.TimeoutError:
        device.add_assertion("控制通道连接", False, "超时")
        return False
    except Exception as e:
        device.add_assertion("控制通道连接", False, f"异常: {str(e)}")
        return False


async def device_connect_media(device: DeviceSession) -> bool:
    """设备连接媒体通道"""
    print(f"\n[设备{device.device_index}] ========== 媒体通道连接 ==========")
    
    try:
        if MEDIA_ADDR_ENV:
            media_host, media_port = parse_addr(MEDIA_ADDR_ENV)
            print(f"[设备{device.device_index}] 地址(环境变量): {media_host}:{media_port}")
        elif device.media_addr:
            media_host, media_port = parse_addr(device.media_addr)
            print(f"[设备{device.device_index}] 地址(response): {device.media_addr}")
        else:
            device.add_assertion("媒体通道连接", False, "未配置地址")
            return False
        
        reader, writer = await asyncio.open_connection(media_host, media_port)
        device.media_reader = reader
        device.media_writer = writer
        
        device.add_assertion(
            "媒体通道TCP连接成功",
            True,
            f"{media_host}:{media_port}"
        )
        
        login_packet = TLVEncoder.build_login_packet(
            imei=device.imei,
            imsi=device.imsi,
            token=device.token,
            width=240,
            height=320,
            app_type=1,
        )
        
        writer.write(login_packet)
        await writer.drain()
        
        device.add_assertion(
            "媒体通道TLV登录报文发送成功",
            True,
            f"报文长度={len(login_packet)}字节"
        )
        
        video_count = 0
        audio_count = 0
        start_time = time.time()
        
        while time.time() - start_time < 5 and not (video_count > 0 and audio_count > 0):
            try:
                data = await asyncio.wait_for(reader.read(3145728), timeout=2.0)
                
                if not data:
                    break
                
                packet = TLVDecoder.decode_packet(data)
                
                if packet.get('error'):
                    continue
                
                fields = packet['fields']
                msg_type = TLVDecoder.get_int(fields, TLV_ID['TYPE'])
                
                if msg_type == TLV_TYPE['VIDEO']:
                    video_count += 1
                elif msg_type == TLV_TYPE['AUDIO']:
                    audio_count += 1
            
            except asyncio.TimeoutError:
                continue
        
        device.add_assertion(
            "接收到媒体数据",
            video_count > 0 or audio_count > 0,
            f"video={video_count}, audio={audio_count}"
        )
        
        return video_count > 0 or audio_count > 0
        
    except Exception as e:
        device.add_assertion("媒体通道连接", False, f"异常: {str(e)}")
        return False


async def device_send_control(device: DeviceSession, op_name: str, ctrl_type: int, ctrl_val: int) -> bool:
    """设备发送控制操作"""
    if not device.control_writer:
        device.add_assertion(f"{op_name}", False, "控制通道未连接")
        return False
    
    try:
        session_id = f"{device.imei}_{device.imsi}"
        control_packet = TLVEncoder.build_control_packet(ctrl_type, ctrl_val, session_id)
        
        device.control_writer.write(control_packet)
        await device.control_writer.drain()
        
        device.add_assertion(f"{op_name}发送成功", True, f"ctrlType={ctrl_type}")
        return True
    
    except Exception as e:
        device.add_assertion(f"{op_name}发送成功", False, f"异常: {str(e)}")
        return False


async def device_cleanup(device: DeviceSession):
    """清理设备连接"""
    print(f"\n[设备{device.device_index}] ========== 清理连接 ==========")
    
    if device.control_writer:
        try:
            device.control_writer.close()
            await device.control_writer.wait_closed()
            print(f"[设备{device.device_index}] 控制通道已关闭")
        except Exception as e:
            print(f"[设备{device.device_index}] 控制通道关闭异常: {e}")
    
    if device.media_writer:
        try:
            device.media_writer.close()
            await device.media_writer.wait_closed()
            print(f"[设备{device.device_index}] 媒体通道已关闭")
        except Exception as e:
            print(f"[设备{device.device_index}] 媒体通道关闭异常: {e}")


async def test_concurrent_login():
    """测试步骤1: 并发登录"""
    print(f"\n[INFO] ========== 测试步骤1: {DEVICE_COUNT}设备并发登录 ==========")
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    
    devices = [DeviceSession(i+1) for i in range(DEVICE_COUNT)]
    
    tasks = [device_login(device, GIDS_ADDR) for device in devices]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    
    print(f"\n[INFO] 并发登录结果: {success_count}/{DEVICE_COUNT}")
    
    return devices, success_count == DEVICE_COUNT


async def test_session_isolation(devices: list):
    """测试步骤2: 会话隔离验证"""
    print(f"\n[INFO] ========== 测试步骤2: 会话隔离验证 ==========")
    
    tokens = [d.token for d in devices if d.token]
    tcp_addrs = [d.tcp_addr for d in devices if d.tcp_addr]
    
    all_passed = True
    
    for i, device in enumerate(devices):
        if not device.login_success:
            continue
        
        for j, other in enumerate(devices):
            if i == j:
                continue
            
            if not other.login_success:
                continue
            
            if device.token == other.token:
                device.add_assertion(
                    f"Token与其他设备隔离(设备{j+1})",
                    False,
                    f"token相同"
                )
                all_passed = False
    
    if len(set(tokens)) == len(tokens):
        print(f"[PASS] 所有设备Token唯一")
    else:
        print(f"[FAIL] 发现重复Token")
        all_passed = False
    
    if len(set(tcp_addrs)) == len(tcp_addrs):
        print(f"[PASS] 所有设备tcpAddr唯一")
    else:
        print(f"[FAIL] 发现重复tcpAddr")
        all_passed = False
    
    return all_passed


async def test_concurrent_control(devices: list):
    """测试步骤3: 并发控制操作"""
    print(f"\n[INFO] ========== 测试步骤3: 并发控制操作 ==========")
    
    connected_devices = [d for d in devices if d.control_writer]
    
    if not connected_devices:
        print("[FAIL] 没有设备连接控制通道")
        return False
    
    from lib.tlv_encoder import CTRL_TYPE_MAP
    
    tasks = []
    for device in connected_devices:
        tasks.append(device_send_control(device, "UP键", CTRL_TYPE_MAP['up'], 1))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    
    print(f"\n[INFO] 并发控制操作结果: {success_count}/{len(connected_devices)}")
    
    return success_count == len(connected_devices)


async def test_resource_cleanup(devices: list):
    """测试步骤4: 资源清理"""
    print(f"\n[INFO] ========== 测试步骤4: 资源清理 ==========")
    
    tasks = [device_cleanup(device) for device in devices]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"[PASS] 所有设备连接已清理")
    return True


async def main():
    """主测试流程"""
    print("=" * 60)
    print("TC_SBG_Func_E2E_002: 多设备并发登录测试")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        devices, login_success = await test_concurrent_login()
        
        if not devices or not login_success:
            print("\n[FAIL] 并发登录失败，测试终止")
            return False
        
        isolation_success = await test_session_isolation(devices)
        
        connect_tasks = [device_connect_control(device) for device in devices]
        await asyncio.gather(*connect_tasks, return_exceptions=True)
        
        media_tasks = [device_connect_media(device) for device in devices]
        await asyncio.gather(*media_tasks, return_exceptions=True)
        
        control_success = await test_concurrent_control(devices)
        
        await test_resource_cleanup(devices)
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print(f"测试完成，耗时: {elapsed_time:.2f}秒")
        print("=" * 60)
        
        total_assertions = sum(len(d.test_results) for d in devices)
        passed_assertions = sum(sum(1 for _, passed in d.test_results if passed) for d in devices)
        
        print(f"[汇总] 断言统计: {passed_assertions}/{total_assertions} 通过")
        
        return login_success and isolation_success and control_success
        
    except Exception as e:
        print(f"\n[FAIL] 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)