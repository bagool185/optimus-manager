import os
import optimus_manager.envs as envs
from optimus_manager.detection import get_login_managers
import optimus_manager.checks as checks
from optimus_manager.bash import exec_bash, BashError


class LoginManagerError(Exception):
    pass


def restart_login_manager(config):

    login_manager_control = config["optimus"]["login_manager_control"]

    if login_manager_control != "yes":
        print("Login manager control is disabled, not restarting it.")
        return

    try:
        exec_bash("systemctl restart display-manager")
    except BashError as e:
        raise LoginManagerError("Warning : cannot restart service display-manager : %s" % str(e))

    if not checks.is_login_manager_active(config):
        raise LoginManagerError("Warning : cannot restart service display-manager.")


def configure_login_managers(mode):

    login_managers = get_login_managers()

    if len(login_managers) == 0:
        msg = "No supported login manager detected. Please manually configure" \
              "your login manager to use the display setup script at %s. If you" \
              "use xinit, add this script to your .xinitrc" % envs.XSETUP_PATH
        print(msg)
        return

    for manager_name in login_managers:

        if manager_name == "sddm":
            print("\tConfiguring SDDM")
            _configure_sddm(mode)
        elif manager_name == "lightdm":
            print("\tConfiguring LightDM")
            _configure_lightdm(mode)
        elif manager_name == "gdm":
            print("\tConfiguring GDM")
            _configure_gdm(mode)


def _configure_sddm(mode):

    XSETUP_SDDM_PATH = "/usr/share/sddm/scripts/Xsetup"

    header = "#!/bin/sh\n" \
             "# Xsetup - run as root before the login dialog appears\n"

    if mode == "intel":
        text = header

    elif mode == "nvidia":
        text = header + "exec %s\n" % envs.XSETUP_PATH

    try:
        with open(XSETUP_SDDM_PATH, 'w') as f:
            f.write(text)

    except IOError:
        raise LoginManagerError("Cannot write to %s" % XSETUP_SDDM_PATH)


def _configure_lightdm(mode):

    CONF_FOLDER_PATH = "/etc/lightdm/lightdm.conf.d/"

    conf_filepath = os.path.join(CONF_FOLDER_PATH, envs.LIGHTDM_CONF_NAME)

    if mode == "intel":

        if os.path.isfile(conf_filepath):
            os.remove(conf_filepath)

    elif mode == "nvidia":

        if not os.path.isdir(CONF_FOLDER_PATH):
            os.makedirs(CONF_FOLDER_PATH)

        text = "[Seat:*]\n" \
               "display-setup-script=%s\n" % envs.XSETUP_PATH

        try:
            with open(conf_filepath, 'w') as f:
                f.write(text)

        except IOError:
            raise LoginManagerError("Cannot write to %s" % conf_filepath)


def _configure_gdm(mode):

    FOLDER_1_PATH = "/usr/share/gdm/greeter/autostart/"
    FOLDER_2_PATH = "/etc/xdg/autostart/"

    file_1_path = os.path.join(FOLDER_1_PATH, envs.GDM_DESKTOP_FILE_NAME)
    file_2_path = os.path.join(FOLDER_1_PATH, envs.GDM_DESKTOP_FILE_NAME)

    if mode == "intel":

        if os.path.isfile(file_1_path):
            os.remove(file_1_path)

        if os.path.isfile(file_2_path):
            os.remove(file_2_path)

    elif mode == "nvidia":

        if not os.path.isdir(FOLDER_1_PATH):
            os.makedirs(FOLDER_1_PATH)

        if not os.path.isdir(FOLDER_2_PATH):
            os.makedirs(FOLDER_2_PATH)

        text = "[Desktop Entry]\n" \
               "Type=Application\n" \
               "Name=Optimus Manager X Setup\n" \
               "Exec=sh -c \"xrandr --setprovideroutputsource modesetting NVIDIA-0; xrandr --auto\"\n" \
               "NoDisplay=true\n" \
               "X-GNOME-Autostart-Phase=DisplayServer\n"

        try:

            for filepath in [file_1_path, file_2_path]:
                with open(filepath, 'w') as f:
                    f.write(text)

        except IOError:
            raise LoginManagerError("Cannot write to %s" % filepath)
