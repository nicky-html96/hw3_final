# import sys
# import argparse
# from datetime import datetime
# import math
#
# import pandas as pd
# from numpy.random import default_rng
# import simpy
# from pathlib import Path
#
#
# class BloodDriveDonate(object):
#     def __init__(self, env, num_screening_nurse, num_of_donors, num_blood_nurse, num_post_obs_staff,
#                  mean_interarrival_time, reg_time_mean, medical_screen_time_mean, medical_screen_time_sd,
#                  blood_drawn_time_mean, blood_drawn_time_sd,
#                  obs_time, post_obs_time_mean, rg
#                  ):
#         """
#         Primary class that encapsulates Blood Drive workers and donation flow logic.
#
#         The detailed patient flow logic is now in get_vaccinated() method of this class. Also,
#         the run_clinic() function is now a run() method in this class. The only patient information
#         that gets passed in to any class methods is the patient id (int).
#
#         Parameters
#         ----------
#         env
#         num_screening_nurse
#         num_of_donors
#         num_blood_nurse
#         num_post_obs_staff
#         mean_interarrival_time
#         reg_time_mean
#         medical_screen_time_mean
#         medical_screen_time_sd
#         blood_drawn_time_mean
#         blood_drawn_time_sd
#         obs_time
#         post_obs_time_mean
#         rg
#         """
#
#         # Simulation environment and random number generator
#         self.env = env
#         self.rg = rg
#
#         # Create list to hold timestamps dictionaries (one per patient)
#         self.timestamps_list = []
#         # Create lists to hold occupancy tuples (time, occ)
#         self.postdonate_occupancy_list = [(0.0, 0.0)]
#         self.donate_occupancy_list = [(0.0, 0.0)]
#
#         # Create SimPy resources
#         self.screening_nurse = simpy.Resource(env, num_screening_nurse)
#         self.donors = simpy.Resource(env, num_of_donors)
#         self.blood_nurse = simpy.Resource(env, num_blood_nurse)
#         self.post_obs_staff = simpy.Resource(env, num_post_obs_staff)
#
#         # Initialize the patient flow related attributes
#         self.mean_interarrival_time = mean_interarrival_time
#
#         self.medical_screen_time_mean = medical_screen_time_mean
#         self.medical_screen_time_sd = medical_screen_time_sd
#         self.reg_time_mean = reg_time_mean
#         self.blood_drawn_time_mean = blood_drawn_time_mean
#         self.blood_drawn_time_sd = blood_drawn_time_sd
#         self.obs_time = obs_time
#         self.post_obs_time_mean = post_obs_time_mean
#
#     def registration(self):
#         yield self.env.timeout(self.rg.exponential(self.reg_time_mean))
#
#     def medical_screening(self):
#         yield self.env.timeout(self.rg.normal(self.medical_screen_time_mean, self.medical_screen_time_sd))
#
#     def blood_donation(self):
#         yield self.env.timeout(self.rg.normal(self.blood_drawn_time_mean, self.blood_drawn_time_sd))
#
#     def wait_time_post_blood(self):
#         yield self.env.timeout(self.rg.exponential(self.post_obs_time_mean))
#
#     def draw_blood(self, donor, quiet):
#         arrival_ts = self.env.now
#
#         # Request paperwork for questionare to complete registration
#         with self.register.request() as request:
#             yield request
#             got_register_ts = self.env.now
#             yield self.env.proccess(self.registration())
#             release_register_ts = self.env.now
#
#         with self.screening_nurse.request() as request:
#             if not quiet:
#                 print(f"Donor {donor} requested for medical screening at time {self.env.now}")
#             yield request
#             got_screening_ts = self.env.now
#             q_time = got_screening_ts - release_register_ts
#             if not quiet:
#                 print(f"Donor {donor} requested for medical screening at time {self.env.now}")
#             # Updates medical screening -increment by 1
#
#
#
#
#
#
# def compute_durations(timestamp_df):
#     """Compute time durations of interest from timestamps dataframe and append new cols to dataframe"""
#
#     timestamp_df['time_in_center'] = timestamp_df.loc[:, 'exit_system_ts'] - timestamp_df[:, 'arrival_ts']


import simpy
import random
import statistics
import argparse
import sys
from numpy.random import default_rng

wait_times = []


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
        # self.rg = rg
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
        yield self.env.timeout(random.randint(5, 8))

    def medical_screening(self):
        yield self.env.timeout(self.rg.normal(self.medical_screen_time_mean, self.medical_screen_time_sd))

    def drawing_blood(self):
        yield self.env.timeout(self.rg.normal(self.blood_drawn_time_mean, self.blood_drawn_time_sd))

    def wait_time_post_blood(self):
        yield self.env.timeout(self.rg.exponential(self.obs_time_mean))


def arrive_blood_drive(self, center):
    arrival_ts = self.now

    with center.front_desk.request() as request:
        yield request
        yield self.env.process(self.complete_registration)

    with center.medical_nurse.request() as request:
        yield request
        yield self.env.process(self.medical_screening)

    with center.blood_nurse.request() as request:
        yield request
        yield self.env.process(self.drawing_blood)

    with center.obs_greeters.request() as request:
        yield request
        yield self.env.process(self.wait_time_post_blood)

    wait_times.append(self.env.now - arrival_ts)


# def simulate(arg_dict, rep_num):
#     seed = arg_dict['seed'] + rep_num - 1
#     rg = default_rng(seed=seed)


def run_blood_center(self, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                     medical_screen_time_mean, medical_screen_time_sd,
                     blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean):
    center = BloodDriveCenter(self, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                              medical_screen_time_mean, medical_screen_time_sd,
                              blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean)

    for donor in range(5):
        self.process(arrive_blood_drive(self, center))

    while True:
        yield self.timeout(2)

    donor += 1
    env.process(arrive_blood_drive(self, center))


def collect_average_wait_ts(wait_times_usage):
    average_wait = statistics.mean(wait_times_usage)
    mins, frac_mins = divmod(average_wait, 1)
    seconds = frac_mins * 60
    return round(mins), round(seconds)


def get_inputs():
    num_front_desk = input("How many front desk attendances will be working? (Note: minimum of 2 or more): ")
    num_medical_nurse = input("How many Medical Nurses will conduct the screening and mini physical process?: ")
    num_blood_nurse = input("How many Blood Nurses will be drawing blood from each donor?: ")
    num_obs_greeters = input("How many Post obs workers will be working? (Note: minimum of 2 or more): ")
    params = [num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters]
    if all(str(i).isdigit() for i in params):
        params = [int(x) for x in params]
    else:
        print("Error! Must enter numbers greater than 0 and no text!", "\nSetting default values as...",
              "\n 1 front desk worker, 1 medical nurse, 1 blood nurse, 1 post obs worker.")
        params = [1, 1, 1, 1]
    return params


# def process_command_line():
#     parser = argparse.ArgumentParser(prog='blood_drive_simulation',
#                                      description='Executing blood drive center simulation')
#
#     # Add arguments
#     parser.add_argument(
#         "--config", type=str, default=None,
#         help="Configuration file containing input parameter arguments and values"
#     )
#
#     parser.add_argument("--medical_screen_time_mean", default=10,
#                         help="Mean time to complete medical screening (mins)")
#
#     parser.add_argument("--medical_screen_time_sd", default=0.5,
#                         help="Standard Deviation time to complete medical screening (mins)")
#
#     parser.add_argument("--blood_drawn_time_mean", default=15,
#                         help="Mean time to complete the drawing of the blood (mins)")
#
#     parser.add_argument("--blood_drawn_time_sd", default=0.5,
#                         help="Standard Deviation time to complete the drawing of the blood (mins)")
#
#     parser.add_argument("--obs_time_mean", default=0.5,
#                         help="Time (minutes) each donor waits post-drawn blood to receive refreshment after blood loss.")
#
#     args = parser.parse_args()
#
#     if args.config is not None:
#         with open(args.config, "r") as fin:
#             args = parser.parse_args(fin.read().split())
#
#     return args


# def simulation(arg_dict, rep_num):
#     # Create a random number generator for this replication
#     seed = arg_dict['seed'] + rep_num - 1
#     rg = default_rng(seed=seed)
#
#     num_front_desk = arg_dict['num_front_desk']
#     num_medical_nurse = arg_dict['num_medical_nurse']
#     num_blood_nurse = arg_dict['num_blood_nurse']
#     num_obs_greeters = arg_dict['num_obs_greeters']
#
#     medical_screen_time_mean = arg_dict['medical_screen_time_mean']
#     medical_screen_time_sd = arg_dict['medical_screen_time_sd']
#     blood_drawn_time_mean = arg_dict['blood_drawn_time_mean']
#     blood_drawn_time_sd = arg_dict['blood_drawn_time_sd']
#     obs_time_mean = arg_dict['obs_time_mean']
#
#     env = simpy.Environment()
#
#     center = BloodDriveCenter(env, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
#                               medical_screen_time_mean, medical_screen_time_sd,
#                               blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean)
#
#     blood_center = run_blood_center(num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
#                                     medical_screen_time_mean, medical_screen_time_sd,
#                                     blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean
#                                     )
#
#     env.process(
#         blood_center.run())


def main():
    # args = process_command_line()
    # print(args)
    #
    # rg = default_rng()

    random.seed(55)
    num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters = get_inputs()
    env = simpy.Environment()
    env.process(run_blood_center(self, num_front_desk=num_front_desk, num_medical_nurse=num_medical_nurse,
                                 num_blood_nurse=num_blood_nurse, num_obs_greeters=num_obs_greeters,
                                 medical_screen_time_mean=8, medical_screen_time_sd=8,
                                 blood_drawn_time_mean=8, blood_drawn_time_sd=8, obs_time_mean=8))
    # setting simulation to 360 mins or 6 hours, will try to have that in config file
    env.run(until=360)
    minutes, seconds = collect_average_wait_ts(wait_times)
    print("Processing Simulation, please hold...",
          f"\nThe average wait time is {minutes} minutes and {seconds} seconds.")


if __name__ == '__main__':
    main()
