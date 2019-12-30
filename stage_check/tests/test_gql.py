#!/usr/bin/python3.6
##########################################################################################
#   _            _                   _     _          _                             
#  | |_ ___  ___| |_      __ _  __ _| |   | |__   ___| |_ __   ___ _ __ _ __  _   _ 
#  | __/ _ \/ __| __|    / _` |/ _` | |   | '_ \ / _ \ | '_ \ / _ \ '__| '_ \| | | |
#  | ||  __/\__ \ |_    | (_| | (_| | |   | | | |  __/ | |_) |  __/ | _| |_) | |_| |
#   \__\___||___/\__|____\__, |\__, |_|___|_| |_|\___|_| .__/ \___|_|(_) .__/ \__, |
#                  |_____|___/    |_||_____|           |_|             |_|    |___/ 
#
##########################################################################################

import pytest

import pytest_common
import gql_helper

import pprint

class GqlBase:
    def format_expected(self, result):
        expected = result.replace("\n", " ")
        expected = ' '.join(result.split())
        expected = expected.replace("( ", "(")
        return expected

class Test_NewGQL_Requests(GqlBase, pytest_common.TestBase):
    def test_device_interface_query(self):
        result = """
           {
              allRouters(name:"burl-corp") {
                 edges {
                     node {
                         name
                         nodes {
                            edges {
                                node {
                                    name 
                                    deviceInterfaces {
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
               }
           }
        }
        """
        expected = self.format_expected(result)
        dn = gql_helper.NewGQL(
            api_name="deviceInterfaces", 
            api_fields = [ "name" ],
            api_has_edges = True
        )
        nn = gql_helper.NewGQL(
            api_name="nodes", 
            api_fields = [ "name", dn ],
            api_has_edges = True
        )
        rn = gql_helper.NewGQL(
            api_name="allRouters", 
            api_args = { "name" : "burl-corp" }, 
            api_fields = [ "name", nn ],
            api_has_edges = True
        )
        request = rn.build_query()
        query_string = request["query"] 
        assert query_string == expected

    def test_service_ping(self):
        result = """
        {
            servicePing(
                sourceIp:"8.8.8.8"
                destinationIp:"8.8.8.8" 
                serviceName:"google_dns_service"
                routerName:"burl-corp"
                nodeName:"burl-corp-primary" 
                tenant:"corp.t128"
                sequence:107 
                identifier:1000) {
                    status
                    statusReason
                    responseTime
                }
        }
        """
        expected = self.format_expected(result)
        sp = gql_helper.NewGQL(
            api_name="servicePing", 
            api_args = { 
                "sourceIp" : "8.8.8.8", 
                "destinationIp": "8.8.8.8", 
                "serviceName" : "google_dns_service",
                "routerName" : "burl-corp",
                "nodeName" : "burl-corp-primary", 
                "tenant" : "corp.t128",
                "sequence" : 107,
                "identifier" : 1000
            },
            api_fields = [ "status", "statusReason", "responseTime" ],
            api_has_edges = False
        )
        request = sp.build_query()
        query_string = request["query"] 
        assert query_string == expected

