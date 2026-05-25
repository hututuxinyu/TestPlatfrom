#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TLV编解码模块
参考: mobile/src/main/java/com/huawei/mobile/encode/TlvEncoder.java
参考: mobile/src/main/java/com/huawei/mobile/common/ID.java
参考: mobile/src/main/java/com/huawei/mobile/common/Type.java
"""

import struct
from typing import Dict, List, Tuple, Optional

TLV_MAGIC = b'mu'

TLV_ID = {
    'TYPE': 1,
    'FACTORY': 2,
    'DEV_TYPE': 3,
    'IMSI': 4,
    'IMEI': 5,
    'LCD_WIDTH': 6,
    'LCD_HEIGHT': 7,
    'AUD_TYPE': 8,
    'ACK_TYPE': 9,
    'CODE': 10,
    'EVENT': 11,
    'CTRL_TYPE': 12,
    'CTRL_VAL': 13,
    'SEQ': 14,
    'AUDIO_DATA': 15,
    'VIDEO_DATA': 16,
    'AUD_SMPRATE': 17,
    'AUD_CHANNEL': 18,
    'APP_TYPE': 19,
    'TCP_ADDR': 20,
    'TOKEN': 21,
    'SESSION_ID': 22,
    'FRAME_TYPE': 23,
    'CTRL_RSP_ELM': 24,
    'CTRL_RSP_INFO': 25,
    'CONTENT': 26,
    'UPLOAD_TYPE': 27,
    'APP_ID': 28,
    'PLAT_TYPE': 29,
    'EXT_TYPE': 30,
    'PLAY_MODE': 37,
    'ABILITY': 42,
    'CLIENT_LANGUAGE': 45,
    'DEVICE_TYPE': 46,
    'NETWORK_TYPE': 48,
    'URL_TYPE': 49,
    'UPLOAD_FILE_TYPE': 34,
    'UPLOAD_FILE_RESULT': 35,
    'FILE_ADDR': 36,
}

TLV_TYPE = {
    'LOGIN': 1,
    'HEARTBEATS': 2,
    'CONTROL': 4,
    'AUDIO': 5,
    'VIDEO': 6,
    'ACK': 7,
    'RETURN_MEDIA': 9,
    'RETURN_CONTROL': 12,
    'MESSAGE': 13,
    'UPLOAD_FILE': 16,
}

CTRL_TYPE_MAP = {
    'up': 1,
    'down': 2,
    'left': 3,
    'right': 4,
    'ok': 5,
    'volume_up': 6,
    'volume_down': 7,
    'menu': 10,
    'back': 11,
    'home': 15,
    'star': 20,
    'hash': 21,
    'touch_click': 100,
    'touch_swipe_up': 101,
    'touch_swipe_down': 102,
    'touch_swipe_left': 103,
    'touch_swipe_right': 104,
}


class TLVEncoder:
    """TLV报文编码器"""
    
    @staticmethod
    def encode_int(value: int) -> bytes:
        return struct.pack('>I', value)
    
    @staticmethod
    def encode_short(value: int) -> bytes:
        return struct.pack('>H', value)
    
    @staticmethod
    def encode_string(value: str) -> bytes:
        return value.encode('utf-8')
    
    @staticmethod
    def build_field(field_id: int, value: bytes) -> bytes:
        return struct.pack('>II', field_id, len(value)) + value
    
    @staticmethod
    def build_packet(fields: List[Tuple[int, bytes]]) -> bytes:
        data = b''.join([TLVEncoder.build_field(id, val) for id, val in fields])
        header = TLV_MAGIC + struct.pack('>II', len(fields), len(data))
        return header + data
    
    @staticmethod
    def build_login_packet(imei: str, imsi: str, token: str,
                           width: int, height: int, app_type: int,
                           manufacturer: str = "Huawei", 
                           model: str = "Mate60",
                           audio_type: str = "mp3",
                           audio_samplerate: int = 46000,
                           audio_channel: int = 1) -> bytes:
        fields = [
            (TLV_ID['TYPE'], TLVEncoder.encode_int(TLV_TYPE['LOGIN'])),
            (TLV_ID['FACTORY'], TLVEncoder.encode_string(manufacturer)),
            (TLV_ID['DEV_TYPE'], TLVEncoder.encode_string(model)),
            (TLV_ID['IMSI'], TLVEncoder.encode_string(imsi)),
            (TLV_ID['IMEI'], TLVEncoder.encode_string(imei)),
            (TLV_ID['LCD_WIDTH'], TLVEncoder.encode_int(width)),
            (TLV_ID['LCD_HEIGHT'], TLVEncoder.encode_int(height)),
            (TLV_ID['APP_TYPE'], TLVEncoder.encode_int(app_type)),
            (TLV_ID['TOKEN'], TLVEncoder.encode_string(token)),
            (TLV_ID['APP_ID'], TLVEncoder.encode_int(app_type)),
            (TLV_ID['EXT_TYPE'], TLVEncoder.encode_string("default")),
            (TLV_ID['PLAT_TYPE'], TLVEncoder.encode_int(1)),
            (TLV_ID['PLAY_MODE'], TLVEncoder.encode_int(1)),
            (TLV_ID['ABILITY'], TLVEncoder.encode_int(1)),
            (TLV_ID['DEVICE_TYPE'], TLVEncoder.encode_int(2)),
            (TLV_ID['CLIENT_LANGUAGE'], TLVEncoder.encode_string("zh_CN")),
            (TLV_ID['AUD_TYPE'], TLVEncoder.encode_string(audio_type)),
            (TLV_ID['AUD_SMPRATE'], TLVEncoder.encode_int(audio_samplerate)),
            (TLV_ID['AUD_CHANNEL'], TLVEncoder.encode_int(audio_channel)),
            (TLV_ID['NETWORK_TYPE'], TLVEncoder.encode_int(1)),
            (TLV_ID['URL_TYPE'], TLVEncoder.encode_string("1")),
        ]
        return TLVEncoder.build_packet(fields)
    
    @staticmethod
    def build_control_packet(ctrl_type: int, ctrl_val: int, session_id: str) -> bytes:
        fields = [
            (TLV_ID['TYPE'], TLVEncoder.encode_int(TLV_TYPE['CONTROL'])),
            (TLV_ID['CTRL_TYPE'], TLVEncoder.encode_int(ctrl_type)),
            (TLV_ID['CTRL_VAL'], TLVEncoder.encode_int(ctrl_val)),
            (TLV_ID['SESSION_ID'], TLVEncoder.encode_string(session_id)),
        ]
        return TLVEncoder.build_packet(fields)
    
    @staticmethod
    def build_touch_packet(x: int, y: int, action: int, session_id: str) -> bytes:
        fields = [
            (TLV_ID['TYPE'], TLVEncoder.encode_int(TLV_TYPE['CONTROL'])),
            (TLV_ID['CTRL_TYPE'], TLVEncoder.encode_int(action)),
            (TLV_ID['CTRL_VAL'], TLVEncoder.encode_int(x)),
            (TLV_ID['SEQ'], TLVEncoder.encode_int(y)),
            (TLV_ID['SESSION_ID'], TLVEncoder.encode_string(session_id)),
        ]
        return TLVEncoder.build_packet(fields)
    
    @staticmethod
    def build_message_packet(upload_type: int, content: str, session_id: str) -> bytes:
        fields = [
            (TLV_ID['TYPE'], TLVEncoder.encode_int(TLV_TYPE['MESSAGE'])),
            (TLV_ID['UPLOAD_TYPE'], TLVEncoder.encode_int(upload_type)),
            (TLV_ID['CONTENT'], TLVEncoder.encode_string(content)),
            (TLV_ID['SESSION_ID'], TLVEncoder.encode_string(session_id)),
        ]
        return TLVEncoder.build_packet(fields)
    
    @staticmethod
    def build_heartbeat_packet() -> bytes:
        fields = [
            (TLV_ID['TYPE'], TLVEncoder.encode_int(TLV_TYPE['HEARTBEATS'])),
        ]
        return TLVEncoder.build_packet(fields)
    
    @staticmethod
    def build_upload_file_packet(file_addr: str, upload_type: int = 1, result: int = 0) -> bytes:
        fields = [
            (TLV_ID['TYPE'], TLVEncoder.encode_int(TLV_TYPE['UPLOAD_FILE'])),
            (TLV_ID['UPLOAD_FILE_TYPE'], TLVEncoder.encode_int(upload_type)),
            (TLV_ID['UPLOAD_FILE_RESULT'], TLVEncoder.encode_int(result)),
            (TLV_ID['FILE_ADDR'], TLVEncoder.encode_string(file_addr)),
        ]
        return TLVEncoder.build_packet(fields)


class TLVDecoder:
    """TLV报文解码器"""
    
    @staticmethod
    def decode_packet(data: bytes) -> Dict:
        if len(data) < 10:
            return {'error': '数据长度不足', 'raw': data}
        
        magic = data[0:2]
        if magic != TLV_MAGIC:
            return {'error': f'魔数错误: {magic}', 'raw': data}
        
        count = struct.unpack('>I', data[2:6])[0]
        data_len = struct.unpack('>I', data[6:10])[0]
        
        if len(data) < 10 + data_len:
            return {'error': '数据不完整', 'raw': data}
        
        fields = {}
        offset = 10
        
        for _ in range(count):
            if offset + 8 > 10 + data_len:
                break
            
            field_id = struct.unpack('>I', data[offset:offset+4])[0]
            field_len = struct.unpack('>I', data[offset+4:offset+8])[0]
            offset += 8
            
            if offset + field_len > 10 + data_len:
                break
            
            field_value = data[offset:offset+field_len]
            offset += field_len
            
            fields[field_id] = field_value
        
        return {
            'magic': magic,
            'count': count,
            'data_len': data_len,
            'fields': fields,
            'raw': data,
        }
    
    @staticmethod
    def get_int(fields: Dict, field_id: int, default: int = 0) -> int:
        if field_id in fields and len(fields[field_id]) >= 4:
            return struct.unpack('>I', fields[field_id][:4])[0]
        return default
    
    @staticmethod
    def get_short(fields: Dict, field_id: int, default: int = 0) -> int:
        if field_id in fields and len(fields[field_id]) >= 2:
            return struct.unpack('>H', fields[field_id][:2])[0]
        return default
    
    @staticmethod
    def get_string(fields: Dict, field_id: int, default: str = "") -> str:
        if field_id in fields:
            return fields[field_id].decode('utf-8', errors='ignore')
        return default
    
    @staticmethod
    def get_bytes(fields: Dict, field_id: int) -> Optional[bytes]:
        return fields.get(field_id)
    
    @staticmethod
    def get_msg_type(fields: Dict) -> int:
        return TLVDecoder.get_int(fields, TLV_ID['TYPE'])
    
    @staticmethod
    def format_packet(packet: Dict) -> str:
        """格式化TLV报文为可读字符串"""
        if packet.get('error'):
            return f"[ERROR] {packet['error']}"
        
        lines = []
        lines.append(f"magic: {packet['magic']}")
        lines.append(f"count: {packet['count']}")
        lines.append(f"data_len: {packet['data_len']}")
        lines.append("fields:")
        
        id_name_map = {v: k for k, v in TLV_ID.items()}
        type_name_map = {v: k for k, v in TLV_TYPE.items()}
        
        for field_id, field_value in packet['fields'].items():
            field_name = id_name_map.get(field_id, f"UNKNOWN_{field_id}")
            
            if field_id == TLV_ID['TYPE']:
                type_value = TLVDecoder.get_int(packet['fields'], field_id)
                type_name = type_name_map.get(type_value, f"UNKNOWN_TYPE_{type_value}")
                lines.append(f"  [{field_id:2d}] {field_name}: {type_value} ({type_name})")
            elif field_id in [TLV_ID['IMEI'], TLV_ID['IMSI'], TLV_ID['TOKEN'], 
                              TLV_ID['TCP_ADDR'], TLV_ID['SESSION_ID'], TLV_ID['CONTENT'],
                              TLV_ID['FACTORY'], TLV_ID['DEV_TYPE'], TLV_ID['CLIENT_LANGUAGE'],
                              TLV_ID['CTRL_RSP_INFO'], TLV_ID['URL_TYPE']]:
                lines.append(f"  [{field_id:2d}] {field_name}: {field_value.decode('utf-8', errors='ignore')}")
            elif field_id == TLV_ID['VIDEO_DATA']:
                lines.append(f"  [{field_id:2d}] {field_name}: <video_data {len(field_value)} bytes>")
            elif field_id == TLV_ID['AUDIO_DATA']:
                lines.append(f"  [{field_id:2d}] {field_name}: <audio_data {len(field_value)} bytes>")
            elif field_id in [TLV_ID['LCD_WIDTH'], TLV_ID['LCD_HEIGHT'], TLV_ID['APP_TYPE'],
                              TLV_ID['APP_ID'], TLV_ID['ACK_TYPE'], TLV_ID['CODE'],
                              TLV_ID['CTRL_TYPE'], TLV_ID['CTRL_VAL'], TLV_ID['SEQ'],
                              TLV_ID['AUD_SMPRATE'], TLV_ID['AUD_CHANNEL'], TLV_ID['FRAME_TYPE'],
                              TLV_ID['CTRL_RSP_ELM'], TLV_ID['UPLOAD_TYPE'], TLV_ID['UPLOAD_FILE_TYPE'],
                              TLV_ID['UPLOAD_FILE_RESULT'], TLV_ID['PLAT_TYPE'], TLV_ID['PLAY_MODE'],
                              TLV_ID['ABILITY'], TLV_ID['DEVICE_TYPE'], TLV_ID['NETWORK_TYPE']]:
                int_value = TLVDecoder.get_int(packet['fields'], field_id)
                lines.append(f"  [{field_id:2d}] {field_name}: {int_value}")
            else:
                lines.append(f"  [{field_id:2d}] {field_name}: {field_value.hex()}")
        
        return '\n'.join(lines)