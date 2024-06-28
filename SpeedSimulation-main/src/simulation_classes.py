import traci
import sumolib
import pandas as pd

# Function to start the SUMO simulation
def startSumo(config_file):
    sumoBinary = sumolib.checkBinary('sumo-gui')
    traci.start([
        sumoBinary,
        "-c", config_file,
        "--max-depart-delay", "-1",
        "--waiting-time-memory", "99999",
        "--time-to-teleport", "-1"
    ])

# Class for defining and adding vehicles
class Vehicles:
    def __init__(self, vehicle_id, route_id, color=(0, 255, 0, 255), max_speed=30, accel=20, depart_speed="20", depart_lane=0):
        self.vehicle_id = vehicle_id
        self.route_id = route_id
        self.color = color
        self.max_speed = max_speed
        self.accel = accel
        self.depart_speed = depart_speed
        self.depart_lane = depart_lane
       
    def add(self):
        try:
            traci.vehicle.add(self.vehicle_id, self.route_id, departSpeed=self.depart_speed, departLane=self.depart_lane)
            traci.vehicle.setColor(self.vehicle_id, self.color)
            traci.vehicle.setMaxSpeed(self.vehicle_id, self.max_speed)
            traci.vehicle.setAccel(self.vehicle_id, self.accel)
        except traci.exceptions.TraCIException as e:
            print(f"Failed to add vehicle {self.vehicle_id}: {e}")

# Class for defining and adding routes
class Routes:
    def __init__(self, route_id, edge_ids):
        self.route_id = route_id
        self.edge_ids = edge_ids

    def add(self):
        traci.route.add(self.route_id, self.edge_ids)

if __name__ == "__main__":
    config_file = "cfgs/hanoi/osm.sumocfg"
    startSumo(config_file)
    all_edge_ids = traci.edge.getIDList() # Get all edge IDs in the network
    all_lane_ids = traci.lane.getIDList() # Get all lane IDs in the network

    # Set the maximum speed of all lanes to 999 m/s
    for lane_id in all_lane_ids:
        traci.lane.setMaxSpeed(lane_id, 999)
    
    step = 0 # Initialize the simulation step counter
    # Load CSV data
    csv_file = "/Users/feiyucao/Downloads/SpeedSimulation-main/Data/rawTrafficData/Hanoi.csv"
    df = pd.read_csv(csv_file)
    


    # Check if CSV is loaded correctly
    print("CSV loaded successfully. First few rows:")
    print("CSV loaded successfully. Total records:", df.shape[0])
    print(df.head())

    # Filter data
    df_filtered = df[(df['day'] == 3) & (df['start_time'] == '7:15:00')&(df['vehicle_ownership_type']=='Private')]
    df_filtered['steps'] = df_filtered['steps'].astype(int)

    # Check the filtered results
    print("Filtered data successfully. Number of rows after filtering:", df_filtered.shape[0])
    print("First few rows of filtered data:")
    print(df_filtered.head())
    cumulative_speeds = {}
    cumulative_times = {}
    vehicle_counts = {}

    for step in range(6300):
        print(f"Simulation step: {step}")
        traci.simulationStep()

        vehicles_to_add = df_filtered[df_filtered['steps'] == step]
        num_vehicles_to_add = vehicles_to_add.shape[0]
        
        if num_vehicles_to_add > 0:
            print(f"Step {step}: Adding {num_vehicles_to_add} vehicles")
    
            route = Routes(f"route_id_{step}", ["817484210#0", "817484210#3"])  # Create a new route
            route.add()

            vehicle_ids = vehicles_to_add['sid'].tolist()
            depart_lanes = vehicles_to_add['sid'].astype(int).tolist()  # Ensure depart_lanes are integers
            depart_speeds = vehicles_to_add['speed'].tolist()

            for i in range(num_vehicles_to_add):
                vehicle_id = str(vehicle_ids[i])
                depart_lane = int(depart_lanes[i])  # Ensure depart_lane is an integer
                depart_speed = float(depart_speeds[i])  # Ensure depart_speed is a float

            
                vehicle = Vehicles(vehicle_id,  f"route_id_{step}", depart_lane=depart_lane, depart_speed=depart_speed)
                vehicle.add()


                
           

        active_vehicle_ids = traci.vehicle.getIDList()
        for vid in active_vehicle_ids:
            speed = traci.vehicle.getSpeed(vid)
            if vid not in cumulative_speeds:
                cumulative_speeds[vid] = 0
                cumulative_times[vid] = 0
                vehicle_counts[vid] = 0

            cumulative_speeds[vid] += speed
            cumulative_times[vid] += 1  # Increment time by 1 step for each vehicle
            vehicle_counts[vid] += 1

        if step == 6299:  # Calculate averages at the last step or whenever you need
            total_avg_speed = sum(cumulative_speeds.values()) / sum(vehicle_counts.values())
            total_avg_time = sum(cumulative_times.values()) / len(cumulative_times)
            print(f"Average speed of all vehicles: {total_avg_speed} m/s")
            print(f"Average travel time per vehicle: {total_avg_time} steps")

    traci.close()
