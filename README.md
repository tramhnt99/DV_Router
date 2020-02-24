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
  **TODO**
  * Addition to solution: say router A and B had a link and it was severed, when router A receives an update on how to reach B, anything beyond that is just whatever it was original (...) + this new path.
  * **new change** If RoutingUpdate packet is received as a result of a severed link, but the router that received it is a neighbour with an existing link to the router with a severed link, it will send only the paths that don't go throguh the neighbour AND update as well (anything that goes through the severed link = inf). 
  
  
*23.02.20*
 * Updates:
  * Another problem with implementation is that when we can't differentiate if something is unreachable (like h1b), or it is now unreachable because it's next hop was compromised. This also prevents messages from links that are severed from propagating. e.g. s2 received that link with s3 is severed, so now h1b is unreachable (distance = inf). next time it receives a message h1b is unreachable (ie. = inf), it won't propagate it cause it's already = inf.
  * Solution: Say link with router A is severed, don't switch all routers who's next hop is A to inf. Change the way you reach them - ie. if their next hop is reachable we assume the router is reachable. (this just means that we edit how the packets are forwarded - ie. ping function).
  * Now we have routers that are "unreachable" cause its next_hop is unreachable. Solution: When we find a path to that router A who's link we lost, anything that has router A as next hop - we update distance to og path from Router A + distance to router A, and next_hop to next_hop of router A. worked!
  * Next problem: neihbour's next_hops are never fixed. basically say s3 and s2 are linked, then the link is lost, s1, who would want to reach s6 (for eg.), would take the path s3, s2, s6. But that can't happen. the thing is, the distance is incorrect but the message would still reach.
  * Another problem: s2 and s3 link is severed. for s1 to get to s2, originally it would go s1, s3, s2. now, it's next_hop is still s_3 but it can't get to s2 -> we'll get a loop **Problem 1**
 
 
 *24.02.20*
 * Who has correct data on who:
  * Routers who's links are lost have updated data around the whole network
 * Update:
  * When a router receives a severed link, anything that has it as the next_hop, next_hop = None. Thus, when it receives an update on a router, a path towards which next_hop == None, we update it.
 * Intution on fixing problem 1: When a router receives that a neighbour's link is corrupted, if the neighbour is the next_hop, put next_hop as None until further notice. (am running this first to see if it converges)
 * Continuing to fix problem 1: Currently, say the link between s7 and s6 is severed, once s7 finds a path to s6, it floods to its neighbours all the "new" paths to routers where s6 was the next_hop. But, we should flood all the paths it knows, so that anything that the router knows which paths through s7 are still there.
 * ok so, that might've been stupid. New solution to problem 1.
 
 * Say link between s3 and s2 is lost, s3 floods that s2 is inf to s1. s1 *pings* s4 on all the routers it might not be able to reach through s4, and s4 sends a 

