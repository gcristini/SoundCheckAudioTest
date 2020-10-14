
import os
import subprocess
from Libraries.ParseXml import XmlDictConfig
from xml.etree import ElementTree

from soundcheck_tcpip.soundcheck.installation import construct_installation
from Soundcheck.util import configure_ini_for_automation, get_sc_root, construct_controller, get_standard_sequence_dir, is_calibration_curve
import socket

from Libraries.Enums import Enums as en


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
            #en.SealingTestEnum.ST_TEST_STATE_ADB_PULL: self._adb_pull_state_manager,
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

        self._wave_file_name["Muted"] = f'[Muted] {self._sealing_config_dict["General"]["device_name"]}.wav'
        self._wave_file_name["Unmuted"] = f'[Unmuted] {self._sealing_config_dict["General"]["device_name"]}.wav'

        # Open sequence                
        self._soundcheck_struct['construct_controller'].open_sequence(f'{self._soundcheck_struct["root_directory"]}\\Sequences\\Microphones\\SealingTest_WhiteNoise.sqc')                

        #Delete all files into "EasyVoiceRecorder" storage folder in sx5
        subprocess.run("adb shell rm -f /storage/emulated/0/EasyVoiceRecorder/*", text=True)

        # Go to Run Unmuted Test state
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_RUN_UMT)
        return

    def _run_test_unmuted_state_manager(self):
        """"""
        print ("- Record with unmuted microphone", end = '\r')

        # Run sequence
        self._soundcheck_struct['construct_controller'].run_sequence()
        
        # Get the recorded wav file and pull it 
        input_wav_filename=subprocess.run("adb shell ls /storage/emulated/0/EasyVoiceRecorder/", text=True, capture_output=True).stdout.strip('\n\r')            
        output_wav_filename = self._wave_file_name["Unmuted"]
        subprocess.run(f'adb pull "/storage/emulated/0/EasyVoiceRecorder/{input_wav_filename}" "{self._sealing_storage_folder}/{output_wav_filename}"', text=True, stdout=False)
        subprocess.run("adb shell rm -f /storage/emulated/0/EasyVoiceRecorder/*", text=True,  stdout=False) 

        print ("- Record with unmuted microphone\t OK")

        # Go to run muted test state
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_RUN_MT)
        return
   
    def _run_test_muted_state_manager(self):
        """"""
        print ("- Record with unmuted microphone", end = '\r')
        
        # Run sequence
        self._soundcheck_struct['construct_controller'].run_sequence()

        # Get the recorded wav file and pull it       
        input_wav_filename=subprocess.run("adb shell ls /storage/emulated/0/EasyVoiceRecorder/", text=True, capture_output=True).stdout.strip('\n\r')                  
        output_wav_filename=self._wave_file_name["Muted"]
        subprocess.run(f'adb pull "/storage/emulated/0/EasyVoiceRecorder/{input_wav_filename}" "{self._sealing_storage_folder}/{output_wav_filename}"', text=True,  stdout=False)
        subprocess.run("adb shell rm -f /storage/emulated/0/EasyVoiceRecorder/*", text=True,  stdout=False)
        
        # Go to run analyze state
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_ANALYZE)
        return

    def _analyze_state_manager(self):
        """"""
        print ("ANALYZE STATE")
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_STOP)
        return

    def _stop_state_manager(self):
        """"""        
        self._store_last_state()
        return
    
    def _main_state_machine_manager(self):
        """"""
        # Get function from dictionary
        fun = self._sealing_test_state_fun_dict.get(self._sealing_test_state)
        # Execute function
        fun()

        pass

    # ************************************************ #
    # **************** Public Methods **************** #
    # ************************************************ #

    def init(self):
        # Initialize Colorama library
        #cm.init(autoreset=True)
        self._parse_config_file()

        self._sealing_test_state = en.MainStateEnum.MAIN_STATE_INIT
        self._last_main_state = en.MainStateEnum.MAIN_STATE_INIT


    def run(self):
        """ Sealing Test Application """
        print ("\n**** RUN SEALING TEST ****")

        # Init
        self._init_state_manager()

        while not (self._sealing_test_state == en.SealingTestEnum.ST_TEST_STATE_STOP and
                   self._last_sealing_test_state == en.SealingTestEnum.ST_TEST_STATE_STOP):

            # Store the last state machine state
            self._store_last_state()

            # Run state machine at current state
            self._main_state_machine_manager()
