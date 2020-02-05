import time
import threading
import random
import sys
from collections import deque

# constants
TRAVEL_SPEED = 3 # 3 ft / sec
TIME_FACTOR = 0.001 # 0.001 sec IRL = 1 sec in sim
DIG_SPEED = 1 # 1 cm^3 / sec
CHARGING_SPEED = 1 # 1% / sec
TRAVEL_DRAIN_SPEED = 0.1 # 0.3% / sec
DIG_DRAIN_SPEED = 0.5 # 0.5% / sec
CHARGING_PADS = 4 # 4 rovers can be charged at a time

elapsed = 0

random.seed(1)

class Charger :
    def __init__(self, _capacity) :
        self.capacity = _capacity
        self.rover_queue = deque()
        self.pool = 0
    
    @property
    def get_pool(self) :
        return self.pool

    @property
    def get_queue(self) :
        return self.rover_queue

    @property
    def get_capacity(self) :
        return self.capacity
    
    def enqueue_rover(self, _id) :
        self.rover_queue.append(_id)
    
    def deque_rover(self) :
        self.rover_queue.popleft()

    def increment_pool(self) :
        self.pool += 1
    
    def decrement_pool(self) :
        self.pool -= 1

class Rover :
    def __init__(self, _id, _dist_from_charger) :
        self.id = _id
        self.battery = 100
        self.dist_from_charger = _dist_from_charger
        self.traveled = 0
        self.location = (0,0)
        self.amount_dug = 0
        self.battery_spent_on_travel = 0
        self.battery_spent_on_digging = 0
        self.time_waited = 0
    
    def print_status(self) :
        print("ID: {}\nDistance from lander: {}\nBattery: {:.2f}\nAmount dug: {}\nTraveled: {}\n".format(self.id, self.dist_from_charger, self.battery, self.amount_dug, self.traveled))

    def print_report(self) :
        print("Rover ID: {}\nDistance from lander: {}\nBattery spent on traveling: {:.2f}\nBattery spent on digging: {:.2f}\nTotal amount dug: {}\nTotal distance traveled: {}\nTime waited in queue: {}\n".format(
            self.id, self.dist_from_charger, self.battery_spent_on_travel, self.battery_spent_on_digging, self.amount_dug, self.traveled, self.time_waited)
        )
    
    def wait(self) :
        time.sleep(1 * TIME_FACTOR)

    def charge(self) :
        station.enqueue_rover(self.id)
        print("Rover {} waiting to charge...".format(self.id))
        while ((station.get_pool == station.get_capacity) or (station.get_queue[0] != self.id)) :
            self.wait()
            self.time_waited += 1
        station.deque_rover()
        station.increment_pool()
        print("Rover {} charging...".format(self.id))
        while self.battery < 100 :
            self.battery += 1
            time.sleep(1 * TIME_FACTOR)
        print("Rover {} charging complete...".format(self.id))
        station.decrement_pool()
    
    def travel(self) :
        print("Rover {} traveling...".format(self.id))
        time.sleep((self.dist_from_charger/TRAVEL_SPEED) * TIME_FACTOR)
        self.traveled += (TRAVEL_SPEED * self.dist_from_charger)
        self.battery -= (TRAVEL_DRAIN_SPEED * self.dist_from_charger)
        self.battery_spent_on_travel += (TRAVEL_DRAIN_SPEED * self.dist_from_charger)

    def dig(self) :
        print("Rover {} digging...".format(self.id))
        if self.battery <= (0.5 * (self.dist_from_charger/TRAVEL_SPEED)) :
            self.travel()
            self.charge()
        time.sleep(1 * TIME_FACTOR)
        self.amount_dug += (DIG_SPEED)
        self.battery -= 0.5
        self.battery_spent_on_digging += 0.5

    @property
    def get_battery(self) :
        return self.battery
    
    @property
    def get_traveled(self) :
        return self.traveled
    
    @property
    def get_id(self) :
        return self.id
    
    @property
    def get_dig_amount(self) :
        return self.amount_dug

def thread_task(_r, _time) :
    while True :
        global elapsed
        if elapsed >= _time :
            return
        _r.dig()

def timekeeper(_time) :
    global elapsed
    for _ in range(_time) :
        elapsed += 1
        time.sleep(1 * TIME_FACTOR)

def simulate(_num_rovers, _time) :
    rovers = []
    threads = []
    for i in range(_num_rovers) :
        temp = Rover("R"+str(i), random.randint(20, 500))
        print(temp.dist_from_charger)
        rovers.append(Rover("R"+str(i), random.randint(20, 500)))
    for r in rovers :
        threads.append(threading.Thread(target=thread_task, args=[r, _time], daemon=True))
    t_T = threading.Thread(target=timekeeper, args=[_time])
    t_T.start()
    for t in threads :
        t.start()
    t_T.join()
    for t in threads :
        t.join()
    print("Time elapsed: {}".format(elapsed))
    for r in rovers :
        r.print_report()
    total_dug = 0
    for r in rovers :
        total_dug += r.get_dig_amount
    print("Total dug amount from all rovers: {}".format(total_dug))

args = [int(x[4:]) for x in sys.argv[1:]]
station = Charger(args[0])
simulate(_num_rovers=args[1], _time=args[2])