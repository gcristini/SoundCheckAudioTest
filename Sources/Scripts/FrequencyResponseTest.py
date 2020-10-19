import os
import subprocess
import matplotlib.pyplot as plt
import colorama as cm

from Libraries.ParseXml import XmlDictConfig
from xml.etree import ElementTree
from Libraries.Enums import Enums as en

from soundcheck_tcpip.soundcheck.installation import construct_installation
from Soundcheck.util import configure_ini_for_automation, get_sc_root, construct_controller, get_standard_sequence_dir, is_calibration_curve
import socket


class FrequencyResponseTest(object):
    """ """

    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self, soundcheck_struct: dict, storage_folder=""):
        """ Constructor """
        self._main_storage_folder = storage_folder
        self._frequency_response_storage_folder: str
        self._wave_file_name: str

        self._soundcheck_struct = soundcheck_struct

        self._frequency_reponse_config_dict: dict

        # State Machine
        self._frequency_response_test_state_fun_dict = {
            en.FrequencyResponseTestEnum.FR_TEST_STATE_INIT: self._init_state_manager,
            en.FrequencyResponseTestEnum.FR_TEST_STATE_RUN_SEQ: self._run_sequence_state_manager,
            en.FrequencyResponseTestEnum.FR_TEST_STATE_ANALYZE_DATA: self._analyze_data_state_manager,
            en.FrequencyResponseTestEnum.FR_TEST_STATE_STOP: self._stop_state_manager,
            en.FrequencyResponseTestEnum.FR_TEST_STATE_EXIT: self._exit_state_manager,
        }

        self._frequency_response_test_state = None
        self._last_frequency_response_test_state = None

        return

    # ---------------------------------------------------------------- #
    # ----------------------- Private Methods ------------------------ #
    # ---------------------------------------------------------------- #
    @staticmethod
    def _print_help():
        """"""
        pass

    def _parse_config_file(self):
        """"""
        self._frequency_response_config_dict = XmlDictConfig(ElementTree.parse('Config.xml').getroot())
        
        return

    # ------------------ STATE MACHINE ------------------ #
    def _go_to_next_state(self, state):
        """"""
        # Store last state
        self._store_last_state()

        # Go to next state
        self._frequency_response_test_state = state
        return

    def _store_last_state(self):
        """"""
        self._last_frequency_response_test_state = self._frequency_response_test_state
        return

    def _init_state_manager(self):
        """"""
        # Create storage folder for frequency response Test
        self._frequency_response_storage_folder = f"{self._main_storage_folder}/FrequencyResponseTest"
        os.mkdir(self._frequency_response_storage_folder)

        self._wave_file_name = f'{self._frequency_response_config_dict["General"]["device_name"]}_FRT.wav'

        # Delete all files into "EasyVoiceRecorder" storage folder in SX5
        subprocess.run("adb shell rm -f /storage/emulated/0/EasyVoiceRecorder/*", text=True, stdout=False)

        # Go to run test state
        self._go_to_next_state(en.FrequencyResponseTestEnum.FR_TEST_STATE_RUN_SEQ)

        return

    def _run_sequence_state_manager(self):
        """"""                
        # Open and run the first step of sequence
        self._soundcheck_struct['construct_controller'].open_sequence(f'{self._soundcheck_struct["root_directory"]}\\Sequences\\Microphones\\FrequencyResponse_150-10k_Step1.sqc', timeout=60)
        self._soundcheck_struct['construct_controller'].wait_on_ready(timeout=60)
        self._soundcheck_struct['construct_controller'].run_sequence()

        # Get the recorded wav file and pull it       
        input_wav_filename=subprocess.run("adb shell ls /storage/emulated/0/EasyVoiceRecorder/", text=True, capture_output=True).stdout.strip('\n\r')                  
        output_wav_filename=self._wave_file_name
        subprocess.run(f'adb pull "/storage/emulated/0/EasyVoiceRecorder/{input_wav_filename}" "{self._frequency_response_storage_folder}/{output_wav_filename}"', text=True,  stdout=False)
        subprocess.run("adb shell rm -f /storage/emulated/0/EasyVoiceRecorder/*", text=True,  stdout=False)
        print (cm.Fore.GREEN + cm.Style.DIM + f'-- Record saved in {self._frequency_response_storage_folder}/{output_wav_filename}')
        
        # Open and run the second step of sequence        
        self._soundcheck_struct['construct_controller'].open_sequence(f'{self._soundcheck_struct["root_directory"]}\\Sequences\\Microphones\\FrequencyResponse_150-10k_Step2.sqc', timeout=60)
        self._soundcheck_struct['construct_controller'].wait_on_ready(timeout=60)
        self._soundcheck_struct['construct_controller'].run_sequence()
        
        # Go to stop state
        self._go_to_next_state(en.FrequencyResponseTestEnum.FR_TEST_STATE_ANALYZE_DATA)

        return
    
    def _analyze_data_state_manager(self):
        """"""
        
        data = {
            'fundamental': self._soundcheck_struct['construct_controller'].get_curve("Fundamental"),
            'upper_limit': self._soundcheck_struct['construct_controller'].get_curve("Microphone Response Upper Limit"),
            'lower_limit': self._soundcheck_struct['construct_controller'].get_curve("Microphone Response Lower Limit") 
        }        

        fig = plt.figure()
        ax=fig.add_subplot(1,1,1)

        ax.plot(data['fundamental']["XData"],data['fundamental']["YData"], color='tab:blue')
        ax.plot(data['upper_limit']["XData"],data['upper_limit']["YData"], color='tab:red')        
        ax.plot(data['lower_limit']["XData"],data['lower_limit']["YData"], color='tab:red')        

        ax.grid()
        #fig.title("Fundamental")

        # Set limits based on data max/min, looks better than autoscale
        ax.set_xlim(min(data['fundamental']["XData"]), max(data['fundamental']["XData"])+1000)
        ax.set_ylim(min(data['fundamental']["YData"])-20, max(data['fundamental']["YData"])+20)

        # Set axis labels
        ax.set_ylabel(data['fundamental']["YDataScale"])
        ax.set_xlabel(data['fundamental']["XUnit"])

        # set scale format
        ax.set_yscale('Linear')
        ax.set_xscale('Log')
        #plt.show(block=False)
        plt.savefig(f'{self._frequency_response_storage_folder}/FrequencyReponse.jpg')

        # Go to stop state
        self._go_to_next_state(en.FrequencyResponseTestEnum.FR_TEST_STATE_STOP)

        return

    def _stop_state_manager(self):
        """"""        
        # Store the last state
        self._store_last_state()
        
        return

    def _exit_state_manager(self):
        """"""

        return

    def _frequency_response_state_machine_manager(self):
        """"""
        # Get function from dictionary
        fun = self._frequency_response_test_state_fun_dict.get(self._frequency_response_test_state)

        # Execute function
        fun()

        return

    # ************************************************ #
    # **************** Public Methods **************** #
    # ************************************************ #
    def init(self):
        """"""
        # Initialize Colorama library
        cm.init(autoreset=True)

        # Parse configuration file
        self._parse_config_file()

        # Initialize state machine state variables
        self._frequency_response_test_state = en.FrequencyResponseTestEnum.FR_TEST_STATE_INIT
        self._last_frequency_response_test_state = en.FrequencyResponseTestEnum.FR_TEST_STATE_INIT

        return

    def run(self):
        """ Frequency Response Test Application """
        print (cm.Fore.GREEN + cm.Style.DIM + "\n**** RUN FREQUENCY RESPONSE TEST ****")

        # Init
        self._init_state_manager()

        while not (self._frequency_response_test_state == en.FrequencyResponseTestEnum.FR_TEST_STATE_STOP and
                   self._last_frequency_response_test_state == en.FrequencyResponseTestEnum.FR_TEST_STATE_STOP):

            # Store the last state machine state
            self._store_last_state()

            # Run state machine at current state
            self._frequency_response_state_machine_manager()
        
        return
