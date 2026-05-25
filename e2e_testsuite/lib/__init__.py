#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E测试套公共模块
提供TLV编解码、GIDS客户端、媒体流处理等核心功能
"""

from .tlv_encoder import TLVEncoder, TLVDecoder, TLV_ID, TLV_TYPE, TLV_MAGIC, CTRL_TYPE_MAP
from .gids_client import GIDSClient, DeviceLoginRequest, DeviceLoginResponse

__version__ = "1.0.0"
__all__ = [
    "TLVEncoder",
    "TLVDecoder",
    "TLV_ID",
    "TLV_TYPE",
    "TLV_MAGIC",
    "CTRL_TYPE_MAP",
    "GIDSClient",
    "DeviceLoginRequest",
    "DeviceLoginResponse",
]