import optimus_manager.checks as checks
from optimus_manager.bash import exec_bash, BashError
from optimus_manager.xorg import configure_xorg
from optimus_manager.login_managers import configure_login_managers


class SwitchError(Exception):
    pass


def switch_to_intel(config):

    print("Switching to Intel")

    # Nvidia modules
    print("Unloading Nvidia modules")

    try:
        exec_bash("modprobe -r nvidia_drm nvidia_modeset nvidia_uvm nvidia")
    except BashError as e:
        raise SwitchError("Cannot unload Nvidia modules : %s" % str(e))

    if config["optimus"]["switching"] == "bbswitch":

        # Load bbswitch
        print("Loading bbswitch module")
        try:
            exec_bash("modprobe bbswitch")
        except BashError as e:
            raise SwitchError("Cannot load bbswitch : %s" % str(e))

        # bbswitch switching
        print("Ordering OFF via bbswitch")
        exec_bash("echo OFF | tee /proc/acpi/bbswitch")
        if checks.is_gpu_powered():
            raise SwitchError("bbswitch refuses to turn OFF the GPU")
        else:
            print("bbswitch reports that the GPU is OFF")

    elif config["optimus"]["switching"] == "nouveau":

        modeset_value = {"yes": 1, "no": 0}[config["intel"]["modeset"]]

        # Loading nouveau
        print("Loading nouveau module")
        try:
            exec_bash("modprobe nouveau modeset=%d" % modeset_value)
        except BashError as e:
            raise SwitchError("Cannot load nouveau : %s" % str(e))

    # Xorg configuration
    print("Configuring Xorg...")
    configure_xorg(config, mode="intel")

    # Login managers configuration
    print("Configuring login managers..")
    configure_login_managers(mode="intel")


def switch_to_nvidia(config):

    print("Switching to Nvidia")

    if config["optimus"]["switching"] == "bbswitch":

        # bbswitch module
        print("Loading bbswitch module")
        try:
            exec_bash("modprobe bbswitch")
        except BashError as e:
            raise SwitchError("Cannot load bbswitch : %s" % str(e))

        # bbswitch switching
        print("Ordering ON via bbswitch")
        exec_bash("echo ON | tee /proc/acpi/bbswitch")
        if not checks.is_gpu_powered():
            raise SwitchError("bbswitch refuses to turn ON the GPU")
        else:
            print("bbswitch reports that the GPU is ON")

    # Unloading nouveau
    print("Unloading nouveau module")
    try:
        exec_bash("modprobe -r nouveau")
    except BashError as e:
        raise SwitchError("Cannot unload nouveau : %s" % str(e))

    # Nvidia modules
    print("Loading Nvidia modules")

    modeset_value = {"yes": 1, "no": 0}[config["nvidia"]["modeset"]]
    pat_value = {"yes": 1, "no": 0}[config["nvidia"]["PAT"]]

    if not checks.is_pat_available():
        print("Warning : Page Attribute Tables are not available on your system.\n"
              "Disabling the PAT option for Nvidia.")
        pat_value = 0

    try:
        exec_bash("modprobe nvidia NVreg_UsePageAttributeTable=%d" % pat_value)
        exec_bash("modprobe nvidia_uvm nvidia_modeset")
        exec_bash("modprobe nvidia_drm modeset=%d" % modeset_value)

    except BashError as e:
        raise SwitchError("Cannot load Nvidia modules : %s" % str(e))

    # Xorg configuration
    print("Configuring Xorg...")
    configure_xorg(config, mode="nvidia")

    # Login managers configuration
    print("Configuring login managers..")
    configure_login_managers(mode="nvidia")
