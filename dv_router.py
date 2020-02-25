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

            if len(packet.all_dests()) > 1:
                print("received a big packet")

            #Update our forw_table
            for i in packet.all_dests():

                #first we check if we received this because link is severed
                if packet.get_distance(i) == float("inf"):
                    print(str(self) + "received that link is severed at" + str(i))
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

                        #Now, we don't trust that anything we go through i wouldn't loop us back
                        # for r in self.forw_table:
                        #     if self.forw_table[r][1] == i: #if the next_hop to a router is the one we don't have a link with
                        #         self.forw_table[r][1] = None #we no longer have a next hop

                    else:
                        # print(str(self) + "is changing to inf its path to" + str(i))
                        if self.forw_table[i][2] != float("inf"):
                            self.forw_table[i][2] = float("inf")
                            # for r in self.forw_table:
                            #     if self.forw_table[r][1] == i: #if your next hop is i
                            #         # self.forw_table[r][1] = None #remove it as a next_hop
                            #         self.forw_table[r][2] = float("inf") #you no longer have a path to it
                            update = RoutingUpdate()
                            update.add_destination(i,float("inf"))
                            self.send(update, port, flood = True)
                            #else DROP IT DAMN IT

                else:

                    updates_to_flood = {} #To be fair... all packets contain only 1 update each

                    #if dest not in our forwarding table, add it with + 1
                    if i not in self.forw_table:
                        self.forw_table[i] = array([None, packet.src, packet.get_distance(i) + 1]) # plus 1 cause flooded by neighbour
                        update = RoutingUpdate()
                        update.add_destination(i, packet.get_distance(i) + 1)
                        self.send(update, port, flood = True)


                    #if it is in forw_table, add it if the path + 1 is shorter
                    else:
                        if packet.get_distance(i) == -1:
                            if self.forw_table[i][1] != None and self.forw_table[i][2] != float("inf"): #we received a message from a neighbour with no path
                                print(str(self) + "received ask for help from " + str(packet.src) + " and is sending path to " + str(i))
                                update = RoutingUpdate()
                                update.add_destination(i, self.forw_table[i][2])
                                self.send(update, port, flood = False)
                        else:
                            if self.forw_table[i][2] > (packet.get_distance(i) + 1) or self.forw_table[i][1] == None:

                                og_infinity = self.forw_table[i][2] == float("inf") #originally inifinity?

                                if og_infinity:
                                    print(str(self) + " route to " + str(i) + "from inf to a finite path")
                                    if self.forw_table[i][1] == None: #if it's our original neighbour who's link we lost
                                        print(str(self) + " found a path to " + str(i) + " with whom the link was severed.")
                                        self.forw_table[i][2] = packet.get_distance(i) + 1 #update distance
                                        self.forw_table[i][1] = packet.src #update next_hop

                                        #now that we have updated the next_hop to be the source of the packet (one of our neighbours)
                                        #we need to make sure that neighbour knows so that we don't create a loop

                                        #test what kind of data does a ping message hold
                                        #let it just be a list of all routers towards which the next_hop is the packet.src
                                        data = {
                                            "Kind of message": "Don't route through me!",
                                            "Data": []
                                        }

                                        update = RoutingUpdate()
                                        update.add_destination(i, packet.get_distance(i) + 1)

                                        for r in self.forw_table: #update all router who's next hop was the router we lost the link with
                                            if self.forw_table[r][1] == None and r != self:
                                                data["Data"].append(r)
                                                update.add_destination(i, self.forw_table[r][2] + packet.get_distance(i))
                                                self.forw_table[r][1] = packet.src
                                                self.forw_table[r][2] = self.forw_table[r][2] + packet.get_distance(i)
                                        print("printing the forwarding table sent after a we found a path to a lost router " + str(self.forw_table))
                                        self.send(update, port, flood = True) #don't flood it to port, because that's just going to create a loop

                                        self.send(Ping(packet.src, data = data), port = port, flood = False)
                                    else:
                                        self.forw_table[i][2] = packet.get_distance(i) + 1 #update distance
                                        self.forw_table[i][1] = packet.src #update next_hop
                                else:
                                    # if self.forw_table[i][1] == packet.src:
                                    #     print()
                                    # else:
                                    self.forw_table[i][2] = packet.get_distance(i) + 1 #update distance
                                    self.forw_table[i][1] = packet.src #update next_hop
                                update = RoutingUpdate()
                                update.add_destination(i, packet.get_distance(i) + 1)
                                self.send(update, port, flood = True)
            print(self.forw_table)
            print("\n")


        #DiscoveryPacket packet
        if(isinstance(packet, DiscoveryPacket)):
            if packet.src not in self.forw_table:
                print(str(self) + " received a DiscoveryPacket from " + str(packet.src))
                print(self.forw_table)
                print("\n")
                self.forw_table[packet.src] = array([port, packet.src, packet.latency])
                update = RoutingUpdate()
                update.add_destination(packet.src, packet.latency)
                # print(str(self) + " is about to flood a DiscoverPacket sent from " + str(packet.src))
                self.send(update, port, flood = True)
            if packet.is_link_up == False:
                print(str(self) + " just received a severed link packet from " + str(packet.src))
                self.forw_table[packet.src][2] = float("inf") #update your link distance to the router
                self.forw_table[packet.src][1] = None #update the next_hop - it's not that anymore
                for r in self.forw_table:
                    if self.forw_table[r][1] == packet.src: #if the next_hop to a router is the one we don't have a link with
                        self.forw_table[r][1] = None #we no longer have a next hop
                        # self.forw_table[r][2] = float("inf") #we no longer have a path to it
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
            try:
                if self.forw_table[self.forw_table[packet.dst][1]][2] == float("inf"):
                    #If next hop of the path is unreachable, we drop the packet
                    return
            except:
                print(str(self) + " doesn't have a next_hop to " + str(packet.dst))
            if packet.dst is not self:
                  next_hop = self.forw_table[packet.dst][1]
                  next_port = self.forw_table[next_hop][0]
                  self.send(packet, next_port, flood = False)
            else: #packet.dst is self
                print("a ping from " + str(packet.src) + " to " + str(self) + " has been received with data " + str(packet.data))
                if packet.data["Kind of message"] == "Don't route through me!":
                    print("packet.data[Data] is ")
                    print(packet.data["Data"])
                    routers_to_update = packet.data["Data"]
                    ask_for_path = RoutingUpdate()
                    for r in routers_to_update:
                        if self.forw_table[r][1] == packet.src and r != packet.src:
                            self.forw_table[r][1] = None
                            ask_for_path.add_destination(r, -1)
                    if len(ask_for_path.all_dests()) > 0:
                        self.send(ask_for_path, port, flood = True)
                    print("ask_for_path.all_dests() is ")
                    print(ask_for_path.all_dests())
                    print(self.forw_table)
                    print("\n")


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
