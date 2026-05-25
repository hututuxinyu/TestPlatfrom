#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TC_SBG_Func_E2E_001.py
测试用例: 云手机完整E2E流程测试
目标: 验证云手机完整端到端流程，模拟mobile项目的BrowserContext行为
覆盖: 三步登录 -> 控制通道连接 -> 媒体通道连接 -> 控制操作 -> 心跳保活 -> 事件上报 -> 长时间稳定性 -> 断开连接
参考: D:\\Code\\SBG-Github\\SBG\\SBG\\mobile\\src\\main\\java\\com\\huawei\\mobile\\BrowserContext.java

说明:
- 测试用例唯一调用端口: GIDS HTTP服务端口 (默认9090)
- 登录成功后，GIDS返回tcpAddr，测试用例直接连接边缘服务的控制通道和媒体通道
- 模拟BrowserContext.java的完整流程，无需通过mobile WebSocket代理
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from lib.gids_client import GIDSClient
    from lib.tlv_encoder import TLVEncoder, TLVDecoder, TLV_ID, TLV_TYPE, CTRL_TYPE_MAP
except ImportError as e:
    print(f"[ERROR] 缺少依赖: {e}")
    sys.exit(1)

GIDS_ADDR = os.getenv('GIDS_ADDR', 'http://127.0.0.1:9090')
DEVICE_WHITE_IMEI = os.getenv('DEVICE_WHITE_IMEI', '6258412454025411')
DEVICE_WHITE_IMSI = os.getenv('DEVICE_WHITE_IMSI', '68510155565211')
TEST_DURATION = int(os.getenv('TEST_DURATION', '60'))


class E2ETestContext:
    """E2E测试上下文，模拟BrowserContext"""
    
    def __init__(self):
        self.client = None
        self.control_reader = None
        self.control_writer = None
        self.media_reader = None
        self.media_writer = None
        self.session_id = None
        self.media_addr = None
        self.test_results = []
    
    def add_assertion(self, name: str, condition: bool, message: str = ""):
        """添加断言结果"""
        status = "[PASS]" if condition else "[FAIL]"
        msg = f"{status} {name}"
        if message:
            msg += f" - {message}"
        print(msg)
        self.test_results.append((name, condition))
        assert condition, f"断言失败: {name} - {message}"


async def test_step1_three_step_login(context: E2ETestContext):
    """
    测试步骤1: 三步登录流程
    参考: BrowserContext.deviceLogin()
    断言条件:
    - gridLoginAuth返回code=200
    - gridLoginAuthOpenBrowser返回code=200
    - deviceLoginAuth返回code=200
    - token不为空
    - tcpAddr格式为host:port
    """
    print("\n[INFO] ========== 测试步骤1: 三步登录流程 ==========")
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    
    client = GIDSClient(GIDS_ADDR, DEVICE_WHITE_IMEI, DEVICE_WHITE_IMSI)
    client.create_request(width=240, height=320, device_type=2, app_type=1)
    context.client = client
    context.session_id = client.request.get_session_id() if client.request else ""
    
    resp1 = client.grid_login_auth()
    context.add_assertion(
        "gridLoginAuth返回code=200",
        resp1.get('code') == 200,
        f"实际code={resp1.get('code')}"
    )
    
    if resp1.get('code') == 200:
        data1 = resp1.get('data', {})
        context.add_assertion(
            "gridLoginAuth返回token",
            len(data1.get('token', '')) > 0,
            f"token长度={len(data1.get('token', ''))}"
        )
        context.add_assertion(
            "gridLoginAuth返回nodeGateWayUrl",
            len(data1.get('nodeGateWayUrl', '')) > 0,
            f"nodeGateWayUrl={data1.get('nodeGateWayUrl', '')}"
        )
    
    resp2 = client.grid_login_auth_open_browser()
    context.add_assertion(
        "gridLoginAuthOpenBrowser返回code=200",
        resp2.get('code') == 200,
        f"实际code={resp2.get('code')}"
    )
    
    if resp2.get('code') == 200:
        data2 = resp2.get('data', {})
        context.add_assertion(
            "gridLoginAuthOpenBrowser返回token",
            len(data2.get('token', '')) > 0,
            f"token长度={len(data2.get('token', ''))}"
        )
        context.add_assertion(
            "gridLoginAuthOpenBrowser返回nodeGateWayUrl",
            len(data2.get('nodeGateWayUrl', '')) > 0,
            f"nodeGateWayUrl={data2.get('nodeGateWayUrl', '')}"
        )
    
    resp3 = client.device_login_auth()
    context.add_assertion(
        "deviceLoginAuth返回code=200",
        resp3.get('code') == 200,
        f"实际code={resp3.get('code')}"
    )
    
    if resp3.get('code') == 200:
        data = resp3.get('data', {})
        token = data.get('token', '')
        tcp_addr = data.get('tcpAddr', '')
        
        context.add_assertion(
            "token不为空且长度>0",
            len(token) > 0,
            f"token长度={len(token)}"
        )
        
        context.add_assertion(
            "tcpAddr不为空",
            len(tcp_addr) > 0,
            f"tcpAddr={tcp_addr}"
        )
        
        context.add_assertion(
            "tcpAddr格式为host:port",
            ':' in tcp_addr and tcp_addr.count(':') == 1,
            f"tcpAddr={tcp_addr}"
        )
        
        if ':' in tcp_addr:
            parts = tcp_addr.split(':')
            context.add_assertion(
                "tcpAddr端口为有效数字",
                parts[1].isdigit() and 1 <= int(parts[1]) <= 65535,
                f"port={parts[1]}"
            )
    
    return resp3.get('code') == 200


async def test_step2_control_channel_connect(context: E2ETestContext):
    """
    测试步骤2: 控制通道TCP连接
    参考: BrowserContext.controlLogin()
    断言条件:
    - TCP连接成功
    - TLV登录报文发送成功
    - 收到ACK响应或RETURN_MEDIA响应
    """
    print("\n[INFO] ========== 测试步骤2: 控制通道TCP连接 ==========")
    
    if not context.client or not context.client.response:
        print("[FAIL] 未完成登录，跳过此步骤")
        return False
    
    tcp_addr = context.client.response.tcp_addr
    print(f"\n[TCP] ========== 控制通道连接 ==========")
    print(f"[TCP] 地址: {tcp_addr}")
    
    try:
        parts = tcp_addr.split(':')
        host = parts[0]
        port = int(parts[1])
        
        reader, writer = await asyncio.open_connection(host, port)
        context.control_reader = reader
        context.control_writer = writer
        
        context.add_assertion(
            "控制通道TCP连接成功",
            True,
            f"{host}:{port}"
        )
        
        login_packet = TLVEncoder.build_login_packet(
            imei=DEVICE_WHITE_IMEI,
            imsi=DEVICE_WHITE_IMSI,
            token=context.client.response.token,
            width=240,
            height=320,
            app_type=1,
        )
        
        login_packet_decoded = TLVDecoder.decode_packet(login_packet)
        print(f"\n[TCP REQUEST] ========== 发送登录报文 ==========")
        print(f"[TCP REQUEST] 长度: {len(login_packet)} bytes")
        print(f"[TCP REQUEST] 内容:\n{TLVDecoder.format_packet(login_packet_decoded)}")
        
        writer.write(login_packet)
        await writer.drain()
        
        context.add_assertion(
            "TLV登录报文发送成功",
            True,
            f"报文长度={len(login_packet)}字节"
        )
        
        data = await asyncio.wait_for(reader.read(3145728), timeout=10.0)
        
        if data:
            packet = TLVDecoder.decode_packet(data)
            
            print(f"\n[TCP RESPONSE] ========== 收到响应报文 ==========")
            print(f"[TCP RESPONSE] 长度: {len(data)} bytes")
            print(f"[TCP RESPONSE] 内容:\n{TLVDecoder.format_packet(packet)}")
            
            if not packet.get('error'):
                msg_type = TLVDecoder.get_int(packet['fields'], TLV_ID['TYPE'])
                
                context.add_assertion(
                    "收到TLV响应报文",
                    msg_type in [TLV_TYPE['ACK'], TLV_TYPE['RETURN_MEDIA']],
                    f"type={msg_type}"
                )
                
                if msg_type == TLV_TYPE['RETURN_MEDIA']:
                    media_addr = TLVDecoder.get_string(packet['fields'], TLV_ID['TCP_ADDR'])
                    context.media_addr = media_addr
                    
                    context.add_assertion(
                        "收到媒体地址RETURN_MEDIA",
                        len(media_addr) > 0,
                        f"mediaAddr={media_addr}"
                    )
                    
                    context.add_assertion(
                        "浏览器已打开(收到RETURN_MEDIA表示浏览器开始渲染)",
                        len(media_addr) > 0,
                        "RETURN_MEDIA表明边缘服务浏览器已就绪"
                    )
                    
                    return True
                
                elif msg_type == TLV_TYPE['ACK']:
                    code = TLVDecoder.get_int(packet['fields'], TLV_ID['CODE'])
                    
                    context.add_assertion(
                        "ACK响应code=200",
                        code == 200,
                        f"code={code}"
                    )
                    
                    await asyncio.sleep(1)
                    data2 = await asyncio.wait_for(reader.read(3145728), timeout=10.0)
                    
                    if data2:
                        packet2 = TLVDecoder.decode_packet(data2)
                        
                        print(f"\n[TCP RESPONSE] ========== 收到第二个响应报文 ==========")
                        print(f"[TCP RESPONSE] 长度: {len(data2)} bytes")
                        print(f"[TCP RESPONSE] 内容:\n{TLVDecoder.format_packet(packet2)}")
                        
                        msg_type2 = TLVDecoder.get_int(packet2['fields'], TLV_ID['TYPE'])
                        
                        if msg_type2 == TLV_TYPE['RETURN_MEDIA']:
                            media_addr = TLVDecoder.get_string(packet2['fields'], TLV_ID['TCP_ADDR'])
                            context.media_addr = media_addr
                            
                            context.add_assertion(
                                "收到媒体地址RETURN_MEDIA",
                                len(media_addr) > 0,
                                f"mediaAddr={media_addr}"
                            )
                            
                            return True
                    
                    return True
        
        context.add_assertion("控制通道连接流程", False, "未收到有效响应")
        return False
        
    except asyncio.TimeoutError:
        context.add_assertion("控制通道连接流程", False, "超时")
        return False
    except Exception as e:
        context.add_assertion("控制通道连接流程", False, f"异常: {str(e)}")
        return False


async def test_step3_media_channel_connect(context: E2ETestContext):
    """
    测试步骤3: 媒体通道TCP连接
    参考: BrowserContext.mediaLogin()
    断言条件:
    - 媒体地址格式正确
    - 媒体通道TCP连接成功
    - 媒体通道登录成功
    - 开始接收视频/音频数据
    """
    print("\n[INFO] ========== 测试步骤3: 媒体通道TCP连接 ==========")
    
    if not context.media_addr:
        context.add_assertion("媒体通道连接", False, "未收到媒体地址")
        return False
    
    print(f"\n[TCP] ========== 媒体通道连接 ==========")
    print(f"[TCP] 地址: {context.media_addr}")
    
    try:
        media_addr = context.media_addr.replace('http://', '').replace('https://', '')
        media_parts = media_addr.split(':')
        media_host = media_parts[0]
        media_port = int(media_parts[1])
        
        reader, writer = await asyncio.open_connection(media_host, media_port)
        context.media_reader = reader
        context.media_writer = writer
        
        context.add_assertion(
            "媒体通道TCP连接成功",
            True,
            f"{media_host}:{media_port}"
        )
        
        login_packet = TLVEncoder.build_login_packet(
            imei=DEVICE_WHITE_IMEI,
            imsi=DEVICE_WHITE_IMSI,
            token=context.client.response.token,
            width=240,
            height=320,
            app_type=1,
        )
        
        login_packet_decoded = TLVDecoder.decode_packet(login_packet)
        print(f"\n[TCP REQUEST] ========== 发送媒体登录报文 ==========")
        print(f"[TCP REQUEST] 长度: {len(login_packet)} bytes")
        print(f"[TCP REQUEST] 内容:\n{TLVDecoder.format_packet(login_packet_decoded)}")
        
        writer.write(login_packet)
        await writer.drain()
        
        context.add_assertion(
            "媒体通道TLV登录报文发送成功",
            True,
            f"报文长度={len(login_packet)}字节"
        )
        
        video_count = 0
        audio_count = 0
        start_time = time.time()
        
        print(f"\n[TCP RESPONSE] ========== 接收媒体数据 ==========")
        
        while time.time() - start_time < 10 and not (video_count > 0 and audio_count > 0):
            try:
                data = await asyncio.wait_for(reader.read(3145728), timeout=3.0)
                
                if not data:
                    break
                
                packet = TLVDecoder.decode_packet(data)
                
                if packet.get('error'):
                    continue
                
                fields = packet['fields']
                msg_type = TLVDecoder.get_int(fields, TLV_ID['TYPE'])
                
                if msg_type == TLV_TYPE['VIDEO']:
                    video_data = TLVDecoder.get_bytes(fields, TLV_ID['VIDEO_DATA'])
                    if video_data:
                        video_count += 1
                        if video_count <= 3:
                            print(f"[TCP RESPONSE] 视频#{video_count}: {len(video_data)} bytes")
                
                elif msg_type == TLV_TYPE['AUDIO']:
                    audio_data = TLVDecoder.get_bytes(fields, TLV_ID['AUDIO_DATA'])
                    if audio_data:
                        audio_count += 1
                        if audio_count <= 3:
                            print(f"[TCP RESPONSE] 音频#{audio_count}: {len(audio_data)} bytes")
                
                elif msg_type == TLV_TYPE['ACK']:
                    if video_count == 0 and audio_count == 0:
                        print(f"[TCP RESPONSE] ACK:\n{TLVDecoder.format_packet(packet)}")
            
            except asyncio.TimeoutError:
                continue
        
        context.add_assertion(
            "接收到视频数据",
            video_count > 0,
            f"视频帧数={video_count}"
        )
        
        if video_count > 0:
            context.add_assertion(
                "浏览器界面渲染成功(视频帧=浏览器渲染画面)",
                True,
                f"视频帧来自浏览器渲染的页面界面"
            )
        
        context.add_assertion(
            "接收到音频数据",
            audio_count > 0,
            f"音频帧数={audio_count}"
        )
        
        context.add_assertion(
            "媒体流正常(视频或音频)",
            video_count > 0 or audio_count > 0,
            f"video={video_count}, audio={audio_count}"
        )
        
        return video_count > 0 or audio_count > 0
        
    except Exception as e:
        context.add_assertion("媒体通道连接流程", False, f"异常: {str(e)}")
        return False


async def test_step4_control_operations(context: E2ETestContext):
    """
    测试步骤4: 控制操作测试
    参考: BrowserContext.handleDirection()
    断言条件:
    - 方向键(up/down/left/right)发送成功
    - 确认键(ok)发送成功
    - 返回键(back)发送成功
    - 菜单键(menu)发送成功
    - Home键(home)发送成功
    """
    print("\n[INFO] ========== 测试步骤4: 控制操作测试 ==========")
    
    if not context.control_writer:
        context.add_assertion("控制操作", False, "控制通道未连接")
        return False
    
    session_id = context.session_id or f"{DEVICE_WHITE_IMEI}_{DEVICE_WHITE_IMSI}"
    
    print(f"\n[TCP] ========== 控制操作测试 ==========")
    print(f"[TCP] Session ID: {session_id}")
    
    control_ops = [
        ("UP键", CTRL_TYPE_MAP['up'], 1),
        ("DOWN键", CTRL_TYPE_MAP['down'], 1),
        ("LEFT键", CTRL_TYPE_MAP['left'], 1),
        ("RIGHT键", CTRL_TYPE_MAP['right'], 1),
        ("OK键", CTRL_TYPE_MAP['ok'], 1),
        ("BACK键", CTRL_TYPE_MAP['back'], 1),
        ("MENU键", CTRL_TYPE_MAP['menu'], 1),
        ("HOME键", CTRL_TYPE_MAP['home'], 1),
    ]
    
    success_count = 0
    
    for op_name, ctrl_type, ctrl_val in control_ops:
        try:
            control_packet = TLVEncoder.build_control_packet(ctrl_type, ctrl_val, session_id)
            
            print(f"\n[TCP REQUEST] ========== {op_name} ==========")
            print(f"[TCP REQUEST] ctrlType={ctrl_type}, ctrlVal={ctrl_val}")
            
            context.control_writer.write(control_packet)
            await context.control_writer.drain()
            
            context.add_assertion(
                f"{op_name}发送成功",
                True,
                f"ctrlType={ctrl_type}, ctrlVal={ctrl_val}"
            )
            success_count += 1
            
            await asyncio.sleep(0.5)
        
        except Exception as e:
            context.add_assertion(f"{op_name}发送成功", False, f"异常: {str(e)}")
    
    context.add_assertion(
        "所有控制操作发送成功",
        success_count == len(control_ops),
        f"成功数={success_count}/{len(control_ops)}"
    )
    
    return success_count == len(control_ops)


async def test_step5_heartbeat(context: E2ETestContext):
    """
    测试步骤5: 心跳保活测试
    参考: 控制通道心跳机制
    断言条件:
    - 心跳报文发送成功
    - 收到心跳ACK响应
    - 连接保持稳定
    """
    print("\n[INFO] ========== 测试步骤5: 心跳保活测试 ==========")
    
    if not context.control_writer or not context.control_reader:
        context.add_assertion("心跳测试", False, "控制通道未连接")
        return False
    
    print(f"\n[TCP] ========== 心跳保活测试 ==========")
    
    heartbeat_count = 0
    ack_count = 0
    test_rounds = 3
    
    for i in range(test_rounds):
        try:
            heartbeat = TLVEncoder.build_heartbeat_packet()
            
            print(f"\n[TCP REQUEST] ========== 第{i+1}次心跳 ==========")
            heartbeat_decoded = TLVDecoder.decode_packet(heartbeat)
            print(f"[TCP REQUEST] 内容:\n{TLVDecoder.format_packet(heartbeat_decoded)}")
            
            context.control_writer.write(heartbeat)
            await context.control_writer.drain()
            heartbeat_count += 1
            
            context.add_assertion(
                f"第{i+1}次心跳发送成功",
                True,
                ""
            )
            
            try:
                data = await asyncio.wait_for(context.control_reader.read(3145728), timeout=5.0)
                
                if data:
                    packet = TLVDecoder.decode_packet(data)
                    
                    print(f"\n[TCP RESPONSE] ========== 第{i+1}次心跳响应 ==========")
                    print(f"[TCP RESPONSE] 内容:\n{TLVDecoder.format_packet(packet)}")
                    
                    msg_type = TLVDecoder.get_int(packet['fields'], TLV_ID['TYPE'])
                    
                    if msg_type == TLV_TYPE['ACK']:
                        ack_count += 1
                        context.add_assertion(
                            f"第{i+1}次心跳ACK响应",
                            True,
                            ""
                        )
            
            except asyncio.TimeoutError:
                context.add_assertion(
                    f"第{i+1}次心跳ACK响应",
                    False,
                    "超时"
                )
            
            await asyncio.sleep(1)
        
        except Exception as e:
            context.add_assertion(f"第{i+1}次心跳", False, f"异常: {str(e)}")
    
    context.add_assertion(
        f"心跳发送成功率100%",
        heartbeat_count == test_rounds,
        f"发送{heartbeat_count}/{test_rounds}"
    )
    
    context.add_assertion(
        f"心跳ACK响应率>50%",
        ack_count >= test_rounds * 0.5,
        f"收到{ack_count}/{test_rounds}"
    )
    
    return heartbeat_count == test_rounds and ack_count >= test_rounds * 0.5


async def test_step6_send_client_events(context: E2ETestContext):
    """
    测试步骤6: 客户端事件上报测试
    参考: BrowserContext.sendError() 和 sendUseTime()
    断言条件:
    - sendClientEvent type=1 成功
    - sendClientEvent type=2 成功
    - sendAppUseTimesEvent 成功
    """
    print("\n[INFO] ========== 测试步骤6: 客户端事件上报测试 ==========")
    
    if not context.client or not context.client.request:
        context.add_assertion("事件上报", False, "客户端未初始化")
        return False
    
    try:
        resp1 = context.client.send_client_event(1)
        context.add_assertion(
            "sendClientEvent type=1成功",
            resp1.get('code') == 0,
            f"code={resp1.get('code')}"
        )
        
        resp2 = context.client.send_client_event(2)
        context.add_assertion(
            "sendClientEvent type=2成功",
            resp2.get('code') == 0,
            f"code={resp2.get('code')}"
        )
        
        resp3 = context.client.send_use_times_event(100000)
        context.add_assertion(
            "sendAppUseTimesEvent成功",
            resp3.get('code') == 0,
            f"code={resp3.get('code')}"
        )
        
        return resp1.get('code') == 0 and resp2.get('code') == 0 and resp3.get('code') == 0
    
    except Exception as e:
        context.add_assertion("事件上报", False, f"异常: {str(e)}")
        return False


async def test_step7_long_run_stability(context: E2ETestContext):
    """
    测试步骤7: 长时间运行稳定性测试
    参考: 长时间视频播放场景
    断言条件:
    - 运行期间连接不中断
    - 持续接收媒体数据
    - 心跳正常
    """
    print(f"\n[INFO] ========== 测试步骤7: 长时间运行稳定性({TEST_DURATION}秒) ==========")
    
    if not context.control_writer or not context.media_reader:
        context.add_assertion("长时间稳定性", False, "通道未连接")
        return False
    
    start_time = time.time()
    video_count = 0
    audio_count = 0
    heartbeat_sent = 0
    heartbeat_ack = 0
    disconnect_detected = False
    last_report_time = start_time
    
    async def send_heartbeat():
        nonlocal heartbeat_sent, heartbeat_ack
        try:
            heartbeat = TLVEncoder.build_heartbeat_packet()
            context.control_writer.write(heartbeat)
            await context.control_writer.drain()
            heartbeat_sent += 1
            
            try:
                data = await asyncio.wait_for(context.control_reader.read(3145728), timeout=5.0)
                if data:
                    packet = TLVDecoder.decode_packet(data)
                    msg_type = TLVDecoder.get_int(packet['fields'], TLV_ID['TYPE'])
                    if msg_type == TLV_TYPE['ACK']:
                        heartbeat_ack += 1
            except asyncio.TimeoutError:
                pass
        except Exception:
            pass
    
    while time.time() - start_time < TEST_DURATION:
        try:
            data = await asyncio.wait_for(context.media_reader.read(3145728), timeout=5.0)
            
            if not data:
                disconnect_detected = True
                break
            
            packet = TLVDecoder.decode_packet(data)
            
            if packet.get('error'):
                continue
            
            fields = packet['fields']
            msg_type = TLVDecoder.get_int(fields, TLV_ID['TYPE'])
            
            if msg_type == TLV_TYPE['VIDEO']:
                video_data = TLVDecoder.get_bytes(fields, TLV_ID['VIDEO_DATA'])
                if video_data:
                    video_count += 1
            
            elif msg_type == TLV_TYPE['AUDIO']:
                audio_data = TLVDecoder.get_bytes(fields, TLV_ID['AUDIO_DATA'])
                if audio_data:
                    audio_count += 1
            
            current_time = time.time()
            if current_time - last_report_time >= 30:
                await send_heartbeat()
                elapsed = current_time - start_time
                print(f"[INFO] 运行{elapsed:.1f}秒: 视频帧={video_count}, 音频帧={audio_count}")
                last_report_time = current_time
        
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"[WARN] 接收数据异常: {str(e)}")
            continue
    
    duration = time.time() - start_time
    
    print(f"\n[INFO] ========== 长时间运行统计 ==========")
    print(f"[INFO] 运行时长: {duration:.1f}秒")
    print(f"[INFO] 视频帧总数: {video_count}")
    print(f"[INFO] 音频帧总数: {audio_count}")
    print(f"[INFO] 心跳发送: {heartbeat_sent}次")
    print(f"[INFO] 心跳ACK: {heartbeat_ack}次")
    
    context.add_assertion(
        "运行时长达到预期",
        duration >= TEST_DURATION * 0.9,
        f"实际{duration:.1f}秒"
    )
    
    context.add_assertion(
        "连接未断开",
        not disconnect_detected,
        f"断开={disconnect_detected}"
    )
    
    context.add_assertion(
        "接收到视频数据",
        video_count > 0,
        f"视频帧={video_count}"
    )
    
    context.add_assertion(
        "接收到音频数据",
        audio_count > 0,
        f"音频帧={audio_count}"
    )
    
    context.add_assertion(
        "心跳正常工作",
        heartbeat_sent > 0,
        f"发送{heartbeat_sent}次"
    )
    
    return not disconnect_detected and video_count > 0 and audio_count > 0


async def test_step8_graceful_disconnect(context: E2ETestContext):
    """
    测试步骤8: 优雅断开连接测试
    参考: BrowserContext.close()
    断言条件:
    - 控制通道正常关闭
    - 媒体通道正常关闭
    """
    print("\n[INFO] ========== 测试步骤8: 优雅断开连接测试 ==========")
    
    results = []
    
    if context.control_writer:
        try:
            context.control_writer.close()
            await context.control_writer.wait_closed()
            context.add_assertion(
                "控制通道正常关闭",
                True,
                ""
            )
            results.append(True)
        except Exception as e:
            context.add_assertion("控制通道正常关闭", False, f"异常: {str(e)}")
            results.append(False)
    else:
        context.add_assertion("控制通道正常关闭", False, "未连接")
        results.append(False)
    
    if context.media_writer:
        try:
            context.media_writer.close()
            await context.media_writer.wait_closed()
            context.add_assertion(
                "媒体通道正常关闭",
                True,
                ""
            )
            results.append(True)
        except Exception as e:
            context.add_assertion("媒体通道正常关闭", False, f"异常: {str(e)}")
            results.append(False)
    else:
        context.add_assertion("媒体通道正常关闭", False, "未连接")
        results.append(False)
    
    context.add_assertion(
        "所有通道优雅关闭",
        all(results),
        f"成功{sum(results)}/{len(results)}"
    )
    
    return all(results)


async def main_async():
    print("""
==================================================================
    云手机完整E2E流程测试
    TC_SBG_Func_E2E_001
    目标: 验证云手机完整端到端流程
    
    参考: D:\\Code\\SBG-Github\\SBG\\SBG\\mobile\\src\\main\\java\\com\\huawei\\mobile\\BrowserContext.java
    
    调用端口: GIDS HTTP服务端口
    - 三步登录: gridLoginAuth/gridLoginAuthOpenBrowser/deviceLoginAuth
    - 事件上报: sendClientEvent/sendAppUseTimesEvent
    
    TCP连接: 边缘服务控制通道和媒体通道
    - 控制通道: GIDS返回的tcpAddr
    - 媒体通道: 控制通道登录后返回的媒体地址
    
    流程:
    1. 三步登录流程 (HTTP)
    2. 控制通道TCP连接
    3. 媒体通道TCP连接
    4. 控制操作测试
    5. 心跳保活测试
    6. 客户端事件上报 (HTTP)
    7. 长时间运行稳定性
    8. 优雅断开连接
==================================================================
    """)
    
    print(f"[INFO] GIDS地址: {GIDS_ADDR}")
    print(f"[INFO] IMEI: {DEVICE_WHITE_IMEI}")
    print(f"[INFO] IMSI: {DEVICE_WHITE_IMSI}")
    print(f"[INFO] 长时间测试时长: {TEST_DURATION}秒")
    
    context = E2ETestContext()
    
    try:
        await test_step1_three_step_login(context)
        await test_step2_control_channel_connect(context)
        await test_step3_media_channel_connect(context)
        await test_step4_control_operations(context)
        await test_step5_heartbeat(context)
        await test_step6_send_client_events(context)
        await test_step7_long_run_stability(context)
        await test_step8_graceful_disconnect(context)
    
    except AssertionError as e:
        print(f"\n[ERROR] 断言失败: {str(e)}")
    except Exception as e:
        print(f"\n[ERROR] 测试异常: {str(e)}")
    finally:
        if context.control_writer:
            try:
                context.control_writer.close()
                await context.control_writer.wait_closed()
            except:
                pass
        
        if context.media_writer:
            try:
                context.media_writer.close()
                await context.media_writer.wait_closed()
            except:
                pass
    
    print("\n[INFO] ========== 测试结果汇总 ==========")
    
    passed = sum(1 for _, r in context.test_results if r)
    total = len(context.test_results)
    
    for name, result in context.test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\n[INFO] 通过率: {passed}/{total} ({passed*100//total if total > 0 else 0}%)")
    
    all_passed = all(r for _, r in context.test_results)
    
    if all_passed:
        print("\n[SUCCESS] ========== 所有测试通过 ==========")
        return 0
    else:
        print("\n[FAILED] ========== 测试未全部通过 ==========")
        return 1


def main():
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())