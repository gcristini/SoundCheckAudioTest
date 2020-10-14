from Libraries.Enums import Enums as en

class FrequencyResponseTest(object):
    """ """

    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self, storage_folder=""):
        """ Constructor """

        self._main_storage_folder=storage_folder
        
        pass
       
    # ---------------------------------------------------------------- #
    # ----------------------- Private Methods ------------------------ #
    # ---------------------------------------------------------------- #
    @staticmethod
    def _print_help():
        """"""
        pass

  
    def init(self):
        # Initialize Colorama library
        #cm.init(autoreset=True)
        
        # self._sealing_test_state = en.MainStateEnum.MAIN_STATE_INIT
        # self._last_main_state = en.MainStateEnum.MAIN_STATE_INIT
        return

    def run(self):
        """ Main Application """

        # Init
        #self._init_state_manager()

        # while not (self._sealing_test_state == en.SealingTestEnum.MAIN_STATE_STOP and
        #            self._last_sealing_test_state == en.SealingTestEnum.MAIN_STATE_STOP):

        #     # Store the last state machine state
        #     self._store_last_state()

        #     # Run state machine at current state
        #     self._main_state_machine_manager()
        print ("RUN FREQUENCY RESPONSE TEST")

