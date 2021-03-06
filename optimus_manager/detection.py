from optimus_manager.bash import exec_bash, BashError

NVIDIA_VENDOR_ID = "10de"
INTEL_VENDOR_ID = "8086"


class DetectionError(Exception):
    pass


def get_bus_ids(notation_fix=True):

    # TODO : Return code error checking
    lspci_output = exec_bash("lspci -n").stdout.decode('utf-8')

    bus_ids = {}

    for line in lspci_output.splitlines():

        items = line.split(" ")

        bus_id = items[0]

        # Notation quirk
        if notation_fix:
            bus_id = bus_id.replace(".", ":")

        pci_class = items[1]
        vendor_id, product_id = items[2].split(":")

        # Display controllers are identified by a 03xx class
        if pci_class[:2] != "03":
            continue

        if vendor_id == NVIDIA_VENDOR_ID:
            if "nvidia" in bus_ids.keys():
                raise DetectionError("Multiple Nvidia GPUs found !")
            bus_ids["nvidia"] = bus_id

        elif vendor_id == INTEL_VENDOR_ID:
            if "intel" in bus_ids.keys():
                raise DetectionError("Multiple Intel GPUs found !")
            bus_ids["intel"] = bus_id

    if "nvidia" not in bus_ids.keys():
        raise DetectionError("Cannot find Nvidia GPU in PCI devices list.")

    if "intel" not in bus_ids.keys():
        raise DetectionError("Cannot find Intel GPU in PCI devices list.")

    return bus_ids


def get_login_managers():

    login_managers = []

    for manager in ["sddm", "gdm", "lightdm"]:
        try:
            exec_bash("which %s" % manager)
            login_managers.append(manager)
        except BashError:
            pass

    return login_managers
