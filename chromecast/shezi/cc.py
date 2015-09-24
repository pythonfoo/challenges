
import pychromecast
from time import sleep

def get_some_cast():

    casts = pychromecast.get_chromecasts_as_dict()

    return casts[casts.keys()[0]]



def reboot_all_command():
    """Reboot all Chromecasts we can find."""

    for c in pychromecast.get_chromecasts_as_dict().values():
        print("rebooting {}".format(c.device.friendly_name))
        c.reboot()


def enumerate_apps_command(start_at=None):
    """Enumerate the apps that can be started.

    Will take quite a while and flash all the apps on the screen.
    """

    cast = get_some_cast()
    print("starting run on {}".format(cast.device.friendly_name))
    apps = {}

    app_ids = list(sorted(pychromecast.get_possible_app_ids()))
    
    if start_at is None:
        start_at = app_ids[0]
    
    for app_id in app_ids:
        if app_id <= start_at:
            continue
        try:
            print("     starting {}".format(app_id))
            cast.start_app(app_id)
            sleep(0.2)
            apps[app_id] = cast.app_display_name
            print("{}: {}".format(app_id, cast.app_display_name))
        except Exception as e:
            print(e)
            print("could not start {}".format(app_id))
            apps[app_id] = None

    return apps


if __name__ == '__main__':
    import commandeer
    commandeer.cli()
