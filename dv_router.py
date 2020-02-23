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
        self.send(discover, flood = True)


    def handle_rx (self, packet, port):

        #Logging
        trace = ','.join((s.name for s in packet.trace))

        # if packet.dst is not self:
        #   self.log("NOT FOR ME: %s %s" % (packet, trace), level="WARNING")
        # else:
        #   self.log("rx: %s %s" % (packet, trace))

        #Dealing with packets

        #RoutingUpdate packet
        if(isinstance(packet,RoutingUpdate)):

            all = {}
            for k in packet.all_dests():
                all[k] = packet.get_distance(k)
            print(str(self) + "received a RoutingUpdate packet from " + str(packet.src) + " with updates on " + str(all))

            #Update our forw_table
            for i in packet.all_dests():

                #first we check if we received this because link is severed
                if packet.get_distance(i) == float("inf"):
                    # print(str(self) + "received that link is severed at" + str(i))
                    if self.forw_table[i][2] == 1: #if the router with severed link is our neighbour
                        print(str(self) + " is neighbour to " + str(i) + "and flooding that everywhere")
                        update = RoutingUpdate()
                        update.add_destination(i, 1)
                        neighbour_port = self.forw_table[i][0]
                        self.send(update, neighbour_port, flood = True) #send to all neighbours even who sent the og packet, other than who's link was severed

                        update_neighbour = RoutingUpdate() #send to neighbour your own connections
                        for r in self.forw_table:
                            if r != i and r != self:
                                if self.forw_table[r][1] != i: #next hop cannot! be the neighbour router
                                    update_neighbour.add_destination(r, self.forw_table[r][2])
                        self.send(update_neighbour, neighbour_port, flood = False)

                    else:
                        print(str(self) + "is changing to inf its path to" + str(i))
                        if self.forw_table[i][2] != float("inf"):
                            self.forw_table[i][2] = float("inf")
                            for r in self.forw_table:
                                if self.forw_table[r][1] == i: #if your next hop is i
                                    # self.forw_table[r][1] = None #remove it as a next_hop
                                    self.forw_table[r][2] = float("inf") #you no longer have a path to it
                            update = RoutingUpdate()
                            update.add_destination(i,float("inf"))
                            self.send(update, port, flood = True)
                            #else DROP IT DAMN IT

                else:

                    updates_to_flood = {} #To be fair... all packets contain only 1 update each

                    #if dest not in our forwarding table, add it with + 1
                    if i not in self.forw_table:
                        assert packet.dst == NullAddress, "It should only be added to table if flooded by neighbour"
                        self.forw_table[i] = array([None, packet.src, packet.get_distance(i) + 1]) # plus 1 cause flooded by neighbour
                        updates_to_flood[i] = packet.get_distance(i) + 1

                    #if it is in forw_table, add it if the path + 1 is shorter
                    else:
                        if packet.dst == NullAddress:
                            if(self.forw_table[i][2] > packet.get_distance(i) + 1):
                                # if self.forw_table[i][2] == float("inf"):
                                #     print("We're updating the inf at " + str(self) + "for " + str(i))
                                og_infinity = self.forw_table[i][2] == float("inf") #originally inifinity?
                                self.forw_table[i][2] = packet.get_distance(i) + 1 #update distance
                                self.forw_table[i][1] = packet.src #update next_hop
                                if og_infinity:
                                    updates_to_flood[i] = packet.get_distance(i) + 1

                    #We flood our update to the network only when it's a newly discovered entity or we found shorter path
                    update = RoutingUpdate()
                    if updates_to_flood: #if the dictionary is not empty
                        for i in updates_to_flood:
                            update.add_destination(i, updates_to_flood[i])
                        self.send(update, port, flood = True)
            print(self.forw_table)
            print("\n")


        #DiscoveryPacket packet
        if(isinstance(packet, DiscoveryPacket)):
            if packet.src not in self.forw_table:
                self.forw_table[packet.src] = array([port, packet.src, packet.latency])
                update = RoutingUpdate()
                update.add_destination(packet.src, packet.latency)
                # print(str(self) + " is about to flood a DiscoverPacket sent from " + str(packet.src))
                self.send(update, port, flood = True)
            if packet.is_link_up == False:
                print(str(self) + " just received a severed link packet from " + str(packet.src))
                self.forw_table[packet.src][2] = float("inf") #update your link distance to the router
                for r in self.forw_table:
                    if self.forw_table[r][1] == packet.src: #if the next_hop to a router is the one we don't have a link with
                        # self.forw_table[r][1] = None #we no longer have a next hop
                        self.forw_table[r][2] = float("inf") #we no longer have a path to it
                update = RoutingUpdate()
                update.add_destination(packet.src, float("inf"))
                self.send(update, port, flood = True)

                # for i in self.forw_table:
                #     if self.forw_table[i][0] != None:
                #         if self.forw_table[i][2] != float("inf"):
                #             print(str(self) + "is sending severed link Discovery packet to" + str(i) + "at port" + str(self.forw_table[i][0]))
                #             update = RoutingUpdate()
                #             update.add_destination(packet.src, float("inf"))
                #             self.send(update, self.forw_table[i][0])

                            #only send to neighbours who's link is not severed


        #Ping packet
        if(isinstance(packet, Ping)):
            if packet.dst is NullAddress:
                 # Silently drop packet
                 return
            if self.forw_table[packet.dst][2] == float("inf"):
                #Drop packet cause we can't reach there
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
            if self.forw_table[packet.dst][2] == float("inf"):
                return
            if packet.dst is not self:
                self.log("NOT FOR ME: %s %s" % (packet, trace), level="WARNING")
                pong_dst = packet.original.src
                next_hop = self.forw_table[pong_dst][1]
                next_port = self.forw_table[next_hop][0]
                self.send(packet, next_port)
            else:
                self.log("IS FOR ME: %s %s" % (packet, trace))
