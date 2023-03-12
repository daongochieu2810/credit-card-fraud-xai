import os
import pickle
import json
import random
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import HeteroData
from neo4j import GraphDatabase, basic_auth

# set seed
seed = 2023
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
os.environ["PYTHONHASHSEED"] = str(seed)
DATA_PATH = "./data"

URI = "neo4j://localhost"
AUTH = ("neo4j", "password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

data = HeteroData()

transaction_index_mappings = {}
account_index_mappings = {}
user_index_mappings = {}
country_index_mappings = {}
lob_index_mappings = {}
sector_index_mappings = {}

def construct_nodes(transactions, users, accounts):#, countries, lobs, sectors):
    data['transaction'].x = []
    for index, t in enumarate(transactions):
        data['transaction'].x.append(list(t[0].values()))
        transaction_index_mappings[t[0]['id']] = index

    data['user'].x = []
    for index, t in enumarate(users):
        data['user'].x.append(list(t[0].values()))
        user_index_mappings[t[0]['id']] = index

    data['account'].x = []
    for index, t in enumarate(accounts):
        data['account'].x.append(list(t[0].values()))
        account_index_mappings[t[0]['id']] = index
    
    # data['user'].x = [list(t[0].values()) for t in users]
    # data['account'].x = [list(t[0].values()) for t in accounts]
    # data['country'].x = [list(t[0].values()) for t in countries]
    # data['lob'].x = [list(t[0].values()) for t in lobs]
    # data['sector'].x = [list(t[0].values()) for t in sectors]

def construct_edges(belongs_to, from_country, lob_in, received_by, transferred_by, works_in):
    data['account', 'belongs_to', 'user'].edge_index = []
    # data['account', 'from', 'country'].edge_index = []#... # [2, num_edges_writes]
    # data['account', 'lob_in', 'lob'].edge_index = []#... # [2, num_edges_affiliated]
    data['transaction', 'received_by', 'account'].edge_index = []#... # [2, num_edges_topic]
    data['transaction', 'transferred_by', 'account'].edge_index = []#... # [2, num_edges_topic]
    # data['account', 'works_in', 'sector'].edge_index = []

def fetch_nodes(tx):
    transactions = list(tx.run("MATCH (n:Transaction) RETURN properties(n) limit 25"))
    users = list(tx.run("MATCH (n:User) RETURN properties(n) limit 25"))
    accounts = list(tx.run("MATCH (n:Account) RETURN properties(n) limit 25"))
    # countries = list(tx.run("MATCH (n:Country) RETURN properties(n)"))
    # lobs = list(tx.run("MATCH (n:Lob) RETURN properties(n)"))
    # sectors = list(tx.run("MATCH (n:Sector) RETURN properties(n)"))

    construct_nodes(transactions, users, accounts)#, countries, lobs, sectors)

def fetch_edges(tx):
    belongs_to = list(tx.run("MATCH ()-[r:BELONGS_TO]->() RETURN r"))
    from_country = list(tx.run("MATCH ()-[r:FROM]->() RETURN r"))
    lob_in = list(tx.run("MATCH ()-[r:LOB_IN]->() RETURN r"))
    received_by = list(tx.run("MATCH ()-[r:RECEIVED_BY]->() RETURN r"))
    transferred_by = list(tx.run("MATCH ()-[r:TRANSFERRED_BY]->() RETURN r"))
    works_in = list(tx.run("MATCH ()-[r:WORKS_IN]->() RETURN r"))

    construct_edges(belongs_to, from_country, lob_in, received_by, transferred_by, works_in)

with driver.session() as session:
    records, summary = session.execute_read(fetch_nodes)

# print(data)

driver.close()