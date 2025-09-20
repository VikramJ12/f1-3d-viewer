import numpy as np
from panda3d.core import *
from direct.task import Task
import fastf1

class Car:
    def __init__(self, render, loader, car_id, color):
        self.render = render
        self.loader = loader
        self.car_id = car_id
        self.color = color
        
        # Car state
        self.position = [0, 0, 0]
        self.rotation = 0
        self.speed = 0
        self.throttle = 0
        self.brake = 0
        self.drs = False
        self.tire_temps = [80, 80, 80, 80]  # FL, FR, RL, RR
        
        # Create car model
        self.model = self.create_car_model()
        
    def create_car_model(self):
        """Create a simple F1 car model"""
        # Create car body (main chassis)
        car_node = self.render.attachNewNode(f"car_{self.car_id}")
        
        # Main body
        body = self.loader.loadModel("environment")  # Placeholder
        if not body:
            # Create simple box as car body
            body = car_node.attachNewNode("body")
            self.create_car_geometry(body)
        
        body.reparentTo(car_node)
        body.setScale(0.05, 0.15, 0.03)  # Scale for F1 car proportions
        body.setColor(self.color)
        
        # Add wheels
        self.create_wheels(car_node)
        
        return car_node
    
    def create_car_geometry(self, parent):
        """Create simple car geometry"""
        # Create a simple box for the car
        format = GeomNode.getDefaultFormat()
        vdata = GeomVertexData('car', format, Geom.GStatic)
        vdata.setNumRows(8)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        # Box vertices
        vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        
        for v in vertices:
            vertex.addData3(v[0], v[1], v[2])
        
        # Create box faces
        geom = Geom(vdata)
        
        # Define faces
        faces = [
            [0,1,2,3], [4,7,6,5], [0,4,5,1],
            [2,6,7,3], [0,3,7,4], [1,5,6,2]
        ]
        
        for face in faces:
            prim = GeomTriangles(Geom.UHStatic)
            prim.addVertices(face[0], face[1], face[2])
            prim.addVertices(face[0], face[2], face[3])
            geom.addPrimitive(prim)
        
        geom_node = GeomNode('car_geom')
        geom_node.addGeom(geom)
        parent.attachNewNode(geom_node)
    
    def create_wheels(self, parent):
        """Add wheels to the car"""
        wheel_positions = [
            (-0.8, -0.6, -0.3), (0.8, -0.6, -0.3),  # Front wheels
            (-0.8, 0.6, -0.3), (0.8, 0.6, -0.3)     # Rear wheels
        ]
        
        for i, pos in enumerate(wheel_positions):
            wheel = parent.attachNewNode(f"wheel_{i}")
            # Create simple cylinder for wheel (simplified)
            wheel.setPos(pos[0] * 0.05, pos[1] * 0.15, pos[2] * 0.03)
            wheel.setScale(0.01, 0.01, 0.01)
            wheel.setColor(0.1, 0.1, 0.1, 1)  # Dark wheels
    
    def update_position(self, track_data, progress):
        """Update car position along track"""
        if track_data is None:
            return
            
        # Calculate position along track
        total_distance = track_data['distance'][-1]
        current_distance = (progress * total_distance) % total_distance
        
        # Find closest track point
        distances = track_data['distance']
        idx = np.searchsorted(distances, current_distance)
        
        if idx >= len(distances):
            idx = len(distances) - 1
        
        # Set car position
        x = track_data['x_coords'][idx] / 100
        y = track_data['z_coords'][idx] / 100
        z = -track_data['y_coords'][idx] / 100
        
        self.model.setPos(x, y + 0.02, z)  # Slightly above track
        
        # Calculate rotation (facing direction)
        if idx < len(distances) - 1:
            next_x = track_data['x_coords'][idx + 1] / 100
            next_z = -track_data['y_coords'][idx + 1] / 100
            
            dx = next_x - x
            dz = next_z - z
            rotation = np.degrees(np.arctan2(dx, dz))
            self.model.setH(rotation)

class CarSystem:
    def __init__(self, render, loader):
        self.render = render
        self.loader = loader
        self.cars = []
        self.track_data = None
        self.race_time = 0
        
    def create_cars(self, num_cars=5):
        """Create multiple cars with different colors"""
        colors = [
            (1, 0, 0, 1),    # Red
            (0, 0, 1, 1),    # Blue
            (0, 1, 0, 1),    # Green
            (1, 1, 0, 1),    # Yellow
            (1, 0, 1, 1),    # Magenta
        ]
        
        for i in range(num_cars):
            color = colors[i % len(colors)]
            car = Car(self.render, self.loader, i, color)
            self.cars.append(car)
    
    def set_track_data(self, track_data):
        """Set track data for car positioning"""
        self.track_data = track_data
    
    def update_cars(self, dt):
        """Update all cars"""
        self.race_time += dt
        
        for i, car in enumerate(self.cars):
            # Each car has slight offset in progress for train effect
            car_progress = (self.race_time * 0.1 + i * 0.1) % 1.0
            car.update_position(self.track_data, car_progress)
    
    def load_real_lap_data(self, year, gp, session, driver):
        """Load real F1 data for one car"""
        try:
            session_data = fastf1.get_session(year, gp, session)
            session_data.load()
            
            driver_laps = session_data.laps.pick_driver(driver)
            if len(driver_laps) == 0:
                print(f"No data found for driver {driver}")
                return None
                
            # Get fastest lap
            fastest_lap = driver_laps.pick_fastest()
            telemetry = fastest_lap.get_telemetry()
            
            return {
                'telemetry': telemetry,
                'lap_time': fastest_lap['LapTime'],
                'driver': driver
            }
        except Exception as e:
            print(f"Error loading lap data: {e}")
            return None
