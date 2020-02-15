from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        # TODO: create a dictionary that for other switches and distance, including it's own and 0
        self.forw_table = {
            self : 0
        }

    def handle_rx (self, packet, port):
        # print("DVRouter received a packet!")
        # Add your code here!

        #Logging
        trace = ','.join((s.name for s in packet.trace))

        if packet.dst is not self:
          self.log("NOT FOR ME: %s %s" % (packet, trace), level="WARNING")
        else:
          self.log("rx: %s %s" % (packet, trace))

        #Dealing with packets
        if(isinstance(packet,RoutingUpdate)):

            #Update our forw_table
            for i in packet.all_dests():
                #if dest not in our forwarding table, add it with + 1
                if i not in self.forw_table:
                    self.forw_table[i] = packet.get_distance(i) + 1
                #if it is, compare if it's less than what it currently is and only change if it is
                else:
                    if(self.forw_table[i] < packet.get_distance(i) + 1):
                        self.forw_table[i] = packet.get_distance(i) + 1

            if packet.dst is not self:
                #We flood an updated packet to all ports but its own
                update = RoutingUpdate()
                for i in packet.all_dests():
                    update.add_destination(i, packet.get_distance(i) + 1)
                self.send(update, port, flood = True)











        #
        #   # If we received Ping
        # if type(packet) is Ping:
        #     # Trace this path
        #     import core
        #     core.events.highlight_path([packet.src] + packet.trace)
        #     # Send a pong response
        #     self.send(Pong(packet), port)
        #
        #
        #  #If we received Pong:
        # if type(packet) is Pong:
        #      # we do nothing
        #      raise NotImplementedError
        #
        # if type(packet) is DiscoveryPacket:
        #      # TODO: Implement
        #      raise NotImplementedError
        #
        # if type(packet) is RoutingUpdate:
        #      #TODO: Implement
        #      raise NotImplementedError
