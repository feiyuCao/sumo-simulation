import traci
import sumolib 

"""
This script is a refactored version of the demo.py script. It contains classes for Vehicles and Routes.

"""

color_red = (255, 0, 0, 255)
color_green = (0, 255, 0, 255)
color_blue = (0, 0, 255, 255)

class Vehicles:
    """
    The class Vehicles is used to create vehicles in the simulation.
    
    Parameters:
        vehicle_id (str): The ID of the vehicle.
        route_id (str): The ID of the route the vehicle will follow.

    Attributes:
        vehicle_id (str): The ID of the vehicle.
        route_id (str): The ID of the route the vehicle will follow.
        color (tuple): The color of the vehicle in RGB format.
        max_speed (float): The maximum speed of the vehicle in m/s.
        accel (float): The acceleration of the vehicle in m/s^2.
        depart_speed (str): The speed at which the vehicle departs.
        depart_position (float): The position at which the vehicle departs.
        depart_lane (int): The lane from which the vehicle departs.
        depart_time (int): The time at which the vehicle departs.

    Methods:
        add(): Adds the vehicle to the simulation.
    """
    def __init__(self, vehicle_id, route_id, color=color_green, max_speed=30, accel=20, depart_speed="20",depart_lane = 0):
        self.vehicle_id = vehicle_id
        self.route_id = route_id
        self.color = color
        self.max_speed = max_speed
        self.accel = accel
        self.depart_speed = depart_speed
        self.depart_lane = depart_lane
       
     
    def add(self):
        try:
            traci.vehicle.add(
                self.vehicle_id,
                self.route_id,
                departSpeed=self.depart_speed,
                departLane=self.depart_lane,
            )
            traci.vehicle.setColor(self.vehicle_id, self.color)
            traci.vehicle.setMaxSpeed(self.vehicle_id, self.max_speed)
            traci.vehicle.setAccel(self.vehicle_id, self.accel)
        except traci.exceptions.TraCIException as e:
            print(f"Failed to add vehicle {self.vehicle_id}: {e}")


class Routes:
    """
    The class Routes is used to create routes in the simulation.

    Parameters:
        route_id (str): The ID of the route.
        edge_ids (list): A list of edge IDs that make up the route.

    Attributes:
        route_id (str): The ID of the route.
        edge_ids (list): A list of edge IDs that make up the route.
    
    Methods:
        add(): Adds the route to the simulation.
    """
    def __init__(self, route_id, edge_ids):
        self.route_id = route_id
        self.edge_ids = edge_ids

    def add(self):
        traci.route.add(self.route_id, self.edge_ids)
    
 
def startSumo(config_file):
    sumoBinary = sumolib.checkBinary('sumo-gui')
    traci.start([
        sumoBinary,
        "-c", config_file,
        "--max-depart-delay", "-1",
        "--waiting-time-memory", "99999",
        "--time-to-teleport", "-1"
    ])

if __name__ == "__main__":

    config_file = "cfgs/hanoi/osm.sumocfg"
    startSumo(config_file) # Start the SUMO simulation

    all_edge_ids = traci.edge.getIDList() # Get all edge IDs in the network
    all_lane_ids = traci.lane.getIDList() # Get all lane IDs in the network

    # Set the maximum speed of all lanes to 999 m/s
    for lane_id in all_lane_ids:
        traci.lane.setMaxSpeed(lane_id, 999)
    
    step = 0 # Initialize the simulation step counter
  


    # Run the simulation for 5000 steps
    # Every 10 steps, add a new route and vehicle to the simulation
    for step in range(5000):
        print(f"Simulation step: {step}")
        traci.simulationStep() # Advance the simulation by one step
        if step % 5 == 0:
             
            route = Routes(f"route_id_{step}", ["817484210#0","817484210#3"]) # Create a new route
            route.add()
            vehicle = Vehicles(f"vehicle_id_{step}", f"route_id_{step}",depart_lane= 0) # Create a new vehicle with the new route
            vehicle2 = Vehicles(f"vehicle_id_{step+1}", f"route_id_{step}",depart_lane= 1) 
            vehicle3 = Vehicles(f"vehicle_id_{step+2}", f"route_id_{step}",depart_lane= 2)
        
            vehicle.add()
            vehicle2.add()
            vehicle3.add()
        
         
        if step == 135:
            vehicle_ids = traci.vehicle.getIDList()
            traci.vehicle.setColor(vehicle_ids[-1], color_red)
            traci.vehicle.setSpeed(vehicle_ids[-1], 0)

