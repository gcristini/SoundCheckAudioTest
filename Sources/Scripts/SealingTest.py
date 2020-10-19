
import os
import subprocess
import colorama as cm
from scipy.io import wavfile
import numpy as np  

from Libraries.ParseXml import XmlDictConfig
from xml.etree import ElementTree
from Libraries.Enums import Enums as en

from soundcheck_tcpip.soundcheck.installation import construct_installation
from Soundcheck.util import configure_ini_for_automation, get_sc_root, construct_controller, get_standard_sequence_dir, is_calibration_curve
import socket


class SealingTest(object):
    """ """

    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self, soundcheck_struct: dict, storage_folder = ""):
        """ Constructor """
        self._main_storage_folder=storage_folder
        self._sealing_storage_folder = ""
        self._wave_file_name = {
            "Muted": "",
            "Unmuted": ""
        }
        self._soundcheck_struct = soundcheck_struct
        
        self._sealing_config_dict: dict

        # State Machine
        self._sealing_test_state_fun_dict = {
            en.SealingTestEnum.ST_TEST_STATE_INIT: self._init_state_manager,
            en.SealingTestEnum.ST_TEST_STATE_RUN_UMT: self._run_test_unmuted_state_manager,    
            en.SealingTestEnum.ST_TEST_STATE_RUN_MT: self._run_test_muted_state_manager,
            en.SealingTestEnum.ST_TEST_STATE_ANALYZE: self._analyze_state_manager,
            en.SealingTestEnum.ST_TEST_STATE_STOP: self._stop_state_manager
        }

        self._sealing_test_state: None
        self._last_sealing_test_state: None

    # ---------------------------------------------------------------- #
    # ----------------------- Private Methods ------------------------ #
    # ---------------------------------------------------------------- #
    @staticmethod
    def _print_help():
        """"""
        pass

    def _parse_config_file(self):
        """"""
        self._sealing_config_dict = XmlDictConfig(ElementTree.parse('Config.xml').getroot())
        
        return

    # ------------------ STATE MACHINE ------------------ #
    def _go_to_next_state(self, state):
        """"""
        # Store last state
        self._store_last_state()

        # Go to next state
        self._sealing_test_state = state
        return

    def _store_last_state(self):
        """"""
        self._last_sealing_test_state = self._sealing_test_state
        return

    def _init_state_manager(self):
        """"""        
        # Create storage folder for Sealing Test
        self._sealing_storage_folder = f"{self._main_storage_folder}/SealingTest"
        os.mkdir(self._sealing_storage_folder)

        self._wave_file_name["Muted"] = f'[Muted] {self._sealing_config_dict["General"]["device_name"]}_ST.wav'
        self._wave_file_name["Unmuted"] = f'[Unmuted] {self._sealing_config_dict["General"]["device_name"]}_ST.wav'

        # Open sequence                
        self._soundcheck_struct['construct_controller'].open_sequence(f'{self._soundcheck_struct["root_directory"]}\\Sequences\\Microphones\\SealingTest_WhiteNoise.sqc', timeout=60)

        # Delete all files into "EasyVoiceRecorder" storage folder in sx5
        subprocess.run("adb shell rm -f /storage/emulated/0/EasyVoiceRecorder/*", text=True, stdout=False)

        # Go to Run Unmuted Test state
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_RUN_UMT)
        return

    def _run_test_unmuted_state_manager(self):
        """"""
        print (cm.Fore.CYAN + cm.Style.DIM + "- Record with unmuted microphone", end = '\r')

        # Run sequence
        self._soundcheck_struct['construct_controller'].run_sequence()
        
        # Get the recorded wav file and pull it 
        input_wav_filename=subprocess.run("adb shell ls /storage/emulated/0/EasyVoiceRecorder/", text=True, capture_output=True).stdout.strip('\n\r')            
        output_wav_filename = self._wave_file_name["Unmuted"]
        subprocess.run(f'adb pull "/storage/emulated/0/EasyVoiceRecorder/{input_wav_filename}" "{self._sealing_storage_folder}/{output_wav_filename}"', text=True, stdout=False)
        subprocess.run("adb shell rm -f /storage/emulated/0/EasyVoiceRecorder/*", text=True,  stdout=False) 

        print (cm.Fore.CYAN + cm.Style.DIM + "- Record with unmuted microphone\t\t" + cm.Fore.GREEN + cm.Style.DIM + "OK")

        # Go to run muted test state
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_RUN_MT)
        return
   
    def _run_test_muted_state_manager(self):
        """"""
        print (cm.Fore.CYAN + cm.Style.DIM + "- Record with muted microphone", end = '\r')

        # Run sequence
        self._soundcheck_struct['construct_controller'].run_sequence()

        # Get the recorded wav file and pull it       
        input_wav_filename=subprocess.run("adb shell ls /storage/emulated/0/EasyVoiceRecorder/", text=True, capture_output=True).stdout.strip('\n\r')                  
        output_wav_filename=self._wave_file_name["Muted"]
        subprocess.run(f'adb pull "/storage/emulated/0/EasyVoiceRecorder/{input_wav_filename}" "{self._sealing_storage_folder}/{output_wav_filename}"', text=True,  stdout=False)
        subprocess.run("adb shell rm -f /storage/emulated/0/EasyVoiceRecorder/*", text=True,  stdout=False)
        
        print (cm.Fore.CYAN + cm.Style.DIM + "- Record with muted microphone\t\t" + cm.Fore.GREEN + cm.Style.DIM + "OK")

        # Go to run analyze state
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_ANALYZE)
        return

    def _analyze_state_manager(self):
        """"""
        print (cm.Fore.CYAN + cm.Style.DIM + "- Calulate track's RMS and sealing:")        
        bit_depth = (2**15) # Track audio are 16-bit signed, so the max value is (2**16)/2

        # Calculate RMS of unmuted track
        data = wavfile.read(f'{self._sealing_storage_folder}/{self._wave_file_name["Unmuted"]}')[1]
        unmuted_RMS_dbFS = np.round(10*np.log10(np.mean((data/bit_depth)**2)),2)        

        # Calculate RMS of Muted track
        data = wavfile.read(f'{self._sealing_storage_folder}/{self._wave_file_name["Muted"]}')[1]
        muted_RMS_dbFS = np.round(10*np.log10(np.mean((data/bit_depth)**2)),2)
        
        # Calculate sealing
        sealing_RMS_dbFS = np.round(abs(unmuted_RMS_dbFS) - abs(muted_RMS_dbFS),2)
        
        # Print and save log
        log_text =  f'\t{self._wave_file_name["Unmuted"]}: {unmuted_RMS_dbFS} dbFS\n' +\
                    f'\t{self._wave_file_name["Muted"]}: {muted_RMS_dbFS} dbFS\n' +\
                    f'\tSealing: {sealing_RMS_dbFS} dbFS'

        print (cm.Fore.CYAN + cm.Style.DIM + log_text)
        
        file = open(f"{self._sealing_storage_folder}/SealingTest.log", "w")
        file.write(log_text)
        file.close()

        # Go to stop state
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_STOP)
        return

    def _stop_state_manager(self):
        """"""        
        self._store_last_state()
        return
    
    def _sealing_state_machine_manager(self):
        """"""
        # Get function from dictionary
        fun = self._sealing_test_state_fun_dict.get(self._sealing_test_state)
        
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
        self._sealing_test_state = en.MainStateEnum.MAIN_STATE_INIT
        self._last_main_state = en.MainStateEnum.MAIN_STATE_INIT

        return

    def run(self):
        """ Sealing Test Application """
        print (cm.Fore.CYAN + cm.Style.DIM + "\n**** RUN SEALING TEST ****")

        # Init
        self._init_state_manager()

        while not (self._sealing_test_state == en.SealingTestEnum.ST_TEST_STATE_STOP and
                   self._last_sealing_test_state == en.SealingTestEnum.ST_TEST_STATE_STOP):

            # Store the last state machine state
            self._store_last_state()

            # Run state machine at current state
            self._sealing_state_machine_manager()

        return
