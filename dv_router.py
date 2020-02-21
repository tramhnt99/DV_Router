from sim.api import *
from sim.basics import *
from numpy import array

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        #forw_table is a dictionary of keys are the entities, and values are arrays of
        #port to entity (can be None), next_hop (can be None), and distance to entity
        self.forw_table = {
            self : array([None, None, 0])
        }
        #We need to flood a DiscoveryPacket of ourselves
        #We are flooding it to our neighbours, so link latency is 1
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
                #self.forw_table[i][2] is the 2nd element in array value (which is the distance to entity)
                if i not in self.forw_table:
                    assert packet.dst == NullAddress #sanity check that it's flooded by neighbour
                    self.forw_table[i] = array([None, packet.src, packet.get_distance(i) + 1]) #1 because this packet is received from neighbour
                    update = RoutingUpdate()
                    for i in updates_to_flood:
                        update.add_destination(i, updates_to_flood[i])
                    self.send(update, port, flood = True)
                    print(self.forw_table)

                #if it is in forw_table, and the link has been broken or no path to get there
                else:
                    if packet.dst == NullAddress:
                        if(self.forw_table[i][2] > packet.get_distance(i) + 1):
                            self.forw_table[i][2] = packet.get_distance(i) + 1 #update distance
                            self.forw_table[i][1] = packet.src #update next_hop
                            updates_to_flood[i] = packet.get_distance(i) + 1
                            #We flood our update to the network only when we found a shorter path
                            update = RoutingUpdate()
                            for i in updates_to_flood:
                                update.add_destination(i, updates_to_flood[i])
                            self.send(update, port, flood = True)


#CODE FOR updating a shorter path when received a specific RoutingUpdate pack

                    # if (packet.get_distance(i) == float("inf")):
                    #     self.forw_table[i][2] = float("inf")
                    # else:
                    #     #if it is in forw_table, add it if the path + distance to router is shorter
                    #     if(self.forw_table[i][2] > packet.get_distance(i) + self.forw_table[packet.src][2]):
                    #         self.forw_table[i][2] = packet.get_distance(i) + self.forw_table[packet.src][2] #update distance
                    #         self.forw_table[i][1] = packet.src #update next_hop
                            # #send this update to EVERYONE in the network
                            # for entities in self.forw_table:
                            #     if self.forw_table[entities][2] == float("inf"):
                            #         return #drop the packet
                            #     else:
                            #         next_hop = self.forw_table[packet.dst][1]
                            #         next_port = self.forw_table[next_hop][0]
                            #         self.send(packet, next_port, flood = False)




        #DiscoveryPacket packet
        #ASSUMING DiscoveryPacket is ONLY sent to us from our neighbours (ie flood only floods to neighbours)
        if(isinstance(packet, DiscoveryPacket)):
            if packet.src not in self.forw_table:
                self.forw_table[packet.src] = array([port, packet.src, packet.latency])
            update = RoutingUpdate()
            update.add_destination(packet.src, packet.latency)
            self.send(update, port, flood = True)


        #Ping packet
        if(isinstance(packet, Ping)):
            if packet.dst is NullAddress:
                 # Silently drop packet
                 return
            if packet.dst is not self:
                print("Ping received at" + str(self))
                next_hop = self.forw_table[packet.dst][1]
                next_port = self.forw_table[next_hop][0]
                self.send(packet, next_port, flood = False)
              # Assume that Ping is never sent to a router


        #Pong packet
        if(isinstance(packet, Pong)):
            if packet.dst is NullAddress:
                return
            if packet.dst is not self:
                self.log("NOT FOR ME: %s %s" % (packet, trace), level="WARNING")
                pong_dst = packet.original.src
                next_hop = self.forw_table[pong_dst][1]
                next_port = self.forw_table[next_hop][0]
                self.send(packet, next_port)
            else:
                self.log("IS FOR ME: %s %s" % (packet, trace))




















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
