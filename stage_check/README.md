## Introduction

Stage_check is a tool initially developed to determine if a 128 Technology router was 'ready' to be deployed in production.  As such, it replaced the need to perform various "PCLI show" and some Linux shell commands piped through grep expressions, which then required human evaluation to determine if the 'passing' criteria were actually met.

This document has been updated with information for stage_check 2.9.1

When run to generate human-readable output, stage_check outputs information as densely as possible without compromising readability.

```
---------------------------
stage_check version: 1.2.0
---------------------------
Router:    SITE0999 [1/237]
Primary:   SITE0999A (LR227938473948) 4.1.5-3.el7.centos
Secondary: SITE0999B (LR239428347239) 4.1.5-3.el7.centos
Deployment State: Deployed 
-----------------------------------------------------------
0  Check Router Asset(s) State   : PASS  All 2/2 nodes are in state RUNNING
1  NetworkDeviceStatus           : PASS  All required network devices In Service                           
2  Peer Reachability             : PASS  14 paths (6 excluded) to 4 peers avalable
3  Check Inactive Sessions       : PASS  8/8 port 5060 sessions have idle times < 400s (16 processed)
4  Check BGP Routes              : PASS  All 2 BGP peers have >= 10 routes                                         
5  Test node connectivity        : PASS  6 / 6 connections OK
6  Test Gateway Ping             : PASS  NI DIA: 10/10 replies from 192.168.0.1; average latency 1.7e+01ms
7 Test Gateway Ping             : PASS  NI T1: 10/10 replies from 192.168.1.1; average latency 0.75ms
8 Check T1 Details              : FAIL  4 exceptions detected for                                                                 
   :                                     Bit Errors CRC6/Ft/Fs (142923) > 1000
   :                                     Line Code Violation (8387371) > 1000
   :                                     Out of Frame Errors (12907) > 1000
   :                                     Sync Errors (1306) > 1000
   :                                     For more info: ip netns exec t1-ns-5 wanpipemon -i w1g1 -c Ta
9 Check HA interface speed      : PASS  enp0s20f0 speed is 1000Mb/s                                  
10 Check recent crashes          : PASS  SITE0999A:  Uptime OS: 81d 12h 12m   128T: 9d 7h 37m     
11 Check recent crashes          : PASS  SITE0999B:  Uptime OS: 81d 11h 58m   128T: 81d 11h 56m  


```

Since its inception stage_check has evolved into a tool which is driven by a json configuration file.  It now includes the ability to refine the meaning of a test by evaluating configured expressions against the much of the data available to it.  Furthermore, different type of output (human readable text, json) are now supported.

stage_check is written in python and is a self-contained pex file which expands into a dedicated python virtual environment, complete with all of the required modules, on the host it runs on. 

## Usage

| Argument         | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| -R               | Router matching pattern .   Applicable to conductor only.  Allows mulitple routers to be matched, but is most useful for matching a sngle router by a site identifier embedded in the router name.  For example, were the router name SITE2345A, `stage_check.pex -R 2345` would match this router. |
| -c               | Path specifying an alternative config.json file.  By default a configuration file embedded in the stage_check.pex self-contained binary is used.<br><br>Example usage:<br> `stage_check.pex -c /path/to/my_config.json` |
| -d               | Enable debugging output.  This outputs loads of debug information to help with fixing defects or debugging new tests. |
| -o               | Send output to the specfied path.  When this option is specified, stage_check.pex directs its normal text output to the file specified.  Only tests which FAIL are output to stdout.  This option currently hs no meaning when a test's LogStash output module is used.<br><br>Example usage:<br>`stage_check.pex -o /path/to/output_file` |
| -v               | output stage_check version                                   |
| -p               | regular expression to identify the primary node              |
| -s               | regular expression to identify the secondary node            |
| -e               | Exclude test numbers.  Each test invocation defined in the config.json file is assigned an index otput at the beginning of each test's first line before the description field.  This indices can be pased to the -e argument to exclude those tests.<br><br>Example Usage:<br>`stage_check.pex -e 0 2 3 7 9` |
| -r               | Conductor only: Explicit router name (this is rarely used and may soon be deprecated; for this reason no example is given) |
| -n               | Conductor only: Explicit node name (this is rarely used and may soon be deprecated; for this reason no example is given) |
| --regex-patterns | Conductor only:   The argument to the -R option is interpreted as a regex rather than a substring match.<br><br>Example Usage: <br>`stage_check.pex -R SITE2.*5 --regex-patterns` |
| --start-after    | Conductor only: Start pattern matching after the specified pattern.  This is useful when running stage_check against a large list of patterns, or against a pattern matching many routers after the connection has dropped and stage_check was interrupted after running for a period of time.<br><br>Example usage:<br>stage_check -R SITE -- start-after SITE2345A` |
| -g               | Use the generic config.json embedded in the stage_check.pex |

Typical usage:

`stage_check.pex -R 1234`

Note:

stage_check is typically installed as an rpm which includes the pex file plus custom modules and config files.  The repo used for building / staging the rpm is not publically available at this time, so to avoid stage_check.pex looking in the global /etc/stage_check.d directory you can use the -g option to tell stage_check to use the file in this repo located at stage_check/stage_check/config.json and bundled into stage_check.pex, as the config file (Or you can have stage_check use an external config.json by using the -c option, but file will have to be copied onto the target system in addition to stage_check.pex). 

## Configuration

stage_check uses a configuration file named config.json to specify which tests to run with what parameters and in what sequence.  The json content is broken up into three major categories.

### Global Configuration

#### Version 

The version of the config.json file

#### BannerModule                                                                                                                                                                                                                                                                        
The module to use to generate the banner displayed for each router instance the tests are run against.

1. **"BannerText"** - For text output
2. **"BannerNone"** - For simple json output

#### RouterContextModule   

If deployment-specific code needs to be added to get configuration items or state, then the python module is defined here.  An example use case is determining if a router is in a pre-production or production state by examining specific configuration that would be non-existent or meaningless elsewhere.  

Unless a new router context module has been written, set this value to:

1. **"RouterContext"**  - The default module to use for processing router information.                                                                                                                      

#### PrimaryRegex

The Primaryregex is used to differentiate between nodes in an HA router pair.  Stage_check can be run against many different routers for a given deployment,  and the rules used to exclude  from or match data for test failure include specifying which node the test is run against, there must be a generic way to refer to one node versus the other.

The PrimaryRegex is a regular expression which identifies the primary node.   

In the example below, any router's node name ending in 'A' is identified as primary.

```
"PrimaryRegex" : "A$"
```

The identification as primary  would be used in an exclusion or match instance string as follows:

```
node_type == 'primary'
```

or in a test parameter as:   

```
"node_type" : "primary"                                                                                                                                                                                                                                                                 
```

See the section on test-specific parameters for more information on data matching and test parameters

#### SecondaryRegex

This regular expression is used to identify the other (non-primary) node as secondary.         

In the example below, any router's node name ending in 'B' is identified as secondary.

```
"PrimaryRegex" : "B$"
```

The identification as secondary would be used in an exclusion or match instance string as follows:

```
node_type == 'secondary'
```

or in a test parameter as:   

```
"node_type" : "secondary"                                                                                                                                                                                                                                                                 
```

See the section on test-specific parameters for more information on data matching and test parameters                      

#### SkipIfOneNode

Skips this test if the router is comprised of one node only.  Introduced in version 2.0.0, this can be used to implement Linux-based tests which are router node count agnostic.  The default value is false.  Typically used in conjunction with the enhanced node_type to make allow tests to be run even is a node cannot be identified as one of primary,secondary, or solitary.

```
"Tests" : [
    {
        :
        "SkipIfOneNode" : true,
        :
        "Parameters": { 
            :
            "node_type" : "secondary|1"
            :
         }
     }                                                                                                                                                                                                    
```

#### Tests

Each test utilizes both parameters common across tests and those specific the given test module.

Example Global Json Configuration:

```json
{
  "Version"             : "0.0.1",
  "BannerModule"        : "BannerText",
  "RouterContextModule" : "RouterContext",
  "PrimaryRegex"        : "A$",
  "SecondaryRegex"      : "B$",
  "Tests" :  [  
       :
       :
    ]
}
```

### Common Test Parameters

#### TestModule

The test module to execute.  Stage_check python tests are named **Test**+**Name**, so specifying **DeviceState** loads the python module **TestDeviceState.py**.

Some of the entries for this string field include:

1. AssetState
2. DeviceState
3. DeviceNameSpace
4. Ethtool
5. FIB
6. GatewayPing
7. /etc/hosts content
8. Logs
9. LTE Info
10. InterfaceLearnedIP
11. NodeConnectivity
12. PeerReachability
13. RecentCores
14. Service Ping
15. Sessions
16. T1DeviceDetail

Additional tests are actively being developed.

#### OutputModule

Initially `stage_check` only outputs human readable text, but recently there has been interest in various json formats.  Currently 2  values for this string field exist:

1. LogStash
2. Text

#### Description

This unique string field is used to describe the specific test instance.  A test can be run a number of times with different parameters resulting in different aspects of the router node being tested.  The Description makes this clear.

In the text output snippet, below the **Check Router Asset(s) State** text is from description field.

```
0  Check Router Asset(s) State   : PASS  All 2/2 nodes are in state RUNNING
```

#### Example

```json
{
:
:
  "Tests" :  [ 
     {
         "TestModule"   : "AssetState"
         "OutputModule" : "Text"
         "Description"  : "Check Asset(s) State"
         "Parameters"   : {
               :
         }
     } 
       :
       :
    ]
}
```

### Specific Test Parameters

Although efforts are underway to normalize some of the test parameters,  there can still be a great deal of variability between the parameters used for different tests.

Tests generally fall into 2 categories:

1. Collecting one or more json entries, against which exclusion and matching tests can be performed (e.g. DeviceState, AssetState).
2. Purpose built tests, which deviate from the formula of sending a request to get a dataset to process, and then processing it in a fairly standardized fashion (e,g,GatewayPing).

The former tests usually accept parameters as described below.  The latter tests use extremely customized parameters.

#### entry_tests

Each entry in entry tests is evaluated against each entry  (e.g. network-interface, asset, device-interface, peer-path, fib entry, etc.) in the dataset acquired by the test.

##### defaults

Allows the specification of default **format** and **status** values (see tests) so it is not necessary to repeat these fields again and again in the tests section.

Example:

               "defaults" : {
                   "status"  : "FAIL",
                   "format"  : "Node {nodeName} is in state {status}"
               },
Note that {nodeName} and {status} are replaced with corresponding values from the matching dataset entry.

##### tests

The **tests** section of **entry_tests** is comprised of multiple sub-entries.  The **test** field is mandatory,  The **format** and / or **status** fields, if omitted will be obtained from the **defaults** section

###### format

What to display or record if an entry test expression matches (evaluates to true) when applied a data entry returned from a GraphQL or other type of query.  Text enclosed by {}s is treated as a key with which to reference the matching data entry, and is replaced with the corresponding value.

Given an example format:

```
"format" : "device interface {name} is in state {state}"
```

applied to a matching device interface entry:

```
{
    :
   "name" : "DIA",
   "status" : "OPER_UP",
    :
}
```

The resulting text would be output (using the human readable text Output module):

*device interface DIA is in stat OPER_UP*

###### status 

One of:

1. "PASS"
2. "FAIL"
3. "WARN"

###### test

A string expression dynamically evaluated to determine if the current data set entry matches.  The expression uses a simple grammar including field names (which are replaced with the dataset entry under consideration's corresponding value), constants and operators.

Available binary operators include: ==, !=, >, <. ||, &&.  Not all of these operators apply to all data types, and furthermore dataset entry fields are often returned as strings even though they perhaps ought to be interpreted as an integer or a float.  The evaluation engine attempts to coerce strings to integers, if the other side of a binary operation evaluates to an integer.  The same approach is used for floating point values.  Needless to say there are many opportunities for the engine to throw exceptions.

A single unary operator is currently available: ? This can be used to test if a field exists the the dataset before attempting to access its value (which causes an exception if it does not)

string literals are expressed as 'string', and the special tokens True and False are interpreted as boolean literals.

Other words are considered keys or field names in the returned dataset entry.

> **WARNING**: At this time there is no simple way for a person writing an expression to know the full set of valid keys/field names that might be present in a returned dataset entry without detailed inspection of the test code.  This requires further study but since GraphQL queries require that the requested response fields be explicitly requested, this may be one way to validate expression content.  

This expression evaluation facility is still under development, but using it is possible to use expressions like:

```json
"tests" : [
    { 
      "test" : "status != 'RUNNING'",
      "status" : "FAIL"
    }
],
```

to refine what is considered PASS or FAIL for asset entries.  A slightly different spin on this test could be:

```json
`"tests" : [`
    `{` 
      `"test" : "status == 'RUNNING'",`
      `"status" : "PASS"`
    `}`
`],
```

However, it is up to the individual test to decide how a matching entry an its status are processed in the context of multiple dataset entries.  If the test were to declare PASS for all entries because only one entry matched with a status of PASS, that would make the test unreliable.

As previously mentioned this facility is still under study to see how best it might be utilized.

##### result

The result section is used to  define output formatting / messaging for when a test fails, passes, (or results in a warning).  Test statistics are available by enclosing field names (dictionary keys) in {}s.

Each entry has the format:

"<status>" : "<output format string>"

where <status> can be one of:

1. PASS 
2. FAIL
3. WARN

Below is an example entry:

```
"PASS"  : "All {non_match_count}/{total_count} nodes are in state RUNNING"
```

non_match_count, and total_count are variables filled by the test as it is evaluated.  Note that at this time there is no easy way to access the full set of statistics the test supports other than reading the script but

match_count and non_match_count are maintained by the expression matching / evaluation engine and thus are available to all stage_check tests.

Example:

```json
  "result"    : {
     "PASS"  : "All {non_match_count}/{total_count} nodes are in state RUNNING",
     "FAIL"  : "{match_count}/{total_count} nodes are NOT RUNNING"
  }
```
##### Entry_tests example

Combining all of the above sections together yields a complete **entry_tests** parameter.  

```json
"entry_tests" : {
     "defaults" : {
          "status"  : "FAIL",
          "format"  : "Node {nodeName} is in state {status}"
      },
      "tests" : [
           { "test" : "status != 'RUNNING'" }
      ],
      "result"    : {
         "PASS"  : "All {non_match_count}/{total_count} nodes are in state RUNNING",
         "FAIL"  : "{match_count}/{total_count} nodes are NOT RUNNING"
      }
  }
```

#### exclude_tests

This parameter allows a list entry results oriented stage_check test  to exclude some entries from consideration.  This parameter contains a list of test expressions (using the same grammar defined for entry_tests.tests).  If any given exclude_tests expression matches a results entry, that entry is excluded from consideration by the stage_check test.

Note that in the the below example **networkInterface** refers to a field in entries returned by the **PeerReachability** test.  As mentioned above, there is no easy way (other than looking at the tests) to understand what field names (dictionary keys) are available for use.  A plan to resolve this difficulty is currently under consideration.

```json
        "exclude_tests" : [
            "node_type == 'secondary' && networkInterface == 'DIA'",
            "node_type == 'secondary && networkInterface == 'LTE"
        ]
```
#### node_type

This parameter is present in almost all tests.  It can have 3 values:

1. primary
2. secondary
3. solitary

where each the primary node and secondary nodes are determined by evaluation the regular expressions defined by the global PrimaryRegex and SecondaryRegex parameters to the router's node name.

```json
"node-type" : "primary"
```

In some cases, version 2.0.0 extends the values permitted (this is  a function of the test json schema's more than anything else) to:

1. 0  
2. 1
3. primary
4. primary|0 
5. secondary
6. secondary|1
7. solitary

When used in the context of a Linux command-base test, the node_type parameter tells stage-check run from the conductor which node to collect the test data from (unlike graphql tests which can simultaneously collect data from one or both router nodes).

The new types, 0, 1, primary|0 and secondary|1 **should not** be used in graphql test parameters as node_type is used to evaluate tests in graphql-based tests.  Even if they could be evaluated, how meaningful would it be to say "exclude node 0 interface LTE from this test"?  Which node is node 0? It could be the primary, secondary, or even a solitary node.  Furthermore node 0's type might evaluate to **None** if there are 2 nodes to the router and neither match the **PrimaryRegex** or **SecondaryRegex**.

These new node when used for Linux tests, are processed as follows:

1. 0: Run on the first node
2. 1: Run on the second node
3. primary|0: First try the primary node, if it exists. Otherwise try the first node identified.  The difference between 0 and primary|0 is simply that if node 0 happens to be identified as secondary and a primary node has been identified, primary|0 will run the test against the primary node.
4. secondary|0: First try the secondry node, if it exists.  Otherwise try the second node identified.

Together with the SkipIfOneNode parameter, these new node_types can be used to make Linux tests router node type and count agnostic (a snippet from the default config.json):

```json
 {
    "TestModule"    : "RecentCores",
    "OutputModule"  : "Text",
    "Description"   : "Node 1 crashes",
    "Parameters"    : {
        "node_type" : "primary|0",
        "service"   : "128T"
     }
 },
 {
    "TestModule"    : "RecentCores",
    "OutputModule"  : "Text",
    "Description"   : "Node 2 crashes",
    "SkipIfOneNode" : true,
    "Parameters"    : {
        "node_type" : "secondary|1",
        "service"   : "128T"
     }
 },
```
#### Specific Parameters

At this time the best way to examine the set of available parameters for each test is to look at the sample_config.json file in the stage_check source code.  All configuration parameters for all tests are utilized.

This is an area for improvement.  A future version of stage_check will feature an option which dumps the configurable variables and their usage for each test.

## Stage Check Design

This section describes the architecture components for those interested in extending stage_check.

### TestExecutor

### LocalContext

The LocalContext class is used to determine if stage_check is running on a conductor or on a router, by examining the local.init and global.init files.  Certain tests may only be applicable if run from the router.  For example asset information can only be accessed on the conductor.

### RouterContext

The RouterContext class identifies the current router, stage_check is executing tests against.  It has a number of methods for acquiring and accessing information such as whether a node is primary or secondary, what the asset id of a node is, what the 128T version of the node is, etc.

### Test Development 

Currently there are two methods that must be overridden for each new `stage_check` test.  The first method, get_params provides default parameters in the event a parameter value is missing in config.json:

```
def get_params(self):
```

The second performs the test:

```python
 def run(self, local_info, router_context, gql_token, fp):
    """
    local_info     - The LocalContext, indicating if the node running stage_check is
                     a conductor or a router.
    router_context - The RouterContext, or information about the current router the tests                 
                     listed in config.json is being run against
    gql_token      - GraphQL Access Token (Note this will probably be deprecated as it may not 
                     be needed)    
    fp             - FilePointer to an output file passed by the TestExector class.  Human
                     readable text is sent to this file when stage_check.pex -o <filepath> is
                     executed
    """
```

#### GraphQL

Most configuration and/or state information specific to the 128T routing application can be obtained via its GraphQl API.

In order to construct a GraphQL query, the best place to start is to navigate to:

https://128.128.128.128/documentation/graphql

in a web browser, where **128.128.128.128** is replaced by the actual administrative IP address of a 128 technology router or conductor node.  Once you have constructed a query, send it to see what the results look like.

The existing GraphQL API is designed with a web client in mind, so for the purposes of stage_check some of the information can be populated by default.

Consider the following simple query from the GUI documentation (The allRouters(name : "router-name" top-level API is often used as it allows information for both nodes belonging to the same router to be acquired).

```graphql
{
  allRouters(name : "corp2")  {
     edges {
       node {
          name
          nodes {
             edges {
                node {
                  name
                }
            }
          }
      }
    }
  }
}
```

and the result returned on a test 128 Technology router node:

```json
{
  "data": {
    "allRouters": {
      "edges": [
        {
          "node": {
            "name": "corp2",
            "nodes": {
              "edges": [
                {
                  "node": {
                    "name": "corp2-primary"
                  }
                },
                {
                  "node": {
                    "name": "corp2-secondary"
                  }
                }
              ]
            }
          }
        }
      ]
    }
  }
}
```

Some graphql clients would just send the exact message body:

```
request_body - '{  allRouters(name : "corp2")  {  edges { node { name  nodes  { edges { node { name } } } } } } }'
```

However, stage_check attempts a more algorithmic approach:

```python
  qr = gql_helper.NodeGQL("allRouters", ['name'], [ router_context.get_router() ], debug=self.debug)
  qn = gql_helper.NodeGQL("nodes", ['name'])
```
where each **gql_helper.NodeGQL** instance hides the need for the edge and nodes constructs.  

When considering the results of a GraphQL query, stage_check usually 'flattens' the json response to make it easier to handle with algorithmically, so the using the above response (not really a realistic example) the response would be flattened to:

```
{
    {
         "router/name" : "corp2",
         "name"        : "corp2-primary"
    },
    {
         "router/name" : "corp2",
         "name"        : "corp2-secondary"
    }
}
```

by using the following method:

```
flatter_json = qr.flatten_json(json_reply, 'router/nodes', '/')
```

which effectively says take the returned json and flatten it into multiple entries at the router/nodes level in the response data, identifying fields (leaf nodes) from higher-levels by concatenating the node 'names' using the '/' character.

now the following can be used

```
router_context.set_allRouters_node_type(flatter_json, node_name_key="nodeName")
```

to add the node_type information to the flattened results:

```
{
    {
         "router/name" : "corp2",
         "name"        : "corp2-primary"
         "node_type"   : "primary"
    },
    {
         "router/name" : "corp2",
         "name"        : "corp2-secondary"
         "node_type"   : "secondary"
    }
}
```

This approach has worked most of the time, but it does have its limits, because the flattened entry may contain complex data types such as lists or dictionaries -- and processing these without specialized code would require processing of jmespath-like expressions.

If this flattening is possible, one can simply iterate over the json dictionary:

```python
for entry in flatter_json:
    do_something_with_the entry()
```

TestAssetState.py is an example of on test that can be used as reference code.

#### GraphQL and Jinja templates.

In addition to the above approach of using Node class instances to define the GraphQL query, 
a new GQLTemplate class using a jina2 template to represent the query is now available.  
This makes it easy to cut and paste from the conductor's GraphQL explorer GUI into a request 
which can be sent by stage_check.pex (from TestProcessStates.py):

```
class TestProcessStates(AbstractTest.GraphQL):

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

  def run(self, local_info, router_context, gql_token, fp):

      :
      : 

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
```

Generally speaking, a GraphQL jinja template should include a variable for the router name 
it's intended for, which should then be populated in the run method using router_context.name.

Although this is not yet added, algorithmic analysis of the jinja2 template defining te query
can provide a list of valid field name / variable references in the test configuration which
should allow for some validation of the test configuration without requiing that the request
be sent to the GraphQL API and the results evaluated.

Additionally the json reply is flattened to the level specified by the flatpath
constructor argument, so this is no longer required to be done explicitly.

#### Linux

Sometimes the information being sought is not available from the 128T application itself, but must be obtained by running a Linux command.  Generally speaking, the **Linux.py** contains classes for various Linux commands, which scrape the output (most Linux commands of interest do not output in json or xml, but some do) and convert it into json.

Note that a linux command invoked when stage_check is run on the router is executed in a sub-process.  When stage_check is run on a conductor, linux commands are executed remotely on router noes by using: t128- salt <asset-id> cmd.run <command>.

If support for a new Linux command is added, a unit test should be added to :

test_linux_json.py

To utilize a json / python dictionary converted from linux shell command output in a stage_check test, something like the following would be used:

```python
  t1_detail = Linux.T1Detail(
      debug=self.debug,
      progobj=self
  )

  # Ugly....                                                                                                                                                                                          
  self.fp = fp
  shell_status = t1_detail.run_linux_args(
      local_info,
      router_context,
      params['node_type'],
      params['namespace'],
      params['linux_device'],
      error_lines,
      json_data
  )
  # Ugly
  self.fp = None
```
#### Entry Tests

The dataset entry test module is found in EntryTest.py.   This plays a large role in the processing of tests which operate on one or more python dictionary entries derived from GraphQL responses, or Linux output.

For tests which process one or more python list entries, the processing loop will look something like:

```python
 engine = EntryTest.Parser()
 for entry in flatter_json:
      if engine.exclude_entry(entry, params["exclude_tests"]):
          stats["exclude_count"] += 1
          continue
      test_status = engine.eval_entry_by_tests(entry, params["entry_tests"])
      Output.update_stats(stats, test_status)
      if test_status != None:
          self.output.proc_interim_result(entry, status=test_status)
```

where params["entry_tests"] is the **entry_tests** parameter, and params["exclude_tests"] is the exclude_tests parameter both of which are further discussed in the configuration section.

engine.eval_entry_by_tests() stops at the first  configured **entry_tests["tests"]** list entry, where entry['test'] matches the current entry in the dataset returned from querying the router node.  Each stage_check test may process the results somewhat differently (for example invoking a different output module method depending on the value returned by engine.exclude_entry()).  

#### Output Modules

The desire for stage_check to output data in more than human-readable text mandated the creation of an abstract output class which each stage_check tests interacts with via a set of events / observations (realized as specific Output class methods):

Example of a test invoking one of its Output methods:

```python
self.output.proc_interim_result(entry, status=test_status)
```

A test should implement as many of the output types as possible.  Currently this includes:

1. Text (human-readable text output)
2. LogStash (test simple PASS/FAIL json output)

Currently if an Output sub-class (say LogStash) is configured in the config.json, file stage_check will throw an exception.  In the future it may FAIL the test with an output event / method.

Current OutputModule class hierarchies for a new test named **New**.  

```text
                   Output.Base                Output.Base                
                    /        \                /        \                 
              OutputNew   Output.Text    OutputNew  Output.LogStash   
                    \        /                \        /
                    OutputNewText           OutputNewLogStash 
```

The Output**New**, Output**New**Text, and Output**New**LogStash classes should all be created in new files -- Output**New**.py, Output**New**Text.py, Output**New**LogStash.py.

Note that some output events occur frequently enough across different tests that they are implemented in the OutputText and OutputLogStash classes (see Output.py):

```python
  def run_as_wrong_user(self, user, status=Status.WARN):
      self.status = status
      self.message = f'Run script from Linux as user {user}'
      return self.status
```

While OutputModule classes contain data such as the test **status,** or in the case of OutputText, an additional **message** and **message list**, Output classes should refrain from making status judgements based on their own  data.

Avoid making status decisions (if possible) in Output classes:

```python
def my_test_event(self, some_interesting_data):
    if self.message is None:
          self.status = PASS
```

In other words, the stage_check test logic should make the determination of test PASS or FAIL, and not the output module (the original implementation of stage_check did not have Output classes and thus relied on the presence of  lack of certain output information to be an indication of PASS or FAIL.  This does not work if the Output class lacks he detailed information to make this decision though -- and thus it should be the responsibility of the stage_check test to make this determination).

One other consideration is the output consumer.  For example, data sent into a time series database may require that tests which scan multiple dataset entries, generate an independent, standalone time series entry for each dataset entry instead of a consolidated report.

#### Python Command Line Scripts

stage_check must be able to run both remotely from a conductor, and locally on a router node.  It is also preferable that it not install helper scripts to the router node (using salt) or otherwise alter the router node's environment if possible.  Nevertheless it is sometimes desirable to perform some test-related tasks on the router node which are difficult using bash.  For example the **TestLogs.py** module utilizes the **LogFilesSince** class from **Linux.py** to get a json list of log files newer than some timestamp (examination of arbitrary router logs is better done locally, on the router node),  rather than copying a python script though, stage_check.py runs a python command line script.

It can be challenging to find the correct escaping syntax, but hopefully the example below (from LogFilesSince)  will make things a bit easier, should this approach be required;

```python
command = f"""python3.6 -c 'exec(\"\"\"import pathlib, os, time, re, datetime, json 
debug={self.debug} 
path_list=pathlib.Path("{log_path}").glob("{log_glob}")                        
first_str=""                                                                       
last_str=""      
pattern="{self.date_regex}"
local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
dt_now = datetime.datetime.now(tz=local_tz) 
now_string = dt_now.strftime("%b %d %H:%M:%S %Y [%Z]") 
json_out = dict()                           
json_list = [] 
json_out["files"] = json_list 
json_out["now"] = now_string 
for path in path_list:
    fpath=str(path)
        with open(fpath, "rb") as fh:
        next(fh)
        next(fh)
        first=next(fh).decode()                                                                                          
        matches=re.search(pattern,first)
        if matches is not None:                                                         
            first_str=matches.group(1)
        fh.seek(-1024, os.SEEK_END)                                                           
        last=fh.readlines()[-1].decode() 
        matches=re.search(pattern, last)     
        if matches is not None:
             last_str=matches.group(1)          
             entry=dict() 
             entry["file"]  = fpath
             entry["start"] = first_str 
             entry["end"]   = last_str
             json_list.append(entry)   
print("{self.json_prefix}" + json.dumps(json_out, indent={self.json_indent})) \"\"\")' 
"""
```

   

## Building stage_check.pex

From the top level directory, run the bash script ./build_pex.

The build product, stage_check.pex, can be found at:

> python_build_env/stage_check/stage_check.pex



### Test Environment

While there are a few unit tests currently run to test human readable output formatting, the expression parser etc. these tests provide minimal coverage.  

Moving forwards **stage_check** will utilize **pytest** and minimally **mock** the responses from the GraphQL queries returned to various test modules.

## Writing New Stage Check Tests

Some of the concepts discussed in this section have evolved over time, and the current realization of existing tests may  not have been implemented with them in mind.

### Test Breadth

When adding a new test to stage_check, it is important to consider the breadth of the test.  If the stage_check queries Linux information or a 128Technology GraphQL API, the test should be as broad as possible.  

That is instead of writing a test module, **TestDeviceInterfaceStatus.py**, consider writing **TestDeviceInterface.py**, and use the **entry_tests.tests** configuration parameter:

```json
"test" : "status == OPER_DOWN"
```

