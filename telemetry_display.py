import numpy as np
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *

class TelemetryDisplay:
    def __init__(self):
        self.lap_data = None
        self.current_time = 0
        self.text_objects = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Create telemetry UI elements"""
        # Speed display
        self.text_objects['speed'] = OnscreenText(
            text="Speed: 0 km/h",
            pos=(-1.3, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Throttle display
        self.text_objects['throttle'] = OnscreenText(
            text="Throttle: 0%",
            pos=(-1.3, 0.8),
            scale=0.07,
            fg=(0, 1, 0, 1),
            align=TextNode.ALeft
        )
        
        # Brake display
        self.text_objects['brake'] = OnscreenText(
            text="Brake: 0%",
            pos=(-1.3, 0.7),
            scale=0.07,
            fg=(1, 0, 0, 1),
            align=TextNode.ALeft
        )
        
        # DRS display
        self.text_objects['drs'] = OnscreenText(
            text="DRS: OFF",
            pos=(-1.3, 0.6),
            scale=0.07,
            fg=(1, 1, 0, 1),
            align=TextNode.ALeft
        )
        
        # Gear display
        self.text_objects['gear'] = OnscreenText(
            text="Gear: 1",
            pos=(-1.3, 0.5),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Lap time display
        self.text_objects['lap_time'] = OnscreenText(
            text="Lap Time: --:--.---",
            pos=(-1.3, 0.3),
            scale=0.08,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
    
    def set_lap_data(self, lap_data):
        """Set the lap data for telemetry"""
        self.lap_data = lap_data
        if lap_data and 'telemetry' in lap_data:
            print(f"Telemetry data loaded: {len(lap_data['telemetry'])} data points")
    
    def update(self, current_time):
        """Update telemetry display"""
        if not self.lap_data or 'telemetry' not in self.lap_data:
            return
        
        telemetry = self.lap_data['telemetry']
        
        # Calculate current position in telemetry data
        # Cycle through the data based on current time
        cycle_time = 90  # 90 seconds to complete one lap cycle
        progress = (current_time % cycle_time) / cycle_time
        
        data_index = int(progress * len(telemetry))
        if data_index >= len(telemetry):
            data_index = len(telemetry) - 1
        
        # Get current telemetry values
        current_data = telemetry.iloc[data_index]
        
        # Update displays
        speed = getattr(current_data, 'Speed', 0)
        throttle = getattr(current_data, 'Throttle', 0)
        brake = getattr(current_data, 'Brake', 0)
        drs = getattr(current_data, 'DRS', 0)
        gear = getattr(current_data, 'nGear', 1)
        
        self.text_objects['speed'].setText(f"Speed: {speed:.1f} km/h")
        self.text_objects['throttle'].setText(f"Throttle: {throttle:.0f}%")
        self.text_objects['brake'].setText(f"Brake: {brake:.0f}%")
        self.text_objects['drs'].setText(f"DRS: {'ON' if drs > 0 else 'OFF'}")
        self.text_objects['gear'].setText(f"Gear: {gear}")
        
        # Update lap time
        if 'lap_time' in self.lap_data:
            lap_time = self.lap_data['lap_time']
            if lap_time:
                total_seconds = lap_time.total_seconds()
                minutes = int(total_seconds // 60)
                seconds = total_seconds % 60
                self.text_objects['lap_time'].setText(f"Lap Time: {minutes}:{seconds:06.3f}")
