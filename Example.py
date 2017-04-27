from JRecInterface import JRecInterface
import jsonpickle

interface = JRecInterface()
interface.request()
interface.response(True)
interface.request()
interface.response(False)
interface.request()
interface.response(True)

# Get Json String
s = interface.recommender_json_str()
# Construct from Json String
interface_t = JRecInterface(recommender_json_str=s)


interface = JRecInterface()
req = interface.request()
print "Document ID:", req.id
print req.text
print

continue_loop = True
while continue_loop:
    while True:
        str = raw_input("Enter user response: yes/no/quit:")
        if str == "yes":
            interface.response(True)
            break
        elif str == "no":
            interface.response(False)
            break
        elif str == "quit":
            continue_loop = False
            break
    if continue_loop:
        req = interface.request()
        print "Document ID:", req.id
        print req.text
        print
