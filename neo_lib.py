
from contextlib import nullcontext
import pandas as pd
from pprint import pprint

from neo4j import GraphDatabase, basic_auth
from py2neo import Graph
class Neo_lib:
    def __init__(self, neo_url, neo_user, neo_pwd, neo_database):
        self.driver = GraphDatabase.driver(neo_url, auth=basic_auth(neo_user, neo_pwd))
        self.neo_database = neo_database
        self.graph = Graph(neo_url, auth=(neo_user, neo_pwd))



    def run_cypher(self,cq,limit=10):
        tran = lambda tx: tx.run(cq,limit=limit).data()
        with self.driver.session(database=self.neo_database) as session:
            results = session.write_transaction(tran)
        return results

    def run_cypher_pd(self,cq):
        results = self.graph.run(cq).to_data_frame()
        return results

    def reset_db(self):
        cq = "match (n) detach delete n"
        return self.run_cypher(cq)

    def get_stats(self):
        cq = """
        call apoc.meta.stats() yield labelCount, relTypeCount, propertyKeyCount, nodeCount, relCount
        with labelCount, relTypeCount, propertyKeyCount, nodeCount, relCount
        return labelCount, relTypeCount,propertyKeyCount, nodeCount,relCount
        """
        return self.run_cypher_pd(cq)

    def checksum(self):
        cq = """
        call apoc.meta.stats() yield labelCount, relTypeCount, propertyKeyCount, nodeCount, relCount
        with labelCount, relTypeCount, propertyKeyCount, nodeCount, relCount
        return labelCount+relTypeCount+propertyKeyCount+nodeCount+relCount as checksum
        """
        res = self.run_cypher(cq)
        return res[0]['checksum']

    def nodeCount(self):
        cq = """
        match (n) return count(n) as count
        """
        return self.run_cypher_pd(cq)


    def get_stats_all(self):
        cq = """
            call apoc.meta.stats()
            """
        return self.run_cypher_pd(cq)


    def schema_view(self):
        cq = "CALL db.schema.visualization()"
        print ("Run {} in Neo4j Browser to see a graphical view".format(cq))
        return self.run_cypher_pd(cq)


    def print_label_count(self):
        result = {"Label": [], "Count": []}
        for label in self.graph.run("CALL db.labels()").to_series():
            query = f"MATCH (:`{label}`) RETURN count(*) AS count"
            count = self.graph.run(query).to_data_frame().iloc[0]['count']
            result["Label"].append(label)
            result["Count"].append(count)
        nodes_df = pd.DataFrame(data=result)
        return nodes_df

