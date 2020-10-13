from pathlib import Path
import os
from contextlib import contextmanager
from soundcheck_tcpip.soundcheck.controller import SCControlTCPIP


def get_sc_root():
    """ get the SoundCheck root directory by navigating up
    three parent directories from the location of this script.

    :return:
    """
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    return current_dir.parent.parent.parent


def is_calibration_curve(curve_name):
    """ decide if a curve is a SoundCheck calibration curve by
    searching for some qualifier strings in the curve name

    :param curve_name:
    :return:
    """
    qualifiers = ['corr-in', 'corr-out', 'eq-out']
    return any([q in curve_name for q in qualifiers])

@contextmanager
def configure_ini_for_automation(installation, tcpip_port_orig=4444):
    """ Select INI file options that allow SoundCheck to be opened and
    immediately controlled from external applications without
    interruptions or blocking dialogs.

    :param installation:
    :param tcpip_port_orig:
    """

    try:
        #
        # capture the current configuration so that we can restore it
        # when this context is exited
        #
        suppress_login_orig = installation.get_ini_option('User Interface', 'SupressLogin', default="TRUE")
        suppress_pdfs_orig = installation.get_ini_option('User Interface', 'SupressPDFs', default="TRUE")
        run_setup_wizard_orig = installation.get_ini_option('MiscSettings', 'RUN SETUP WIZARD', default="FALSE")
        show_splashscreen_orig = installation.get_ini_option('Dialogs', 'SHOW SPLASHSCREEN', default="FALSE")
        suppress_dialogs_orig = installation.get_ini_option('External Control', 'SUPPRESS DIALOGS', default="TRUE")
        tcpip_enabled_orig = installation.get_ini_option('External Control', 'TCP IP SERVER ENABLED', default="TRUE")
        tcpip_port_orig = installation.get_ini_option('External Control', 'TCP IP SERVER PORT', default="4444")

        #
        # dialogs can block the TCP/IP connection.  Disable the relevant
        # ones so that blocking due to a dialog does not occur.
        #
        installation.set_ini_option('User Interface', 'SupressLogin', 'TRUE')
        installation.set_ini_option('User Interface', 'SupressPDFs', 'TRUE')
        installation.set_ini_option('MiscSettings', 'RUN SETUP WIZARD', 'FALSE')
        installation.set_ini_option('Dialogs', 'SHOW SPLASHSCREEN', 'False')
        installation.set_ini_option('External Control', 'SUPPRESS DIALOGS', 'TRUE')
        installation.set_ini_option('External Control', 'TCP IP SERVER ENABLED', 'TRUE')
        installation.set_ini_option('External Control', 'TCP IP SERVER PORT', str(tcpip_port_orig))

        yield

    finally:
        #
        # dialogs can block the TCP/IP connection.  Disable the relevant
        # ones so that blocking due to a dialog does not occur.
        #
        installation.set_ini_option('User Interface', 'SupressLogin', suppress_login_orig)
        installation.set_ini_option('User Interface', 'SupressPDFs', suppress_pdfs_orig)
        installation.set_ini_option('MiscSettings', 'RUN SETUP WIZARD', run_setup_wizard_orig)
        installation.set_ini_option('Dialogs', 'SHOW SPLASHSCREEN', show_splashscreen_orig)
        installation.set_ini_option('External Control', 'SUPPRESS DIALOGS', suppress_dialogs_orig)
        installation.set_ini_option('External Control', 'TCP IP SERVER ENABLED', tcpip_enabled_orig)
        installation.set_ini_option('External Control', 'TCP IP SERVER PORT', tcpip_port_orig)


def construct_controller(installation, tcpip_port=4444):
    """ construct a SoundCheck TCP/IP controller object by wrapping an
    installation object. The installation takes care of interacting with
    SoundCheck files such as the INI, while the controller is responsible
    for communicating with a running instance of SoundCheck via TCP/IP.

    :param version:
    :param tcpip_port:
    :return:
    """
    return SCControlTCPIP(installation)


def setup_sc_argparse(parser):
    """ Add some common arguments to an existing command line arg parser

    :param parser:
    :return:
    """
    parser.add_argument('--shutdown', action='store_true',
                        help='Flag for shutting down SoundCheck after test runs')
    parser.add_argument('--launch', action='store_true',
                        help='Flag for launching SoundCheck before test')


def safe_open_sequence(sc_controller, sqc_name, sqc_path):
    """ Opens a sequence only if it is different from the sequence currently
    loaded in SoundCheck. Helpful for making efficient scripts that may be run
    several times with different arguments.

    :param sc_controller:
    :param sqc_name:
    :param sqc_path:
    :return:
    """
    current_seq = sc_controller.current_sequence()
    if not current_seq == sqc_name:
        print(f'Opening Sequence: {sqc_name}')
        return sc_controller.open_sequence(sqc_path)


def get_standard_sequence_dir():
    return Path(get_sc_root(), 'Sequences')


def get_automation_sequence(sqc_name):
    sqc_path = get_standard_sequence_dir().joinpath('Automation', f'{sqc_name}.sqc')
    if not sqc_path.exists():
        raise FileNotFoundError(f'Example sequence named "{sqc_name}" not found at expected path {sqc_path}')
    return sqc_path
