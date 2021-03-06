import os
import optimus_manager.envs as envs


def clean_all():
    clean_xorg()
    clean_login_managers()


def clean_xorg():

    try:
        os.remove(envs.XORG_CONF_PATH)
        print("Removed %s" % envs.XORG_CONF_PATH)
    except FileNotFoundError:
        pass


def clean_login_managers():

    def _clean_sddm():

        XSETUP_SDDM_PATH = "/usr/share/sddm/scripts/Xsetup"

        text = "#!/bin/sh\n" \
               "# Xsetup - run as root before the login dialog appears\n"

        try:
            with open(XSETUP_SDDM_PATH, 'w') as f:
                f.write(text)
                print("Reverted %s" % XSETUP_SDDM_PATH)

        except FileNotFoundError:
            pass

    def _clean_lightdm():

        CONF_FOLDER_PATH = "/etc/lightdm.conf.d/"
        conf_filepath = os.path.join(CONF_FOLDER_PATH, envs.LIGHTDM_CONF_NAME)

        try:
            os.remove(conf_filepath)
            print("Removed %s" % conf_filepath)
        except FileNotFoundError:
            pass

    def _clean_gdm():

        FOLDER_1_PATH = "/usr/share/gdm/greeter/autostart/"
        FOLDER_2_PATH = "/etc/xdg/autostart/"

        file_1_path = os.path.join(FOLDER_1_PATH, envs.GDM_DESKTOP_FILE_NAME)
        file_2_path = os.path.join(FOLDER_2_PATH, envs.GDM_DESKTOP_FILE_NAME)

        try:
            os.remove(file_1_path)
            print("Removed %s" % file_1_path)
        except FileNotFoundError:
            pass

        try:
            os.remove(file_2_path)
            print("Removed %s" % file_2_path)
        except FileNotFoundError:
            pass

    # -----------

    _clean_sddm()
    _clean_lightdm()
    _clean_gdm()
