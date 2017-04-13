from JRecInterface import JRecInterface

interface = JRecInterface()
interface.request()
interface.response(True)
s = interface.recommender_json_str()
interface_t = JRecInterface(recommender_json_str=s)
