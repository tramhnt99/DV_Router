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

                #first we check if we received this because link is severed
                if packet.get_distance(i) == float("inf"):
                    self.forw_table[i][2] = float("inf")
                    self.send(packet, port, flood = True)
                else:
                    #if dest not in our forwarding table, add it with + 1
                    if i not in self.forw_table:
                        assert packet.dst == NullAddress, "It should only be added to table if flooded by neighbour"
                        self.forw_table[i] = array([None, packet.src, packet.get_distance(i) + 1]) # plus 1 cause flooded by neighbour
                        updates_to_flood[i] = packet.get_distance(i) + 1
                        #We flood our update to the network only when it's a newly discovered entity
                        update = RoutingUpdate()
                        for i in updates_to_flood:
                            update.add_destination(i, updates_to_flood[i]) #DO WE NEED THIS???
                        self.send(update, port, flood = True)
                        # print(self.forw_table)

                    #if it is in forw_table, add it if the path + 1 is shorter
                    else:
                        if packet.dst == NullAddress:
                            #This is only for convergence when all routers are created
                            if(self.forw_table[i][2] > packet.get_distance(i) + 1):
                                self.forw_table[i][2] = packet.get_distance(i) + 1 #update distance
                                self.forw_table[i][1] = packet.src #update next_hop
                                updates_to_flood[i] = packet.get_distance(i) + 1
                                #We flood our update to the network only when we found a shorter path
                                update = RoutingUpdate()
                                for i in updates_to_flood:
                                    update.add_destination(i, updates_to_flood[i])
                                self.send(update, port, flood = True)


        #DiscoveryPacket packet
        if(isinstance(packet, DiscoveryPacket)):
            if packet.src not in self.forw_table:
                self.forw_table[packet.src] = array([port, packet.src, packet.latency])
                update = RoutingUpdate()
                update.add_destination(packet.src, packet.latency)
                self.send(update, port, flood = True)
            if packet.is_link_up == False:
                update = RoutingUpdate()
                update.add_destination(packet.src, packet.latency)
                self.send(update, port, floor = True)


        #Ping packet
        if(isinstance(packet, Ping)):
            if packet.dst is NullAddress:
                 # Silently drop packet
                 return
            if packet.dst is not self:
              # self.log("NOT FOR ME: %s %s" % (packet, trace), level="WARNING")
              next_hop = self.forw_table[packet.dst][1]
              next_port = self.forw_table[next_hop][0]
              self.send(packet, next_port, flood = False)
              # No host will send ping to router


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
