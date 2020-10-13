from Libraries.Enums import Enums as en

class SealingTest(object):
    """ """

    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self):
        """ Constructor """
        
        # State Machine
        self._sealing_test_state_fun_dict = {
            en.SealingTestEnum.ST_TEST_STATE_INIT: self._init_state_manager,
            en.SealingTestEnum.ST_TEST_STATE_RUN_UMT: self._run_test_unmuted_state_manager,
            en.SealingTestEnum.ST_TEST_STATE_ADB_PULL: self._adb_pull_state_manager,
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

    # def _parse_config_file(self):
    #     """"""
    #     self._main_config_dict = XmlDictConfig(ElementTree.parse('Config.xml').getroot())
        
    #     return

    # ------------------ STATE MACHINE ------------------ #
    def _go_to_next_state(self, state):
        """"""
        # Store last state
        self._store_last_state()

        # Go to next state
        self._sealing_test_state = state
        return

    def _store_last_state(self):
        self._last_sealing_test_state = self._sealing_test_state
        return

    def _init_state_manager(self):
        """"""

        #sequence_path = get_standard_sequence_dir().joinpath('Loudspeakers', 'Complete test.sqc') #sistemare path
        # sequence_path = "C:\Program Files\SoundCheck 18\Sequences\Loudspeakers\Complete test.sqc"
        # open_result = self._soundcheck_struct['construct_controller'].open_sequence(sequence_path)
        self._go_to_next_state(en.SealingTestEnum.ST_TEST_STATE_STOP)
        return

    def _run_test_unmuted_state_manager(self):
        """"""
        
        return

    def _adb_pull_state_manager(self):
        """"""
        return

    def _run_test_muted_state_manager(self):
        """"""
        return

    def _analyze_state_manager(self):
        """"""
        return

    def _stop_state_manager(self):
        """"""        
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
        
        self._sealing_test_state = en.MainStateEnum.MAIN_STATE_INIT
        self._last_main_state = en.MainStateEnum.MAIN_STATE_INIT


    def run(self):
        """ Sealing Test Application """
        print ("RUN SEALING TEST")

        # Init
        self._init_state_manager()

        while not (self._sealing_test_state == en.SealingTestEnum.ST_TEST_STATE_STOP and
                   self._last_sealing_test_state == en.SealingTestEnum.ST_TEST_STATE_STOP):

            # Store the last state machine state
            self._store_last_state()

            # Run state machine at current state
            self._main_state_machine_manager()
