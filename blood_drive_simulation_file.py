# importing relative packages for simulation

import simpy
import random
import statistics
import argparse
import sys
from numpy.random import default_rng

# Establishing the wait_time dictionary to store the donors progression through the Blood Drive Center
wait_times = []


# creation of the BloodDriveCenter class with establishing variables for the simulation
class BloodDriveCenter(object):
    def __init__(self, env, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                 medical_screen_time_mean, medical_screen_time_sd,
                 blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean):
        """
        Parameters
        ----------
        env
        num_front_desk
        num_medical_nurse
        num_blood_nurse
        num_obs_greeters
        medical_screen_time_mean
        medical_screen_time_sd
        blood_drawn_time_mean
        blood_drawn_time_sd
        obs_time_mean
        """

        self.env = env
        self.front_desk = simpy.Resource(env, num_front_desk)
        self.medical_nurse = simpy.Resource(env, num_medical_nurse)
        self.blood_nurse = simpy.Resource(env, num_blood_nurse)
        self.obs_greeters = simpy.Resource(env, num_obs_greeters)

        self.medical_screen_time_mean = medical_screen_time_mean
        self.medical_screen_time_sd = medical_screen_time_sd
        self.blood_drawn_time_mean = blood_drawn_time_mean
        self.blood_drawn_time_sd = blood_drawn_time_sd
        self.obs_time_mean = obs_time_mean

    def complete_registration(self, donor):
        # Generates a random number between 5 and 8 minutes to simulate how long it might take for a donor to fill in
        # a registration form/questionare
        yield self.env.timeout(random.randint(5, 8))

    def medical_screening(self, donor):
        # Same thing here, generates a random number between 5 and 10 minutes to clear medical screening before drawing
        # blood
        yield self.env.timeout(random.randint(5, 10))

    def drawing_blood(self, donor):
        # This states that the drawing of the blood would be a total of 15 minutes which is a standard amount of time
        # it takes to draw/fill blood
        yield self.env.timeout(15)

    def wait_time_post_blood(self, donor):
        # Generates a random number for donors to wait after getting there blood drawn and receive refreshments/snacks
        yield self.env.timeout(random.randint(1, 6))


# This function is created and used to simulating arriving at the donation center and requesting the stages of
# drawing your blood
def arrive_blood_drive(env, donor, center):
    arrival_ts = env.now

    # Goes through the process of requesting a front desk worker for paperwork amd waits if any are unavailable
    with center.front_desk.request() as request:
        yield request
        yield env.process(center.complete_registration(donor))

    # Requests Medical Nurse for Medical screening station
    with center.medical_nurse.request() as request:
        yield request
        yield env.process(center.medical_screening(donor))

    # Requests Blood nurse to draw blood station
    with center.blood_nurse.request() as request:
        yield request
        yield env.process(center.drawing_blood(donor))

    # Requests observer to pay attention to any donors feeling light-headed
    with center.obs_greeters.request() as request:
        yield request
        yield env.process(center.wait_time_post_blood(donor))

    # appends the time from which you arrived to after completing the stages, and into the wait_time dictionary
    wait_times.append(env.now - arrival_ts)


# This function creates and runs the blood center, with the passing of the inputs and variables
def run_blood_center(env, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                     medical_screen_time_mean, medical_screen_time_sd,
                     blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean):
    center = BloodDriveCenter(env, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                              medical_screen_time_mean, medical_screen_time_sd,
                              blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean)

    for donor in range(5):
        env.process(arrive_blood_drive(env, donor, center))

    # waiting 2 minutes before a new donor enters
    while True:
        yield env.timeout(2)

        donor += 1
        env.process(arrive_blood_drive(env, donor, center))


# calculates the time a donor spends going through the different stages to donate blood
def collect_average_wait_ts(wait_times_usage):
    average_wait = statistics.mean(wait_times_usage)
    minutes, f_minutes = divmod(average_wait, 1)
    seconds = f_minutes * 60
    hours = minutes // 60
    time_minutes = minutes % 60
    # returns hour, minutes, and seconds breakdown
    return round(hours), round(time_minutes), round(seconds)


# calls for user inputs that affect the output
def get_inputs():
    num_front_desk = input("How many front desk attendances will be working?: ")
    num_medical_nurse = input("How many Medical Nurses will conduct the screening and mini physical process?: ")
    num_blood_nurse = input("How many Blood Nurses will be drawing blood from each donor?: ")
    num_obs_greeters = input("How many Post obs workers will be working?: ")
    params = [num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters]
    if all(str(i).isdigit() for i in params):
        params = [int(x) for x in params]
    else:
        print("Error! Must enter numbers greater than 0 and no text!", "\nSetting default values as...",
              "\n 1 front desk worker, 1 medical nurse, 1 blood nurse, 1 post obs worker.")
        params = [1, 1, 1, 1]
    return params


# function to run and execute on the command line
def main():
    random.seed(55)
    num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters = get_inputs()

    env = simpy.Environment()
    env.process(run_blood_center(env, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                                 medical_screen_time_mean=10, medical_screen_time_sd=0.5,
                                 blood_drawn_time_mean=10, blood_drawn_time_sd=0.5, obs_time_mean=5))
    env.run(until=360)

    hours, minutes, seconds = collect_average_wait_ts(wait_times)
    # output
    print("Processing Simulation, please hold...",
          f"\nThe average wait time is {hours} hour(s) {minutes} minutes and {seconds} seconds.")


if __name__ == '__main__':
    main()
