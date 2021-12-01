from zeroconf import ServiceBrowser, Zeroconf


class PupilInvisibleListener:
    def __init__(self, added_cb=None, removed_cb=None, updated_cb=None):
        self.added_cb = added_cb
        self.removed_cb = removed_cb
        self.updated_cb = updated_cb
        self._devices_found = {}

    def add_service(self, zeroconf, type, name):
        if self.is_valid_name(name):
            info = zeroconf.get_service_info(type, name)
            print(f"Found Pupil Invisible device:")
            print(f"\tName: {name}")
            print(f"\tFull info: {info}")

    def remove_service(self, zeroconf, type, name):
        pass

    def update_service(self, zeroconf, type, name):
        pass

    @staticmethod
    def is_valid_name(name: str) -> bool:
        return name.split(":")[0] == "PI monitor"


if __name__ == "__main__":
    zeroconf = Zeroconf()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", PupilInvisibleListener())
    try:
        input("Press enter to exit...\n\n")
    finally:
        zeroconf.close()
