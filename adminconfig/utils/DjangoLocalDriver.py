import os
import sys

import django


class LocalDriver:
    def __init__(self) -> None:
        self.root_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )
        sys.path.append(self.root_path)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adminconfig.settings")
        django.setup()


def test():
    from taiwan_area_info.models import AreaInfo

    temp = AreaInfo.objects.all()
    print(temp.first())


if __name__ == "__main__":
    test()
