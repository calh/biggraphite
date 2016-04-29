#!/usr/bin/env python
from __future__ import print_function

import unittest

from cassandra import cluster as c_cluster
from testing import cassandra as testing_cassandra

from biggraphite import accessor as bg_accessor


def create_unreplicated_keyspace(contact_points, port, keyspace):
    """Create a keyspace, mostly used for tests."""
    cluster = c_cluster.Cluster(contact_points, port)
    session = cluster.connect()
    session.execute(
        "CREATE KEYSPACE %s "
        " WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};" %
        keyspace)
    session.shutdown()
    cluster.shutdown()


class TestCaseWithAccessor(unittest.TestCase):
    """"A TestCase with an Accessor for an ephemeral cassandra cluster."""

    KEYSPACE = "test_keyspace"

    @classmethod
    def setUpClass(cls):
        super(TestCaseWithAccessor, cls).setUpClass()
        cls.cassandra = testing_cassandra.Cassandra()
        cls.cassandra.start()

        # testing.cassandra is meant to be used with the Thrift API, so we need to
        # extract the IPs and native port for use with the native driver.
        cls.__contact_points = [s.split(":")[0]
                                for s in cls.cassandra.server_list()]
        cls.__port = cls.cassandra.cassandra_yaml["native_transport_port"]
        create_unreplicated_keyspace(cls.__contact_points, cls.__port, cls.KEYSPACE)

    @classmethod
    def tearDownClass(cls):
        super(TestCaseWithAccessor, cls).tearDownClass()
        cls.cassandra.stop()

    def setUp(self):
        super(TestCaseWithAccessor, self).setUp()
        self.accessor = bg_accessor.Accessor(
            self.KEYSPACE, self.__contact_points, self.__port)
        self.accessor.connect()
        self.addCleanup(self.accessor.shutdown)
