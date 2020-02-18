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
* Uppdated:
 * forw_table to contain ports 
* TODO: 
  * Update forw_table to contain ports to an Entity, and next_hop to get to the entity, and the distance to it
  * Update handle_rx at RoutingUpdate: fills in next_hop (from packet.paths), and distance
  * Update handle_rx at DiscoveryPacket: fills in port
  * Using this updated architecture, update response to Ping messages and forward messages

