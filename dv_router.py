from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        self.forw_table = {
            self : 0
        }
        #We need to flood a DiscoveryPacket of ourselves
        discover = DiscoveryPacket(self, 1)
        self.send(discover, flood = True) #TODO: find own port to not send to self?


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

        #RoutingUpdate packet
        if(isinstance(packet,RoutingUpdate)):

            updates_to_flood = {}

            #Update our forw_table
            for i in packet.all_dests():
                #if dest not in our forwarding table, add it with + 1
                if i not in self.forw_table:
                    self.forw_table[i] = packet.get_distance(i) + 1
                    updates_to_flood[i] = packet.get_distance(i) + 1
                    #We flood our update to the network only when it's a newly discovered entity
                    update = RoutingUpdate()
                    for i in updates_to_flood:
                        update.add_destination(i, updates_to_flood[i])
                    self.send(update, port, flood = True)
                    print(self.forw_table)

                #if it is in forw_table, add it if the path + 1 is shorter
                else:
                    if(self.forw_table[i] > packet.get_distance(i) + 1):
                        self.forw_table[i] = packet.get_distance(i) + 1
                        updates_to_flood[i] = packet.get_distance(i) + 1
                        #We flood our update to the network only when we found a shorter path
                        update = RoutingUpdate()
                        for i in updates_to_flood:
                            update.add_destination(i, updates_to_flood[i])
                        self.send(update, port, flood = True)


        #DiscoveryPacket packet
        #NOT dealing with link latency yet
        if(isinstance(packet, DiscoveryPacket)):
            if packet.src not in self.forw_table:
                self.forw_table[packet.src] = packet.latency
            update = RoutingUpdate()
            update.add_destination(packet.src, packet.latency)
            self.send(update, port, flood = True)


        #Ping packet
        if(isinstance(packet, Ping)):
            if packet.dst is NullAddress:
                  # Silently drop messages not to anyone in particular
                 print("packet.dst was NullAddress so returning")
                 return
            if packet.dst is not self:
              self.log("NOT FOR ME: %s %s" % (packet, trace), level="WARNING")
              self.send(packet, port, flood = True)
            else:
              self.log("IS FOR ME: %s %s" % (packet, trace))
              if type(packet) is Ping:
                # Send a pong response
                self.send(Pong(packet), port)




















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
