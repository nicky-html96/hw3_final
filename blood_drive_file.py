import sys
import argparse
from datetime import datetime
import math

import pandas as pd
from numpy.random import default_rng
import simpy
from pathlib import Path


class BloodDriveDonate(object):
    def __init__(self, env, num_screening_nurse, num_of_donors, num_blood_nurse, num_post_obs_staff,
                 mean_interarrival_time, reg_time_mean, medical_screen_time_mean, medical_screen_time_sd,
                 blood_drawn_time_mean, blood_drawn_time_sd,
                 obs_time, post_obs_time_mean, rg
                 ):
        """
        Primary class that encapsulates Blood Drive workers and donation flow logic.

        The detailed patient flow logic is now in get_vaccinated() method of this class. Also,
        the run_clinic() function is now a run() method in this class. The only patient information
        that gets passed in to any class methods is the patient id (int).

        Parameters
        ----------
        env
        num_screening_nurse
        num_of_donors
        num_blood_nurse
        num_post_obs_staff
        mean_interarrival_time
        reg_time_mean
        medical_screen_time_mean
        medical_screen_time_sd
        blood_drawn_time_mean
        blood_drawn_time_sd
        obs_time
        post_obs_time_mean
        rg
        """

        # Simulation environment and random number generator
        self.env = env
        self.rg = rg

        # Create list to hold timestamps dictionaries (one per patient)
        self.timestamps_list = []
        # Create lists to hold occupancy tuples (time, occ)
        self.postdonate_occupancy_list = [(0.0, 0.0)]
        self.donate_occupancy_list = [(0.0, 0.0)]

        # Create SimPy resources
        self.screening_nurse = simpy.Resource(env, num_screening_nurse)
        self.donors = simpy.Resource(env, num_of_donors)
        self.blood_nurse = simpy.Resource(env, num_blood_nurse)
        self.post_obs_staff = simpy.Resource(env, num_post_obs_staff)

        # Initialize the patient flow related attributes
        self.mean_interarrival_time = mean_interarrival_time

        self.medical_screen_time_mean = medical_screen_time_mean
        self.medical_screen_time_sd = medical_screen_time_sd
        self.reg_time_mean = reg_time_mean
        self.blood_drawn_time_mean = blood_drawn_time_mean
        self.blood_drawn_time_sd = blood_drawn_time_sd
        self.obs_time = obs_time
        self.post_obs_time_mean = post_obs_time_mean

    def registration(self):
        yield self.env.timeout(self.rg.exponential(self.reg_time_mean))

    def medical_screening(self):
        yield self.env.timeout(self.rg.normal(self.medical_screen_time_mean, self.medical_screen_time_sd))

    def blood_donation(self):
        yield self.env.timeout(self.rg.normal(self.blood_drawn_time_mean, self.blood_drawn_time_sd))

    def wait_time_post_blood(self):
        yield self.env.timeout(self.rg.exponential(self.post_obs_time_mean))

    def draw_blood(self, donor, quiet):
        arrival_ts = self.env.now

        # Request paperwork for questionare to complete registration
        with self.register.request() as request:
            yield request
            got_register_ts = self.env.now
            yield self.env.proccess(self.registration())
            release_register_ts = self.env.now

        with self.screening_nurse.request() as request:
            if not quiet:
                print(f"Donor {donor} requested for medical screening at time {self.env.now}")
            yield request
            got_screening_ts = self.env.now
            q_time = got_screening_ts - release_register_ts
            if not quiet:
                print(f"Donor {donor} requested for medical screening at time {self.env.now}")
            # Updates medical screening -increment by 1






### Stopped at vaccinator request


def compute_durations(timestamp_df):
    """Compute time durations of interest from timestamps dataframe and append new cols to dataframe"""

    timestamp_df['time_in_center'] = timestamp_df.loc[:, 'exit_system_ts'] - timestamp_df[:, 'arrival_ts']
