from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        pass

    def handle_rx (self, packet, port):
        # Add your code here!
        if packet.dst is NullAddress:
          # Silently drop messages not to anyone in particular
          return

        trace = ','.join((s.name for s in packet.trace))

        if packet.dst is not self:
          self.log("NOT FOR ME: %s %s" % (packet, trace), level="WARNING")
        else:
          self.log("rx: %s %s" % (packet, trace))

          # If we received Ping
          if type(packet) is Ping:
            # Trace this path
            import core
            core.events.highlight_path([packet.src] + packet.trace)
            # Send a pong response
            self.send(Pong(packet), port)


         #If we received Pong:
        if type(packet) is Pong:
             # we do nothing
             raise NotImplementedError

        if type(packet) is DiscoveryPacket:
             # TODO: Implement
             raise NotImplementedError

        if type(packet) is RoutingUpdate:
             #TODO: Implement
             raise NotImplementedError
