import simpy
import random
import statistics

wait_times = []


class BloodDriveCenter(object):
    def __init__(self, env, num_front_desk, num_medical_nurse, num_blood_nurse, num_post_obs_greeters,
                 medical_screen_time_mean, medical_screen_time_sd,
                 blood_drawn_time_mean, blood_drawn_time_sd, post_obs_time_mean):
        self.env = env
        self.rg = rg
        self.front_desk = simpy.Resource(env, num_front_desk)
        self.medical_nurse = simpy.Resource(env, num_medical_nurse)
        self.blood_nurse = simpy.Resource(env, num_blood_nurse)
        self.post_obs_greeters = simpy.Resource(env, num_post_obs_greeters)

        self.medical_screen_time_mean = medical_screen_time_mean
        self.medical_screen_time_sd = medical_screen_time_sd
        self.blood_drawn_time_mean = blood_drawn_time_mean
        self.blood_drawn_time_sd = blood_drawn_time_sd
        self.post_obs_time_mean = post_obs_time_mean

    def complete_registration(self, donor):
        yield self.env.timeout(random.randint(5, 8))

    def medical_screening(self):
        yield self.env.timeout(self.rg.normal(self.medical_screen_time_mean, self.medical_screen_time_sd))

    def drawing_blood(self):
        yield self.env.timeout(self.rg.normal(self.blood_drawn_time_mean, self.blood_drawn_time_sd))

    def wait_time_post_blood(self):
        yield self.env.timeout(self.rg.exponential(self.post_obs_time_mean))


def arrive_blood_drive(self, donor, center):
    arrival_ts = self.env.now

    with center.front_desk.request() as request:
        yield request
        yield self.env.process(self.complete_registration)

    with center.medical_nurse.request() as request:
        yield request
        yield self.env.process(self.medical_screening)

    with center.blood_nurse.request() as request:
        yield request
        yield self.env.process(self.drawing_blood)

    with center.post_obs_greeters.request() as request:
        yield request
        yield self.env.process(self.wait_time_post_blood)

    wait_times.append(self.env.now - arrival_ts)




