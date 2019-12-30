"""
"""
import json
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
    return TestProcessStates(test_id, config, args)


class TestProcessStates(AbstractTest.GraphQL):
  """
  """
  QUERY = """
  {
  allRouters(name: "{{ router }}") {
    edges {
      node {
        name
        nodes {
          edges {
            node {
             name
              state {
                processes {
                  name
                  processName
                  status
                  primary
                  leaderStatus
                }
              }
            }
          }
        }
      }
    }
  }
  }
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
         "test_value"    : "UP",
         "test_equality" : True,
         "exclude_tests" : [],
         "include_list"  : []
      }

      params = self.apply_default_params(default_params)
      return params

  def add_entry_peer_data(
      self, 
      router_context,
      results_list, 
      primary_key, 
      secondary_key='node_type',  
      seperator='/'
      ):
      """
      For each entry with another entry having the same primary_key value, 
      each of this entry's peer_{key} values are populated with the other's
      key value, including multi-segment keys.

      [ 
          { 
              "primary_key"   : "fubar",
              "secondary_key" : "primary",
              "key1"          : value1, 
              "/snafu/key2"   : value2 
          },
          { 
              "primary_key"   : "fubar",
              "secondary_key" : "secondary",
              "key1"          : value3, 
              "/snafu/key2"   : value4 
          }
      ]

      becomes:

      [ 
          { 
              "primary_key"           : "fubar",
              "secondary_key"         : "primary",
              "peer_secondary_key"    : "secondary",
              "key1"                  : value1, 
              "/snafu/key2"           : value2,
              "peer_key1"             : value3,
              "/snafu/key2/peer_key2" : value4 
          },
          { 
              "primary_key"           : "fubar",
              "secondary_key"         : "secondary",
              "peer_secondary_key"    : "primary",
              "key1"                  : value3, 
              "/snafu/key2"           : value4,
              "peer_key1"             : value1,
              "/snafu/key2/peer_key2" : value2  
          }
      ]
 
      This allows test criteris to use peer values in the context of the current entry:
           @peer_key1 && key1 != 'RUNNING' && peer_key1 != 'RUNNING'

      TODO: move to AbstractTest, so that any test can use this if needed:
      """
      router_context.set_allRouters_node_type(results_list)
      return

      data_map = {}
      data_key_list = {}
      for entry in results_list:
          primary_value = entry[primary_key]
          if not primary_value in data_map:
              data_map[primary_value] = {}
              data_key_list[primary_value] = []
          secondary_value = entry[secondary_key]
          data_map[primary_value][secondary_value] = entry
          data_key_list[primary_value].append(secondary_value)

      #assert False, "DATA_KEY_LIST:\n" + json.dumps(data_key_list, indent=2)

      entries_updated = 0
      for primary_value in data_map:
          if len(data_key_list) > 1:
              index = 0
              while index < len(data_key_list[primary_value]):
                  peer_index = (index + 1) % 2 
                  key = data_key_list[primary_value][index]
                  peer_key = data_key_list[primary_value][peer_index]
                  entry = data_map[primary_value][key]
                  peer_entry = data_map[primary_value][peer_key] 
                  #assert False, "PEER ENTRIES:\n" + json.dumps(entry, indent=2) + "\n" + json.dumps(peer_entry, indent=2)
                  new_fields={}
                  for key in entry:
                      if key == primary_key:
                          continue
                      key_elements = key.split(seperator)
                      key_elements[-1] = 'peer_' + key_elements[-1]
                      peer_key = seperator.join(key_elements)
                      if len(key_elements) > 1 and key[0] != seperator:
                          peer_key = seperator + peer_key  
                      new_fields[peer_key] = peer_entry[key]
                  entry.update(new_fields)
                  entries_updated += 1 
                  index += 1

      #assert False, "PEERIFIED:\n" + json.dumps(results_list, indent=2)

      if self.debug:
          if entries_updated > 0:
              print(f"--- Start Entries with Peer Values Added ---", flush=True)
              print(f"{json.dumps(results_list, indent=2)}", flush=True) 
              print(f"--- End Entries with Peer Values Added ---", flush=True)
          else:
              print(f"--- No Entries with Peer Values Added ---", flush=True)
                    
  def run(self, local_info, router_context, gql_token, fp):
      test_info = self.test_info(local_info, router_context)
      self.output.test_start(test_info)
      params = self.get_params()
      exclusions    = params["exclude_tests"]
      entry_tests   = params["entry_tests"]

      stats = self.init_stats()
      Output.init_result_stats(stats)

      variables = { 
         "router" : router_context.name
      }
      qr = gql_helper.GQLTemplate(
          template_text=TestProcessStates.QUERY,
          variables=variables,
          flatpath="/allRouters/nodes/state/processes",
          debug=self.debug
      )

      flatter_json = []
      if not self.send_query(qr, gql_token, flatter_json):
          return self.output.test_end(fp)

      self.add_entry_peer_data(router_context, flatter_json, 'processName')

      engine = EntryTester.Parser(self.debug)
      for entry in flatter_json:
          try:
              if engine.exclude_entry(entry, exclusions):
                  stats["exclude_count"] += 1
                  continue
              test_result = engine.eval_entry_by_tests(
                  entry,
                  entry_tests
              )
              # assert False, f"RESULT:\n{json.dumps(entry, indent=2)}"
              Output.update_stats(stats, test_result, inc_total=True)
              self.output.proc_interim_result(entry, status=test_result)
          except KeyError:
              pass

      status = Output.Status.OK
      if stats["FAIL"] > 0:
          status = Output.Status.FAIL

      self.output.proc_test_result(entry_tests, stats, status=status)
      return self.output.test_end(fp)


