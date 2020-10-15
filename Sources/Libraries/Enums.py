class Enums:
    """    """
   
    # ------------------------------ #
    # ---------- Main.py ----------- #
    # ------------------------------ #
    class MainStateEnum:
        MAIN_STATE_INIT = "init"
        MAIN_STATE_SC_OPEN = "sc_open"
        MAIN_STATE_ADB_CONNECT = "adb_connect"
        MAIN_STATE_RECORDER_APP_OPEN = "recorder_app_open"
        MAIN_STATE_RUN_TEST = "run_test"
        MAIN_STATE_STOP = "stop"
        #MAIN_STATE_EXIT = "exit"
        

        @classmethod
        def vars(cls):
            return [name for name, value in vars(cls).items() if name.isupper()]

        @classmethod
        def values(cls):
            return [value for name, value in vars(cls).items() if name.isupper()]

    class SealingTestEnum:
        ST_TEST_STATE_INIT = "init"
        ST_TEST_STATE_RUN_UMT = "run_sequence_unmuted"        
        ST_TEST_STATE_RUN_MT = "run_sequence_muted"
        ST_TEST_STATE_ANALYZE = "analyze_sequences"
        ST_TEST_STATE_STOP = "stop"
        ST_TEST_STATE_EXIT = "exit"

        @classmethod
        def vars(cls):
            return [name for name, value in vars(cls).items() if name.isupper()]

        @classmethod
        def values(cls):
            return [value for name, value in vars(cls).items() if name.isupper()]

    class FrequencyResponseTestEnum:
        FR_TEST_STATE_INIT = "init"
        FR_TEST_STATE_RUN_SEQ = "run_sequence"        
        FR_TEST_STATE_ANALYZE_DATA = "analyze_data"        
        FR_TEST_STATE_STOP = "stop"
        FR_TEST_STATE_EXIT = "exit"

        @classmethod
        def vars(cls):
            return [name for name, value in vars(cls).items() if name.isupper()]

        @classmethod
        def values(cls):
            return [value for name, value in vars(cls).items() if name.isupper()]


if __name__ == "__main__":
    test = Enums.MainStateEnum
    print(type(test.vars()))
    print(test.vars())
    print(test.values())

    print ("exit" in test.values())