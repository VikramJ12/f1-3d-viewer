from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
import sys

from track_loader import TrackLoader
from car_system import CarSystem
from telemetry_display import TelemetryDisplay

class F1Viewer(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Setup basic scene
        self.setup_scene()
        self.setup_camera()
        
        # Initialize systems
        self.track_loader = TrackLoader(self.render, self.loader)
        self.car_system = CarSystem(self.render, self.loader)
        self.telemetry_display = TelemetryDisplay()
        
        # Load track and cars
        self.setup_track_and_cars()
        
        # Start update task
        self.taskMgr.add(self.update_scene, "update_scene")
        
    def setup_scene(self):
        """Setup basic lighting and environment"""
        # Add ambient light
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.4, 0.4, 0.4, 1))
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)
        
        # Add directional light
        dir_light = DirectionalLight('dir_light')
        dir_light.setColor((0.8, 0.8, 0.8, 1))
        dir_light.setDirection((-1, -1, -1))
        dir_light_np = self.render.attachNewNode(dir_light)
        self.render.setLight(dir_light_np)
        
        # Set background color
        self.setBackgroundColor(0.1, 0.3, 0.6)  # Sky blue
    
    def setup_camera(self):
        """Setup camera for track overview"""
        self.camera.setPos(0, -10, 5)  # Above and behind track
        self.camera.lookAt(0, 0, 0)
        
        # Enable mouse control
        self.disableMouse()
        
    def setup_track_and_cars(self):
        """Load track and create cars"""
        print("Loading Monaco track...")
        track_node = self.track_loader.create_monaco_track()
        
        if track_node:
            print("Track loaded successfully")
            
            # Create cars
            print("Creating cars...")
            self.car_system.create_cars(3)  # Start with 3 cars
            self.car_system.set_track_data(self.track_loader.track_data)
            
            # Load real data for first car (example)
            print("Loading real lap data...")
            real_data = self.car_system.load_real_lap_data(2023, 'Monaco', 'FP1', 'VER')
            if real_data:
                print(f"Loaded data for {real_data['driver']}")
                self.telemetry_display.set_lap_data(real_data)
        else:
            print("Failed to load track")
    
    def update_scene(self, task):
        """Main update loop"""
        dt = globalClock.getDt()
        
        # Update cars
        self.car_system.update_cars(dt)
        
        # Update telemetry display
        current_time = task.time
        self.telemetry_display.update(current_time)
        
        return task.cont

if __name__ == "__main__":
    app = F1Viewer()
    app.run()
