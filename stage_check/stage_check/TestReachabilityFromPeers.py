###############################################################################
#  _____         _   ____                 _           _     _ _ _ _         
# |_   _|__  ___| |_|  _ \ ___  __ _  ___| |__   __ _| |__ (_) (_) |_ _   _ 
#   | |/ _ \/ __| __| |_) / _ \/ _` |/ __| '_ \ / _` | '_ \| | | | __| | | |
#   | |  __/\__ \ |_|  _ <  __/ (_| | (__| | | | (_| | |_) | | | | |_| |_| |
#   |_|\___||___/\__|_| \_\___|\__,_|\___|_| |_|\__,_|_.__/|_|_|_|\__|\__, |
#                                                                     |___/ 
#  _____                    ____                                  
# |  ___| __ ___  _ __ ___ |  _ \ ___  ___ _ __ ___   _ __  _   _ 
# | |_ | '__/ _ \| '_ ` _ \| |_) / _ \/ _ \ '__/ __| | '_ \| | | |
# |  _|| | | (_) | | | | | |  __/  __/  __/ |  \__ \_| |_) | |_| |
# |_|  |_|  \___/|_| |_| |_|_|   \___|\___|_|  |___(_) .__/ \__, |
#                                                    |_|    |___/ 
###############################################################################
import pprint

try:
    from stage_check import gql_helper
except ImportError:
    import gql_helper

try:
    from stage_check import AbstractTest
except ImportError:
    import AbstractTest

try:
    from stage_check import Output
except ImportError:
    import Output

try:
    from stage_check import RouterContext
except ImportError:
    import RouterContext

try:
    from stage_check import EntryTester
except ImportError:
    import EntryTester



def create_instance(test_id, config, args):
    """
    Invoked by TestExecutor class to create a test instance
   
    @test_id - test index number
    @config  - test parameters from, config 
    @args    - command line args
    """
    return TestReachabilityFromPeers(test_id, config, args)


class TestReachabilityFromPeers(AbstractTest.GraphQL):
    """
    """
    def __init__(self, test_id, config, args):
        super().__init__(test_id, config, args)

    def requires_grapqhl(self):
        """
        Override
        """
        return True

    def get_params(self):
        """
        expected_entries shoudl fail schema validation if
        missing from the parameters
        """
        default_params = {
            "peer_header"         : "Peer {allRouters/name}.{node}",
            "display_max_paths"   : 0,
            "exclude_tests"       : []
         }

        params = self.apply_default_params(default_params)
        return params

    def query_peer_config(
            self, 
            router_context, 
            gql_token, 
            peer_routers
        ):
        if not isinstance(peer_routers, list):
            raise TypeError
        if router_context.local_role != "conductor":
            return False
        peer_routers.clear()
        qr = gql_helper.NewGQL(
            api_name="allRouters",
            api_args={"name" : router_context.get_router()},
            api_fields=[ "name" ],
            api_has_edges=True,
            debug=self.debug
        )
        qp = gql_helper.NewGQL(
            api_name="peers",
            api_args={},
            api_fields=[ "name", "routerName" ],
            api_has_edges=True,
            debug=self.debug
        )
        qr.add_node(qp)

        """
        json_reply={}
        if not self.send_query(qr, gql_token, json_reply):
            return self.output.test_end(fp)
     
        flatter_json = qr.flatten_json(json_reply, 'allRouters/peers')
        """

        flatter_json = []
        qr.api_flat_key = "allRouters/peers"
        if not self.send_query(qr, gql_token, flatter_json):
            return self.output.test_end(fp)        
        router_context.set_allRouters_node_type(flatter_json, 'node')
        if self.debug:
            print('........ flattened list ..........')
            pprint.pprint(flatter_json)        

        peers = flatter_json
        for peer in peers:
            peer_router = peer['routerName']
            if not peer_router in peer_routers:
                peer_routers.append(peer_router)

    def query_remote_path_states(
            self, 
            router_context, 
            gql_token, 
            peer_routers, 
            remote_peers_status
        ):
        """
        Iterate over all peers of this router and collect the remote view of peer states
        This must be run on a conductor as routers do not have visibility into the state
        of other routers.

        router_context      - IN: This router
        gql_token           - IN: GraphQL access token
        peer_routers        - IN: List of adjacent routers
        remote_peers_status - IN/OUT: Dictionary of remote peer path status
        """
        type_name = router_context.__class__.__module__ + '.' + router_context.__class__.__qualname__
        if not type_name.endswith('RouterContext.Base'):
            print(f"router_Context has type '{type_name}', expecting 'RouterContext.Base'!")
            raise TypeError
        if not isinstance(peer_routers, list):
            raise TypeError
        if not isinstance(remote_peers_status, list):
            raise TypeError

        if router_context.local_role != "conductor":
            return status.WARN, "Must be run from conductor!" 

        remote_peers_status.clear()
        qr = gql_helper.NewGQL(
            api_name="allRouters",
            api_args={"names" : peer_routers},
            api_fields=[ "name" ],
            api_has_edges=True,
            debug=self.debug
            )
        qp = gql_helper.NewGQL(
            api_name="peers",
            api_args={},
            api_fields=[ "name", "routerName", "paths { node adjacentNode deviceInterface networkInterface adjacentAddress status }" ],
            api_has_edges=True,
            debug=self.debug
            )
        qr.add_node(qp)
    
        """
        json_reply={}
        query_status = self.send_query(qr, gql_token, json_reply)
        flatter_json = qr.flatten_json(json_reply, 'allRouters/peers/paths')

        if self.debug:
            print('........ flattened list ..........')
            pprint.pprint(flatter_json)

        if not query_status and \
           len(flatter_json) == 0:
           return Output.Status.FAIL, "GraphQL Query Failed!"
        """
        flatter_json = []
        qr.api_flat_key = "allRouters/peers/paths"
        if not self.send_query(qr, gql_token, flatter_json):
           return Output.Status.FAIL, "GraphQL Query Failed!"
        router_context.set_allRouters_node_type(flatter_json, 'node')
        
        for path in flatter_json:
            remote_router = path["allRouters/peers/routerName"]
            if router_context.get_router() != remote_router:
                continue
            remote_peers_status.append(path)

        if self.debug:
            print('\n........ Paths to this router only ..........')
            pprint.pprint(remote_peers_status)
              
        return Output.Status.OK, ""

    def run(self, local_info, router_context, gql_token, fp):
        """
        This test uses the gql engine to get peer reachability status about this
        router_context from the perspective of it's peers.
  
        The raison d'etre for this test is to determine if this node is alive or
        more specifically sending BFD messages to its peers.  If any path is 
        functional the test should pass, but simply the status of related peer paths
        is also of interest.
        """
        test_info = self.test_info(local_info, router_context)
        self.output.test_start(test_info)
        params = self.get_params()
      
        exclusions    = params["exclude_tests"]
        entry_tests   = params["entry_tests"]

        stats = self.init_stats()
        Output.init_result_stats(stats)

        if router_context.local_role != "conductor":
            self.output.unsupported_exec_node(local_info)
            return self.output.test_end(fp)

        peer_routers = []
        remote_peer_paths = []
        status = self.query_peer_config(router_context, gql_token, peer_routers)
        if status == Output.Status.WARN:
            self.output.unsupported_exec_node(local_info)
            return self.output.test_end(fp)
        if status == Output.Status.FAIL:
            return self.output.test_end(fp)

        if len(peer_routers) == 0: 
            self.output.proc_no_peers()
            return self.output.test_end(fp)

        # assert False, "remote peers: " + pprint.pformat(peer_routers)
          
        status, message = self.query_remote_path_states(
            router_context, 
            gql_token, 
            peer_routers, 
            remote_peer_paths
            )
        if status != Output.Status.OK and \
            len(remote_peer_paths) == 0:
            return self.output.test_end(fp)

        # assert False, "remote paths: " + pprint.pformat(remote_peer_paths)

        remote_router_stats = {}
        engine = EntryTester.Parser(debug=self.debug)
        for path in remote_peer_paths:
            if engine.exclude_entry(path, exclusions):
                stats["exclude_count"] += 1
                continue
            test_result = engine.eval_entry_by_tests(
                path,
                entry_tests
             )
            #path["/allRouters/name"],
            Output.update_stats(stats, test_result, inc_total=True)
            Output.update_stats_by_key(
                remote_router_stats, 
                path["allRouters/name"],
                test_result
            )
            self.output.proc_path_result(test_result, path, params)

        # assert False, "stats: " + pprint.pformat(stats)

        # create stats[router_OK], stats[router_FAIL]....
        Output.apply_stats_by_key(stats, remote_router_stats, "router")
        status = Output.Status.OK
        if stats["FAIL"] > 0:
            status = Output.Status.FAIL
          
        self.output.proc_test_result(entry_tests, stats)
        return self.output.test_end(fp)


