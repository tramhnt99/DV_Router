# ComupterNetworks_Project1

**Project 1**

*15.02.20*
* Passed compatibility test
  * forw_table is a dictionary of Entity and distance
  * handle_rx handles packet RoutingUpdate packets
  
*18.02.20*
* When a DVRouter instance is created, it:
  * create a forw_table
  * floods a DiscoveryPakcet of itself (**wrong because the latency of link would not change**)
  * handle_rx handles packets:
    * RoutingUpdate: if distance found to an Entity doesn't exist, add to forwarding table. OR, if it does exist but RoutingUPdate is advertising a *shorter* path, also update the forwarding table
    * DiscoveryPacket: if it's not in the forw_table, update it. Create a RoutingUpdate packet and flood it
    * Ping: currently just floods it
    
*19.02.20*
* Updated:
 * forw_table to contain ports, next_hop, and distance to an Entity
 * When a router receives a RoutingUpdate, we edit next_hop and distance to the router's forwarding table
 * When a router received DiscoverPacket, it fills in the port number of the neighbouring router
 * Using port and next_hop information, I can now forward Ping messages

*21.02.20*
 * TODO: implement poisoned reverse. Eg. say we're x, and to get to z, we route through y. Then, we have to advertise to y that x's path to z is infinity.
 * Update
  * We are not longer flooding new RoutingUpdates, but rather forwarding the ones we received
 

