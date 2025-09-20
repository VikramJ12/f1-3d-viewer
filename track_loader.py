import numpy as np
from panda3d.core import *
from direct.task import Task
import fastf1

class TrackLoader:
    def __init__(self, render, loader):
        self.render = render
        self.loader = loader
        self.track_node = None
        self.track_data = None
        
    def create_monaco_track(self):
        """Create a simplified Monaco track from GPS data"""
        # Load Monaco session for track layout
        session = fastf1.get_session(2023, 'Monaco', 'FP1')
        session.load()
        
        # Get a representative lap for track shape
        fastest_lap = session.laps.pick_fastest()
        pos_data = fastest_lap.get_pos_data()
        
        # Store track data for car positioning
        self.track_data = {
            'x_coords': pos_data['X'].values,
            'y_coords': pos_data['Y'].values,
            'z_coords': pos_data['Z'].values,
            'distance': pos_data['Distance'].values
        }
        
        # Create track geometry
        self.create_track_mesh()
        return self.track_node
    
    def create_track_mesh(self):
        """Create 3D track mesh from coordinates"""
        # Convert F1 coordinates to our coordinate system
        x_coords = self.track_data['x_coords'] / 100  # Scale down
        y_coords = self.track_data['z_coords'] / 100  # Z becomes Y (height)
        z_coords = -self.track_data['y_coords'] / 100  # Y becomes -Z (track layout)
        
        # Create track surface
        track_points = []
        track_width = 0.15  # Track width in our scale
        
        for i in range(len(x_coords)-1):
            # Calculate track direction
            dx = x_coords[i+1] - x_coords[i]
            dz = z_coords[i+1] - z_coords[i]
            length = np.sqrt(dx*dx + dz*dz)
            
            if length > 0:
                # Normalize direction
                dx /= length
                dz /= length
                
                # Calculate perpendicular for track width
                perp_x = -dz * track_width
                perp_z = dx * track_width
                
                # Create track segment vertices
                left_point = (x_coords[i] + perp_x, y_coords[i], z_coords[i] + perp_z)
                right_point = (x_coords[i] - perp_x, y_coords[i], z_coords[i] - perp_z)
                track_points.extend([left_point, right_point])
        
        # Create track node
        self.track_node = self.render.attachNewNode("track")
        self.create_track_geometry(track_points)
        
        # Set track appearance
        self.track_node.setColor(0.3, 0.3, 0.3, 1)  # Dark gray
        
    def create_track_geometry(self, points):
        """Create the actual track geometry"""
        # Create a simple procedural track
        # This is a simplified version - in production you'd use proper mesh generation
        format = GeomNode.getDefaultFormat()
        vdata = GeomVertexData('track', format, Geom.GStatic)
        vdata.setNumRows(len(points))
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        for point in points:
            vertex.addData3(point[0], point[1], point[2])
        
        # Create track surface
        geom = Geom(vdata)
        prim = GeomTristrips(Geom.UHStatic)
        
        for i in range(0, len(points)-2, 2):
            prim.addVertex(i)
            prim.addVertex(i+1)
            prim.addVertex(i+2)
            prim.addVertex(i+3)
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        geom_node = GeomNode('track_geom')
        geom_node.addGeom(geom)
        self.track_node.attachNewNode(geom_node)
