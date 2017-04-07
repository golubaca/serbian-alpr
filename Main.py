###############################################################################
# Fajl startuje car-in sistem sa predefinisanim brojem kamera koje ucestvuju. #
###############################################################################

import ConfigParser
import multiprocessing
from carinaLibs import IPStream

config = ConfigParser.ConfigParser()
config.read(".carinaConfig.ini")
sections = config.sections()

for camera in sections:
    if camera.startswith('Camera'):
        ip = config.get(camera, 'ip')
        protocol = config.get(camera, 'protocol')
        username = config.get(camera, 'username')
        passwd = config.get(camera, 'passwd')
        vendor = config.get(camera, 'vendor')
        st = IPStream.IPStream(ip, username, passwd, protocol=protocol, vendor=vendor)

        p = multiprocessing.Process(target=st.start)
        p.start()
