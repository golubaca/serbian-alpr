class Helper(object):

    def vivotek_camera(self,ip_address, username=None,passwd=None, protocol="rtsp", camera_name=None, fps=None, resolution=None):
        base_media_url = ""
        if protocol == "rtsp":
            base_media_url="live2.sdp"

        else:
            base_media_url = "video.mjpg"

        if username is not None:
            return "{}://{}:{}@{}/{}".format(protocol,username,passwd,ip_address,base_media_url)
        else:
            return "{}://{}/{}".format(protocol, ip_address, base_media_url)

    def axis_camera(self,ip_address, username=None,passwd=None, protocol="rtsp", quality=0, camera_name=None, fps=None, resolution=None):
        base_media_url = ""
        if protocol == "rtsp":
            base_media_url="live2.sdp"
        elif protocol == "snapshoot":
            protocol = "http"
            base_media_url = "axis-cgi/jpg/image.cgi"

        else:
            if quality is 0:
                base_media_url = "axis-cgi/mjpg/video.cgi?resolution=320x180&compression=40&camera=1&fps=5"
            else:
                base_media_url = "mjpg/video.mjpg"



        if username != None:
            return "{}://{}:{}@{}/{}".format(protocol,username,passwd,ip_address,base_media_url)
        else:
            return "{}://{}/{}".format(protocol, ip_address, base_media_url)

    def video_camera(self,ip_address, username=None,passwd=None, protocol="rtsp", camera_name=None, fps=None, resolution=None):
        return ip_address



    def generate_url(self,ip_address,username=None,passwd=None, camera_vendor="vivotek", protocol="rtsp", quality=0, camera_name=None, fps=3, resolution="1024x768"):

        method = None
        try:
            method = getattr(self, "{}_camera".format(camera_vendor))
        except Exception as e:
            raise NotImplementedError(
                "Class `{}` does not implement `{}`".format(Helper.__class__.__name__, method_name))

        return method(ip_address, username,passwd, protocol, quality)
