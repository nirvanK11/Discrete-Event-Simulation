import simpy
import random
import pandas as pd

# Global parameters class
class g:
    inter_arrival_time = 10
    Time_with_recp = 5
    number_of_recp = 2
    number_Of_nurse = 2
    mean_time_with_nurse = 10
    sim_duration = 120
    run_number = 20
    mean_time_with_GP = 20
    number_of_GP = 2
    pro_seeing_GP = 0.6

# Entity class for the patient
class Patient:
    def __init__(self, Patient_id):
        self.id = Patient_id
        self.q_time = 0
        self.q_nurse_time = 0
        self.q_time_GP = 0

# Model class
class Model:
    def __init__(self, run_numbers):
        self.env = simpy.Environment()
        self.Patient_counter = 0 
        self.recipient_support = simpy.Resource(self.env, capacity=g.number_of_recp)
        self.nurse_support = simpy.Resource(self.env,capacity=g.number_Of_nurse)
        self.GP_support = simpy.Resource(self.env,capacity=g.number_of_GP)
        self.run_numbers = run_numbers
        self.df_result = pd.DataFrame()
        self.df_result['Patient ID'] = [1]
        self.df_result['Wait Time in Queue with recep'] = [0.0]
        self.df_result['Time Spent with Recipient'] = [0.0]
        self.df_result['wait Time in Queue for Nurse'] = [0.0]
        self.df_result['Time Spent with Nurse'] = [0.0]
        self.df_result['Wait Time in Queue for GP'] = [0.0]
        self.df_result['Time Spent with GP'] = [0.0]
        self.df_result.set_index('Patient ID', inplace=True)

        self.mean_q_time = 0 
        self.mean_q_time_nurse = 0
        self.mean_q_time_GP = 0

    def create_patient_arrival(self):
        while True:
            self.Patient_counter += 1
            p = Patient(self.Patient_counter)
            self.env.process(self.Recipient_support(p))
            t = random.expovariate(1.0/g.inter_arrival_time)
            yield self.env.timeout(t)

    def Recipient_support(self, patient):
        start_q_patient = self.env.now

        with self.recipient_support.request() as req:
            yield req

            end_q_patient = self.env.now 

            patient.q_time = end_q_patient - start_q_patient

            sampled_customer_support_time = random.expovariate(1.0/g.Time_with_recp)

            # Add data to the DataFrame
            self.df_result.at[patient.id, 'Wait Time in Queue with recep'] = patient.q_time
            self.df_result.at[patient.id, 'Time Spent with Recipient'] = sampled_customer_support_time

            yield self.env.timeout(sampled_customer_support_time)



        start_q_patient_nurse = self.env.now

        with self.nurse_support.request() as req:
            
            yield req

            end_q_patient_nurse = self.env.now 

            patient.q_nurse_time = end_q_patient_nurse - start_q_patient_nurse


            sampled_customer_support_time_nurse = random.expovariate(1.0/g.mean_time_with_nurse)

            self.df_result.at[patient.id,'wait Time in Queue for Nurse'] = patient.q_nurse_time
            self.df_result.at[patient.id,'Time Spent with Nurse'] = sampled_customer_support_time_nurse

            yield self.env.timeout(sampled_customer_support_time_nurse)

        
        start_q_GP = self.env.now

        with self.GP_support.request() as req:

          yield req

          end_q_GP = self.env.now 

          patient.patient_q_time_GP  = end_q_GP - start_q_GP


          sampled_patient_time_GP = random.expovariate(1.0/g.mean_time_with_GP)

          self.df_result.at[patient.id, 'Wait Time in Queue for GP'] =patient.patient_q_time_GP
          self.df_result.at[patient.id, 'Time Spent with GP'] = sampled_patient_time_GP

          yield self.env.timeout(sampled_patient_time_GP)


    def calculate_run_results(self):
        self.mean_q_time = self.df_result['Wait Time in Queue with recep'].mean()
        self.mean_q_time_nurse = self.df_result['wait Time in Queue for Nurse'].mean()
        self.mean_q_time_GP = self.df_result['Wait Time in Queue for GP'].mean()


    def run(self):
        self.env.process(self.create_patient_arrival())
        self.env.run(until=g.sim_duration)
        self.calculate_run_results()
        print(f"Run Number {self.run_numbers}")
        print(self.df_result)

# Trial class
class Trial:
    def __init__(self):
        self.df_trial_results = pd.DataFrame()
        self.df_trial_results["Run Number"] =[0]
        self.df_trial_results['Mean Queue Time'] = [0.0]
        self.df_trial_results['Mean Queue Time for Nurse'] = [0.0]
        self.df_trial_results['Mean Queue Time for GP'] = [0.0]
        self.df_trial_results.set_index('Run Number', inplace=True)

    def print_trial_results(self):
        print('Trial Results')
        print(self.df_trial_results)

    # Method to run the trial
    def run_trial(self):
        for run in range(g.run_number):
            m = Model(run)
            m.run()
            self.df_trial_results.at[run, 'Mean Queue Time'] = [m.mean_q_time]
            self.df_trial_results.at[run, 'Mean Queue Time for Nurse'] = [m.mean_q_time_nurse]
            self.df_trial_results.at[run, 'Mean Queue Time for GP'] = [m.mean_q_time_GP]
           

        self.print_trial_results()

# Run the trial
my_trial = Trial()
my_trial.run_trial()
