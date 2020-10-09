#!/usr/bin/env python

from Libraries.Enums import Enums as en


class Main(object):
    """ """

    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self):
        """ Constructor """

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

    # ------------------ STATE MACHINE ------------------ #
    def _go_to_next_state(self, state):
        """"""
        # Store last state
        self._last_main_state = self._main_state

        # Go to next state
        self._main_state = state
        pass

    def _init_state_manager(self):
        """"""
        self._go_to_next_state(en.MainStateEnum.MAIN_STATE_SC_OPEN)
        return

    def _sc_open_state_manager(self):
        """"""
        self._go_to_next_state(en.MainStateEnum.MAIN_STATE_ADB_CONNECT)        
        return

    def _adb_connect_state_manager(self):
        """"""
        self._go_to_next_state(en.MainStateEnum.MAIN_STATE_RECORDER_APP_OPEN)
        return

    def _recorder_app_state_manager(self):
        """"""
        self._go_to_next_state(en.MainStateEnum.MAIN_STATE_RUN_TEST)
        return

    def _run_test_state_manager(self):
        """"""
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

        pass

    # ************************************************ #
    # **************** Public Methods **************** #
    # ************************************************ #

    def init(self):
        # Initialize Colorama library
        #cm.init(autoreset=True)
        
        self._main_state = en.MainStateEnum.MAIN_STATE_INIT
        self._last_main_state = en.MainStateEnum.MAIN_STATE_INIT


    def run(self):
        """ Main Application """

        # Init
        self._init_state_manager()

        while not (self._main_state == en.MainStateEnum.MAIN_STATE_STOP and
                   self._last_main_state == en.MainStateEnum.MAIN_STATE_STOP):

            # Store the last state machine state
            self._last_main_state = self._main_state

            # Run state machine at current state
            self._main_state_machine_manager()




if __name__ == "__main__":
    test = Main()
    test.init()
    test.run()
