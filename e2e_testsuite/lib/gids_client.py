#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIDS HTTP客户端模块
参考: mobile/src/main/java/com/huawei/mobile/BrowserContext.java
提供三步登录流程和设备管理API
"""

import json
import os
import urllib3
from typing import Dict, Optional
from dataclasses import dataclass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
    import aiohttp
except ImportError as e:
    print(f"[ERROR] 缺少依赖: {e}")
    print("[INFO] 请运行: pip install requests aiohttp")
    raise


@dataclass
class DeviceLoginRequest:
    """设备登录请求"""
    imei: str
    imsi: str
    manufacturer: str = "Huawei"
    model: str = "Mate60"
    app_type: int = 5
    extend_model: str = "default"
    country: str = "CN"
    platform: int = 1
    width: int = 240
    height: int = 320
    mcc: str = "460"
    mnc: str = "00"
    lac: str = "100"
    ci: str = "5.21"
    rxlev: int = -72
    total_kb: int = 1424122
    free_kb: int = 1424122
    client_language: str = "zh_CN"
    device_type: int = 2
    
    def to_dict(self) -> Dict:
        return {
            "imei": self.imei,
            "imsi": self.imsi,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "appType": str(self.app_type),
            "extendModel": self.extend_model,
            "country": self.country,
            "platform": str(self.platform),
            "width": str(self.width),
            "height": str(self.height),
            "mcc": self.mcc,
            "mnc": self.mnc,
            "lac": self.lac,
            "ci": self.ci,
            "rxlev": str(self.rxlev),
            "totalKb": str(self.total_kb),
            "freeKb": str(self.free_kb),
            "clientLanguage": self.client_language,
            "deviceType": str(self.device_type),
        }
    
    def get_session_id(self) -> str:
        return f"{self.imei}_{self.imsi}"


@dataclass
class DeviceLoginResponse:
    """设备登录响应"""
    token: str = ""
    tcp_addr: str = ""
    tls_tcp_addr: str = ""
    video_mode: int = 0
    short_addr: str = ""
    node_gateway_url: str = ""
    https_node_gateway_url: str = ""
    node_intranet_way_url: str = ""


class GIDSClient:
    """GIDS HTTP客户端"""
    
    def __init__(self, gids_addr: str, imei: str, imsi: str):
        self.gids_addr = gids_addr
        self.imei = imei
        self.imsi = imsi
        self.request: Optional[DeviceLoginRequest] = None
        self.response: Optional[DeviceLoginResponse] = None
    
    def create_request(self, width: int = 240, height: int = 320, device_type: int = 2, app_type: int = 1) -> DeviceLoginRequest:
        self.request = DeviceLoginRequest(
            imei=self.imei,
            imsi=self.imsi,
            width=width,
            height=height,
            device_type=device_type,
            app_type=app_type,
        )
        return self.request
    
    def grid_login_auth(self) -> Dict:
        """步骤1: gridLoginAuth - 宫格登录认证"""
        url = f"{self.gids_addr}/app-api/devicetcp/app/login/v1/gridLoginAuth"
        request_body = self.request.to_dict()
        
        print(f"\n[REQUEST] ========== 步骤1: gridLoginAuth ==========")
        print(f"[REQUEST] URL: POST {url}")
        print(f"[REQUEST] Body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
        
        try:
            resp = requests.post(url, json=request_body, timeout=30, verify=False)
            result = resp.json()
            
            print(f"\n[RESPONSE] ========== 步骤1: gridLoginAuth ==========")
            print(f"[RESPONSE] Status: {resp.status_code}")
            print(f"[RESPONSE] Body: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] gridLoginAuth请求异常: {e}")
            return {'code': -1, 'message': str(e)}
    
    def grid_login_auth_open_browser(self) -> Dict:
        """步骤2: gridLoginAuthOpenBrowser - 宫格登录打开浏览器"""
        url = f"{self.gids_addr}/app-api/devicetcp/app/login/v1/gridLoginAuthOpenBrowser"
        request_body = self.request.to_dict()
        
        print(f"\n[REQUEST] ========== 步骤2: gridLoginAuthOpenBrowser ==========")
        print(f"[REQUEST] URL: POST {url}")
        print(f"[REQUEST] Body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
        
        try:
            resp = requests.post(url, json=request_body, timeout=30, verify=False)
            result = resp.json()
            
            print(f"\n[RESPONSE] ========== 步骤2: gridLoginAuthOpenBrowser ==========")
            print(f"[RESPONSE] Status: {resp.status_code}")
            print(f"[RESPONSE] Body: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] gridLoginAuthOpenBrowser请求异常: {e}")
            return {'code': -1, 'message': str(e)}
    
    def device_login_auth(self) -> Dict:
        """步骤3: deviceLoginAuth - 设备登录认证"""
        url = f"{self.gids_addr}/app-api/devicetcp/app/login/v1/deviceLoginAuth"
        request_body = self.request.to_dict()
        
        print(f"\n[REQUEST] ========== 步骤3: deviceLoginAuth ==========")
        print(f"[REQUEST] URL: POST {url}")
        print(f"[REQUEST] Body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
        
        try:
            resp = requests.post(url, json=request_body, timeout=30, verify=False)
            result = resp.json()
            
            print(f"\n[RESPONSE] ========== 步骤3: deviceLoginAuth ==========")
            print(f"[RESPONSE] Status: {resp.status_code}")
            print(f"[RESPONSE] Body: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('code') == 200:
                data = result.get('data', {})
                self.response = DeviceLoginResponse(
                    token=data.get('token', ''),
                    tcp_addr=data.get('tcpAddr', ''),
                    tls_tcp_addr=data.get('tlsTcpAddr', ''),
                    video_mode=data.get('videoMode', 0),
                    short_addr=data.get('shortAddr', ''),
                    node_gateway_url=data.get('nodeGateWayUrl', ''),
                    https_node_gateway_url=data.get('httpsNodeGateWayUrl', ''),
                    node_intranet_way_url=data.get('nodeIntranetWayUrl', ''),
                )
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] deviceLoginAuth请求异常: {e}")
            return {'code': -1, 'message': str(e)}
    
    def three_step_login(self, width: int = 240, height: int = 320, device_type: int = 2, app_type: int = 1) -> bool:
        """完整三步登录流程"""
        print(f"\n[INFO] ========== 开始三步登录流程 ==========")
        
        self.create_request(width, height, device_type, app_type)
        
        resp1 = self.grid_login_auth()
        if resp1.get('code') != 200:
            print(f"[FAIL] gridLoginAuth失败")
            return False
        
        resp2 = self.grid_login_auth_open_browser()
        if resp2.get('code') != 200:
            print(f"[FAIL] gridLoginAuthOpenBrowser失败")
            return False
        
        resp3 = self.device_login_auth()
        if resp3.get('code') != 200:
            print(f"[FAIL] deviceLoginAuth失败")
            return False
        
        print(f"[PASS] 三步登录流程完成")
        return True
    
    def send_client_event(self, event_type: int) -> Dict:
        """发送客户端事件"""
        url = f"{self.gids_addr}/app-api/center/public/client/sendClientEvent"
        
        event = {
            "hsman": self.request.manufacturer,
            "hstype": self.request.model,
            "appType": str(self.request.app_type),
            "imei": self.imei,
            "imsi": self.imsi,
            "type": event_type,
        }
        
        print(f"\n[REQUEST] ========== sendClientEvent ==========")
        print(f"[REQUEST] URL: POST {url}")
        print(f"[REQUEST] Body: {json.dumps(event, ensure_ascii=False, indent=2)}")
        
        try:
            resp = requests.post(url, json=event, timeout=30, verify=False)
            result = resp.json()
            
            print(f"\n[RESPONSE] ========== sendClientEvent ==========")
            print(f"[RESPONSE] Status: {resp.status_code}")
            print(f"[RESPONSE] Body: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] sendClientEvent请求异常: {e}")
            return {'code': -1, 'message': str(e)}
    
    def send_use_times_event(self, use_times: int = 100000) -> Dict:
        """发送使用时长事件"""
        url = f"{self.gids_addr}/app-api/center/public/client/sendAppUseTimesEvent"
        
        event = {
            "useTimes": use_times,
            "hsman": self.request.manufacturer,
            "hstype": self.request.model,
            "appType": str(self.request.app_type),
            "appId": str(self.request.app_type),
            "scheight": self.request.height,
            "scwidth": self.request.width,
            "exttype": self.request.extend_model,
            "imei": self.imei,
            "imsi": self.imsi,
            "playMode": 1,
        }
        
        print(f"\n[REQUEST] ========== sendAppUseTimesEvent ==========")
        print(f"[REQUEST] URL: POST {url}")
        print(f"[REQUEST] Body: {json.dumps(event, ensure_ascii=False, indent=2)}")
        
        try:
            resp = requests.post(url, json=event, timeout=30, headers={"Content-Type": "application/json"}, verify=False)
            result = resp.json()
            
            print(f"\n[RESPONSE] ========== sendAppUseTimesEvent ==========")
            print(f"[RESPONSE] Status: {resp.status_code}")
            print(f"[RESPONSE] Body: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] sendAppUseTimesEvent请求异常: {e}")
            return {'code': -1, 'message': str(e)}
    
    async def async_http_post(self, path: str, data: Dict) -> Dict:
        """异步HTTP POST"""
        url = f"{self.gids_addr}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, timeout=30, ssl=False) as resp:
                return await resp.json()