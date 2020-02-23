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
  
*22.02.20*
 * Updates:
  * When DiscoveryPacket received for broken link, it is flooded to all neighbours as a RoutingUpdate packet + we change our distance to that router to infinity, and any routers that are reached via this router - their distances also become inifnity
  * RoutingUpdate packet received as a result of an severed link, if the received is not a neighbour to the router who's link was severed, it changes it's distance to said router to infinity, and any routers that need to reached via this router become "unreachable" - ie. and distance becomes infinity (keep next_hop).
  * If RoutingUpdate packet is received as a result of a severed link, but the router that received it is a neighbour with an existing link to the router with a severed link, it will flood it's own link to all it's neighbours to propagate it.   **changed**(**PROBLEM WITH THIS**, is that some paths it would take to other routers use the said link that was just severed (ie. we need to use poison reverse or split horizon)
  * Possible solution: from the neighbour_router next hop to a router is the router with the severed link, then don't advertise that (cause LOOP DUH)
  * Addition to solution: say router A and B had a link and it was severed, when router A receives an update on how to reach B, anything beyond that is just whatever it was original (...) + this new path.
  * **new change** If RoutingUpdate packet is received as a result of a severed link, but the router that received it is a neighbour with an existing link to the router with a severed link, it will send only the paths that don't go throguh the neighbour AND update as well (anything that goes through the severed link = inf). 
 

