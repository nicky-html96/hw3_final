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

    def medical_screening(self, donor):
        yield self.env.timeout(random.randint(5, 10))

    def drawing_blood(self, donor):
        yield self.env.timeout(15)

    def wait_time_post_blood(self, donor):
        yield self.env.timeout(random.randint(1, 6))


def arrive_blood_drive(env, donor, center):
    arrival_ts = env.now

    with center.front_desk.request() as request:
        yield request
        yield env.process(center.complete_registration(donor))

    with center.medical_nurse.request() as request:
        yield request
        yield env.process(center.medical_screening(donor))

    with center.blood_nurse.request() as request:
        yield request
        yield env.process(center.drawing_blood(donor))

    with center.obs_greeters.request() as request:
        yield request
        yield env.process(center.wait_time_post_blood(donor))

    wait_times.append(env.now - arrival_ts)


# def simulate(arg_dict, rep_num):
#     seed = arg_dict['seed'] + rep_num - 1
#     rg = default_rng(seed=seed)


def run_blood_center(env, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                     medical_screen_time_mean, medical_screen_time_sd,
                     blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean):
    center = BloodDriveCenter(env, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                              medical_screen_time_mean, medical_screen_time_sd,
                              blood_drawn_time_mean, blood_drawn_time_sd, obs_time_mean)

    for donor in range(5):
        env.process(arrive_blood_drive(env, donor, center))

    while True:
        yield env.timeout(2)

        donor += 1
        env.process(arrive_blood_drive(env, donor, center))


def collect_average_wait_ts(wait_times_usage):
    average_wait = statistics.mean(wait_times_usage)
    mins, frac_mins = divmod(average_wait, 1)
    seconds = frac_mins * 60
    hours = mins//60
    min = mins%60
    return round(hours), round(min), round(seconds)


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
#

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
#
#     env.run(until=360)
#

def main():
    random.seed(55)
    num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters = get_inputs()

    env = simpy.Environment()
    env.process(run_blood_center(env, num_front_desk, num_medical_nurse, num_blood_nurse, num_obs_greeters,
                                 medical_screen_time_mean=10, medical_screen_time_sd=0.5,
                                 blood_drawn_time_mean=10, blood_drawn_time_sd=0.5, obs_time_mean=5))
    env.run(until=360)

    hours, minutes, seconds = collect_average_wait_ts(wait_times)
    print("Processing Simulation, please hold...",
          f"\nThe average wait time is {hours} hour(s) {minutes} minutes and {seconds} seconds.")


if __name__ == '__main__':
    main()
