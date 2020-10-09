#!/usr/bin/env python

class Main(object):
    """ """

    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self):
        """ Constructor """

    # ---------------------------------------------------------------- #
    # ----------------------- Private Methods ------------------------ #
    # ---------------------------------------------------------------- #
    @staticmethod
    def _print_help():
        """"""        
    pass

    # ******** State Machine Functions ******** #
    def _init_state_manager(self):
        """"""
       

    def _wait_state_manager(self):
        """"""
        # cmd = input("- Please enter a command: ")

        # if cmd == enum.MainAppCommands.MAC_RUN:
        #     # Go to run state
        #     self._main_state = enum.MainAppStatesEnum.MAS_RUN

        # elif cmd == enum.MainAppCommands.MAC_HELP:
        #     # Go to wait state
        #     self._main_state = enum.MainAppStatesEnum.MAS_HELP

        # elif cmd == enum.MainAppCommands.MAC_EXIT:
        #     # Go to exit state
        #     self._main_state = enum.MainAppStatesEnum.MAS_EXIT

        # else:
        #     # Go to help state
        #     self._main_state = enum.MainAppStatesEnum.MAS_HELP
        # pass

    def _run_state_manager(self):
        """"""
        print(cm.Fore.GREEN + cm.Style.DIM + "\n---------- Run Test ----------")
        #self._TemperatureTestSX5_TC.run_test()
        self._TemperatureTestSX5_TS.run_test()

        # Go to Wait state
        # self._main_state = enum.MainAppStatesEnum.MAS_WAIT

        pass

    def _help_state_manager(self):
        """"""
        # # Print Help
        # self._print_help()

        # # Go to wait state
        # self._main_state = enum.MainAppStatesEnum.MAS_WAIT
        pass

    def _exit_state_manager(self):
        """"""
        print(cm.Fore.MAGENTA + "Goodbye!")
        sys.exit()
        pass

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
    def main(self):
        """ Main Application """

        # # Init
        # self._init_state_manager()

        # while not (self._main_state == enum.MainAppStatesEnum.MAS_EXIT and
        #            self._last_main_state == enum.MainAppStatesEnum.MAS_EXIT):

        #     # Store the last state machine state
        #     self._last_main_state = self._main_state

        #     # Run state machine at current state
        #     self._main_state_machine_manager()


Main().main()

