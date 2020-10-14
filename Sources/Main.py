#!/usr/bin/env python

import sys
import os
import subprocess
import time
from distutils.util import strtobool

from soundcheck_tcpip.soundcheck.installation import construct_installation
from Soundcheck.util import configure_ini_for_automation, get_sc_root, construct_controller, get_standard_sequence_dir, is_calibration_curve
import socket

from Libraries.Enums import Enums as en
from Libraries.ParseXml import XmlDictConfig
from xml.etree import ElementTree

from Libraries.Timer import Timer

from Scripts.SealingTest import SealingTest
from Scripts.FrequencyResponseTest import FrequencyResponseTest


class Main(object):
    """ """

    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self):
        """ Constructor """
        self._main_config_dict: dict
        
        self._main_storage_folder = ""

        self._soundcheck_struct = {
            'root_directory': "",
            'installation': "",
            'ini_file': None,
            'construct_controller': None
        }

        self._test_list_dict = {
            'sealing_test': {
                'script': None,
                'run': False,
            },
            'frequency_response': {
                'script': None,
                'run': False,
            }       
        }

        # State Machine
        self._main_state_fun_dict = {
            en.MainStateEnum.MAIN_STATE_INIT: self._init_state_manager,
            en.MainStateEnum.MAIN_STATE_SC_OPEN: self._sc_open_state_manager,
            en.MainStateEnum.MAIN_STATE_ADB_CONNECT: self._adb_connect_state_manager,
            en.MainStateEnum.MAIN_STATE_RECORDER_APP_OPEN: self._recorder_app_state_manager,
            en.MainStateEnum.MAIN_STATE_RUN_TEST: self._run_test_state_manager,
            en.MainStateEnum.MAIN_STATE_STOP: self._stop_state_manager,
            #en.MainStateEnum.MAIN_STATE_EXIT: self._exit_state_manager
        }

        self._main_state: None
        self._last_main: None

    # ---------------------------------------------------------------- #
    # ----------------------- Private Methods ------------------------ #
    # ---------------------------------------------------------------- #
    @staticmethod
    def _print_help():
        """"""
        pass

    def _parse_config_file(self):
        """"""
        self._main_config_dict = XmlDictConfig(ElementTree.parse('Config.xml').getroot())
        
        return

    # ------------------ STATE MACHINE ------------------ #
    def _go_to_next_state(self, state):
        """"""
        # Store last state
        self._store_last_state()

        # Go to next state
        self._main_state = state
        return

    def _store_last_state(self):
        self._last_main_state = self._main_state
        return

    def _init_state_manager(self):
        """"""
       
        # Create storage folder  
        date = time.strftime("%d%m_%H%M_%S")
        self._main_storage_folder = f"{os.getcwd()}/{self._main_config_dict['General']['storage_folder']}_{date}"
        os.mkdir(self._main_storage_folder)

        # Populate list of test
        self._test_list_dict['sealing_test']['script'] = SealingTest(soundcheck_struct=self._soundcheck_struct, storage_folder=self._main_storage_folder)
        self._test_list_dict['sealing_test']['run'] = bool(strtobool(self._main_config_dict['TestList']['sealing_test']))
                
        #self._test_list_dict['frequency_response']['script'] = FrequencyResponseTest(soundcheck_struct=self._soundcheck_struct, storage_folder=self._main_storage_folder)
        #self._test_list_dict['frequency_response']['run'] = bool(strtobool(self._main_config_dict['TestList']['frequency_response_test']))
                       

        # Got to Open SoundCheck state
        self._go_to_next_state(en.MainStateEnum.MAIN_STATE_SC_OPEN) #TODO
        #self._go_to_next_state(en.MainStateEnum.MAIN_STATE_ADB_CONNECT)

        return

    def _sc_open_state_manager(self):
        """"""
        self._soundcheck_struct['root_directory'] = self._main_config_dict['Soundcheck']['root_dir']
        self._soundcheck_struct['installation'] = construct_installation([18, 0], self._soundcheck_struct['root_directory'])        
        self._soundcheck_struct['ini_file'] = configure_ini_for_automation(self._soundcheck_struct['installation'])
        self._soundcheck_struct['construct_controller'] = construct_controller(self._soundcheck_struct['installation'])

        try:
            print("Launching SoundCheck...")
            self._soundcheck_struct['construct_controller'].launch(timeout=60)
            self._soundcheck_struct['construct_controller'].set_lot_number("1234")
        except socket.timeout:
            print("Socket timed out...exiting...")

            # Go to stop state
            self._go_to_next_state(en.MainStateEnum.MAIN_STATE_STOP)
        else: 
            # Go to ADB connect state
            self._go_to_next_state(en.MainStateEnum.MAIN_STATE_ADB_CONNECT)        

        return

    def _adb_connect_state_manager(self):
        """"""
        count = 0
        res = -1
        num_of_try = 60

        # Start Timer
        timer = Timer()
        timer.start()

        while (count < num_of_try):
            if timer.elapsed_time_s(2) >= 1:
                print("- Waiting for SX5 device " + "."*count, end='\r')
                
                # Run fake command to know if adb shell works
                res = subprocess.run("adb shell date", text=True, capture_output=True)     
                
                if res.stdout:
                    timer.stop()
                    break
                else:
                    timer.reset()

                count += 1
        
        if not res.stdout:            
            sys.stdout.write("\033[K")
            print("No Device Found", end="\r")            

        else:
            sys.stdout.write("\033[K")
            print ("SX5 Found", end = "\r")               
        
        # Go to Open Record App State
        self._go_to_next_state(en.MainStateEnum.MAIN_STATE_RECORDER_APP_OPEN)
        
        return

    def _recorder_app_state_manager(self):
        """"""
        easyvoicerecorder_activity_name = "com.digipom.easyvoicerecorder.pro/com.digipom.easyvoicerecorder.ui.activity.EasyVoiceRecorderActivity"

        print ('Opening "EasyVoiceRecorder" app on the device')
        subprocess.run(f"adb shell am start -n {easyvoicerecorder_activity_name}", text=True, capture_output=True)

        # Go to Run Test
        self._go_to_next_state(en.MainStateEnum.MAIN_STATE_RUN_TEST)
        return

    def _run_test_state_manager(self):
        """"""
        # Run Selected Test
        for test in self._test_list_dict.keys():
            if self._test_list_dict[test]['run']:
                self._test_list_dict[test]['script'].init()
                self._test_list_dict[test]['script'].run()           

        # Go to stop state
        self._go_to_next_state(en.MainStateEnum.MAIN_STATE_STOP)
        return

    def _stop_state_manager(self):
        """"""        
        return
    
    def _main_state_machine_manager(self):
        """"""
        # Get function from dictionary
        fun = self._main_state_fun_dict.get(self._main_state)

        # Execute function
        fun()

        return

    # ************************************************ #
    # **************** Public Methods **************** #
    # ************************************************ #

    def init(self):
        # Initialize Colorama library
        #cm.init(autoreset=True)

        # Parse config file 
        self._parse_config_file()
        
        self._main_state = en.MainStateEnum.MAIN_STATE_INIT
        self._last_main_state = en.MainStateEnum.MAIN_STATE_INIT


    def run(self):
        """ Main Application """

        # Init
        self._init_state_manager()

        while not (self._main_state == en.MainStateEnum.MAIN_STATE_STOP and
                   self._last_main_state == en.MainStateEnum.MAIN_STATE_STOP):

            # Store the last state machine state
            self._store_last_state()

            # Run state machine at current state
            self._main_state_machine_manager()


if __name__ == "__main__":    
    test = Main()
    test.init()
    test.run()
