#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
媒体流处理模块
用于解析和处理视频帧、音频帧数据
"""

import struct
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class VideoFrame:
    """视频帧"""
    frame_type: int
    data: bytes
    timestamp: float = 0.0
    
    def is_keyframe(self) -> bool:
        return self.frame_type in [1, 4, 5]
    
    def get_frame_type_name(self) -> str:
        names = {
            1: "I帧",
            2: "P帧",
            3: "B帧",
            4: "SI帧",
            5: "SP帧",
            6: "P_IDR帧",
        }
        return names.get(self.frame_type, f"未知({self.frame_type})")


@dataclass
class AudioFrame:
    """音频帧"""
    data: bytes
    timestamp: float = 0.0
    sample_rate: int = 46000
    channels: int = 1


class MediaHandler:
    """媒体流处理器"""
    
    VIDEO_FRAME_TYPE = 0x01
    AUDIO_FRAME_TYPE = 0x02
    
    def __init__(self):
        self.video_frames: List[VideoFrame] = []
        self.audio_frames: List[AudioFrame] = []
        
        self.video_total_size: int = 0
        self.audio_total_size: int = 0
        
        self.first_video_time: Optional[float] = None
        self.first_audio_time: Optional[float] = None
        self.last_video_time: Optional[float] = None
        self.last_audio_time: Optional[float] = None
    
    def parse_ws_frame(self, data: bytes) -> Optional[Tuple[int, bytes]]:
        """解析WebSocket媒体帧"""
        if len(data) < 1:
            return None
        
        frame_type = data[0]
        
        if frame_type == self.VIDEO_FRAME_TYPE:
            if len(data) < 2:
                return None
            video_info = data[1]
            video_data = data[2:]
            return (self.VIDEO_FRAME_TYPE, data[1:], video_info)
        
        elif frame_type == self.AUDIO_FRAME_TYPE:
            audio_data = data[1:]
            return (self.AUDIO_FRAME_TYPE, audio_data, None)
        
        return None
    
    def handle_video_frame(self, data: bytes, frame_info: int, timestamp: float = None) -> VideoFrame:
        """处理视频帧"""
        import time
        ts = timestamp or time.time()
        
        frame = VideoFrame(
            frame_type=frame_info,
            data=data,
            timestamp=ts,
        )
        
        self.video_frames.append(frame)
        self.video_total_size += len(data)
        
        if self.first_video_time is None:
            self.first_video_time = ts
        self.last_video_time = ts
        
        return frame
    
    def handle_audio_frame(self, data: bytes, timestamp: float = None) -> AudioFrame:
        """处理音频帧"""
        import time
        ts = timestamp or time.time()
        
        frame = AudioFrame(
            data=data,
            timestamp=ts,
        )
        
        self.audio_frames.append(frame)
        self.audio_total_size += len(data)
        
        if self.first_audio_time is None:
            self.first_audio_time = ts
        self.last_audio_time = ts
        
        return frame
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        import time
        
        video_duration = 0.0
        audio_duration = 0.0
        
        if self.first_video_time and self.last_video_time:
            video_duration = self.last_video_time - self.first_video_time
        if self.first_audio_time and self.last_audio_time:
            audio_duration = self.last_audio_time - self.first_audio_time
        
        return {
            'video_frame_count': len(self.video_frames),
            'audio_frame_count': len(self.audio_frames),
            'video_total_size': self.video_total_size,
            'audio_total_size': self.audio_total_size,
            'video_avg_size': self.video_total_size / len(self.video_frames) if self.video_frames else 0,
            'audio_avg_size': self.audio_total_size / len(self.audio_frames) if self.audio_frames else 0,
            'video_duration': video_duration,
            'audio_duration': audio_duration,
            'video_fps': len(self.video_frames) / video_duration if video_duration > 0 else 0,
            'keyframe_count': sum(1 for f in self.video_frames if f.is_keyframe()),
        }
    
    def clear(self):
        """清空数据"""
        self.video_frames.clear()
        self.audio_frames.clear()
        self.video_total_size = 0
        self.audio_total_size = 0
        self.first_video_time = None
        self.first_audio_time = None
        self.last_video_time = None
        self.last_audio_time = None
    
    def save_video_to_file(self, filepath: str) -> int:
        """保存视频帧到文件"""
        saved = 0
        with open(filepath, 'wb') as f:
            for frame in self.video_frames:
                f.write(bytes([0x01, frame.frame_type]))
                f.write(frame.data)
                saved += 1
        return saved
    
    def save_audio_to_file(self, filepath: str) -> int:
        """保存音频帧到文件"""
        saved = 0
        with open(filepath, 'wb') as f:
            for frame in self.audio_frames:
                f.write(bytes([0x02]))
                f.write(frame.data)
                saved += 1
        return saved
    
    def print_summary(self):
        """打印摘要"""
        stats = self.get_stats()
        
        print(f"\n[INFO] ========== 媒体流统计 ==========")
        print(f"[INFO] 视频帧总数: {stats['video_frame_count']}")
        print(f"[INFO] 视频总大小: {stats['video_total_size']} 字节 ({stats['video_total_size']/1024:.1f} KB)")
        print(f"[INFO] 视频平均帧大小: {stats['video_avg_size']:.1f} 字节")
        print(f"[INFO] 视频时长: {stats['video_duration']:.1f} 秒")
        print(f"[INFO] 视频帧率: {stats['video_fps']:.1f} fps")
        print(f"[INFO] 关键帧数量: {stats['keyframe_count']}")
        print(f"[INFO] 音频帧总数: {stats['audio_frame_count']}")
        print(f"[INFO] 音频总大小: {stats['audio_total_size']} 字节 ({stats['audio_total_size']/1024:.1f} KB)")
        print(f"[INFO] 音频平均帧大小: {stats['audio_avg_size']:.1f} 字节")
        print(f"[INFO] 音频时长: {stats['audio_duration']:.1f} 秒")