import pandas as pd
import numpy as np
import networkx as nx
import lightgbm as lgb
import random
import sys
import time

train = pd.read_csv("../Data/train.csv")
test = pd.read_csv("../Data/test.csv")
user_features = pd.read_csv("../Data/user_features.csv")
train.shape, test.shape, user_features.shape

random.seed(2)
ids = list(train.index)
random.shuffle(ids)
folds = []
for i in range(10):
    folds.append(set(ids[i * train.shape[0]//10 : (i+1) * train.shape[0]//10]))

node1_counts = train[['node1_id']].append(test[['node1_id']]).node1_id.value_counts().to_dict()
node2_counts = train[['node2_id']].append(test[['node2_id']]).node2_id.value_counts().to_dict()

def create_features(i):
    start_time = time.time()
    if i >= 0:
        df = train[train.index.isin(folds[i])].reset_index(drop = True)
        graph_df = train[train.index.isin(folds[i]) == False].reset_index(drop = True)
    else:
        df = test.copy()
        graph_df = train.copy()
    user_graph_directed = nx.DiGraph()
    for row in graph_df[graph_df.is_chat == 1].itertuples():
        user_graph_directed.add_edge(row.node1_id, row.node2_id)
    user_graph_undirected = nx.Graph()
    for row in graph_df[graph_df.is_chat == 1].itertuples():
        user_graph_undirected.add_edge(row.node1_id, row.node2_id)
    pg_ranks = nx.pagerank(user_graph_directed)
    avg_neighbors = nx.average_neighbor_degree(user_graph_directed)
    avg_neighbors_undirected = nx.average_neighbor_degree(user_graph_undirected)
    
    node1_contacts = {row[0] : set(row[1]) for row in graph_df[['node1_id', 'node2_id']].groupby('node1_id').aggregate(tuple).itertuples()}
    node2_contacts = {row[0] : set(row[1]) for row in graph_df[['node1_id', 'node2_id']].groupby('node2_id').aggregate(tuple).itertuples()}

    df['num_contacts_from_node1'] = df.node1_id.map(node1_counts) 
    df['num_contacts_from_node2'] = df.node2_id.map(node1_counts)

    df['num_contacts_to_node1'] = df.node1_id.map(node2_counts) 
    df['num_contacts_to_node2'] = df.node2_id.map(node2_counts)

    df['contacts_from_count'] = df.num_contacts_from_node1 + df.num_contacts_from_node2
    df['contacts_to_count'] = df.num_contacts_to_node1 + df.num_contacts_to_node2
    
    df['node_count_from_diff_abs'] = (df.num_contacts_from_node1 - df.num_contacts_from_node2).map(abs)
    df['node_count_from_diff'] = df.num_contacts_from_node1 - df.num_contacts_from_node2

    df['node_count_to_from_diff_abs'] = (df.num_contacts_to_node1 - df.num_contacts_to_node2).map(abs)
    df['node_count_to_diff'] = df.num_contacts_to_node1 - df.num_contacts_to_node2
    
    def common_contacts_from(node1, node2):
        try:
            return len(node1_contacts[node1].intersection(node1_contacts[node2]))
        except KeyError:
            return -1
    def common_contacts_to(node1, node2):
        try:
            return len(node2_contacts[node1].intersection(node2_contacts[node2]))
        except KeyError:
            return -1

    def common_contacts_from_ratio(node1, node2):
        try:
            return len(node1_contacts[node1].intersection(node1_contacts[node2]))/max(1, len(node1_contacts[node1].union(node1_contacts[node2])))
        except KeyError:
            return -1
    def common_contacts_to_ratio(node1, node2):
        try:
            return len(node2_contacts[node1].intersection(node2_contacts[node2])) / max(1, len(node2_contacts[node1].union(node2_contacts[node2])))
        except KeyError:
            return -1

    df['common_contacts_from'] = [common_contacts_from(row.node1_id, row.node2_id) for row in df[['node1_id', 'node2_id']].itertuples()]
    df['common_contacts_to'] = [common_contacts_to(row.node1_id, row.node2_id) for row in df[['node1_id', 'node2_id']].itertuples()]
    df['common_contacts_from_ratio'] = [common_contacts_from_ratio(row.node1_id, row.node2_id) for row in df[['node1_id', 'node2_id']].itertuples()]
    df['common_contacts_to_ratio'] = [common_contacts_to_ratio(row.node1_id, row.node2_id) for row in df[['node1_id', 'node2_id']].itertuples()]

    def reverse_contact_exists(node1, node2):
        try:
            return 1 if node1 in node1_contacts[node2] else 0
        except:
            return -1
    df['reverse_contact_exists'] = [reverse_contact_exists(row.node1_id,row.node2_id) for row in df.itertuples()]
    graph_df['reverse_contact_exists'] = [reverse_contact_exists(row.node1_id,row.node2_id) for row in graph_df.itertuples()]
    graph_df['reverse_contact_exists'] = graph_df['reverse_contact_exists'].astype(np.float16)
    num_contacts_with_reverse_contacts = {row[0] : row[1] for row in graph_df[graph_df.reverse_contact_exists >=0][['node1_id', 'reverse_contact_exists']].groupby('node1_id').sum().itertuples()}
    mean_contacts_with_reverse_contacts = {row[0] : row[1] for row in graph_df[graph_df.reverse_contact_exists >=0][['node1_id', 'reverse_contact_exists']].groupby('node1_id').mean().itertuples()}
    
    df['num_contacts_with_reverse_contacts1'] = df['node1_id'].map(num_contacts_with_reverse_contacts)
    df['num_contacts_with_reverse_contacts2'] = df['node2_id'].map(num_contacts_with_reverse_contacts)

    df['mean_contacts_with_reverse_contacts1'] = df['node1_id'].map(mean_contacts_with_reverse_contacts)
    df['mean_contacts_with_reverse_contacts2'] = df['node2_id'].map(mean_contacts_with_reverse_contacts)

    df['same_node'] = df['node1_id'] == df['node2_id']

    connected_components = list(nx.connected_components(user_graph_undirected))
    connected_components_index = {n : i for i, c in enumerate(connected_components) for n in c}
    df['node1_connected_component'] = df.node1_id.map(connected_components_index)
    df['node2_connected_component'] = df.node2_id.map(connected_components_index)
    df['same_connected_component'] = df['node1_connected_component'] == df['node2_connected_component']
    df['node1_connected_component_count'] = df[['node1_id', 'node1_connected_component']].groupby('node1_id').transform('count')
    df['node2_connected_component_count'] = df[['node2_id', 'node2_connected_component']].groupby('node2_id').transform('count')
    df['connected_component_count_diff'] = df['node1_connected_component_count'] - df['node2_connected_component_count']
    graph_df['node1_connected_component'] = graph_df.node1_id.map(connected_components_index)
    graph_df['node2_connected_component'] = graph_df.node2_id.map(connected_components_index)
    connected_component_is_chat_mean1 = {row[0] : row[1] for row in graph_df[['node1_connected_component', 'is_chat']].groupby('node1_connected_component').mean().itertuples()}
    connected_component_is_chat_mean2 = {row[0] : row[1] for row in graph_df[['node2_connected_component', 'is_chat']].groupby('node2_connected_component').mean().itertuples()}
    df['connected_component_is_chat_mean1'] = df['node1_connected_component'].map(connected_component_is_chat_mean1)
    df['connected_component_is_chat_mean2'] = df['node2_connected_component'].map(connected_component_is_chat_mean2)

    clusters = nx.cluster.clustering(user_graph_undirected)
    df['node1_cluster_coef'] = df.node1_id.map(clusters)
    df['node2_cluster_coef'] = df.node2_id.map(clusters)
    df['cluster_coef_diff'] = df['node1_cluster_coef'] - df['node2_cluster_coef']
    
    df['reverse_connection_exists'] = [user_graph_directed.has_edge(row.node2_id, row.node1_id) for row in df.itertuples()]
    # df['reverse_connection_fraction_node1'] = df[['node1_id', 'reverse_connection_exists']].groupby('node1_id').transform('mean')
    # df['reverse_connection_fraction_node2'] = df[['node2_id', 'reverse_connection_exists']].groupby('node2_id').transform('mean')
    graph_df['reverse_connection_exists'] = [user_graph_directed.has_edge(row.node2_id, row.node1_id) for row in graph_df.itertuples()]
    num_connections_with_reverse_contacts = {row[0] : row[1] for row in graph_df[graph_df.reverse_connection_exists >=0][['node1_id', 'reverse_connection_exists']].groupby('node1_id').sum().itertuples()}
    mean_connections_with_reverse_contacts = {row[0] : row[1] for row in graph_df[graph_df.reverse_connection_exists >=0][['node1_id', 'reverse_connection_exists']].groupby('node1_id').mean().itertuples()}
    
    df['num_connections_with_reverse_contacts1'] = df['node1_id'].map(num_connections_with_reverse_contacts)
    df['num_connections_with_reverse_contacts2'] = df['node2_id'].map(num_connections_with_reverse_contacts)

    df['mean_connections_with_reverse_contacts1'] = df['node1_id'].map(mean_connections_with_reverse_contacts)
    df['mean_connections_with_reverse_contacts2'] = df['node2_id'].map(mean_connections_with_reverse_contacts)

    df['reversed_conection_to_contact_ratio1'] = df['num_connections_with_reverse_contacts1'] / df['num_contacts_with_reverse_contacts1'].map(lambda x : max(1,x))
    df['reversed_conection_to_contact_ratio2'] = df['num_connections_with_reverse_contacts2'] / df['num_contacts_with_reverse_contacts2'].map(lambda x : max(1,x))

    df['page_rank_1'] = df['node1_id'].map(pg_ranks).fillna(-1)
    df['page_rank_2'] = df['node2_id'].map(pg_ranks).fillna(-1)
    df['avg_neighbors_1_directed'] = df['node1_id'].map(avg_neighbors).fillna(-1)
    df['avg_neighbors_2_directed'] = df['node2_id'].map(avg_neighbors).fillna(-1)
    df['avg_neighbors_1_undirected'] = df['node1_id'].map(avg_neighbors_undirected).fillna(-1)
    df['avg_neighbors_2_undirected'] = df['node2_id'].map(avg_neighbors_undirected).fillna(-1)
    df['page_rank_diff'] = df['page_rank_1'] - df['page_rank_2']
    df['avg_neighbors_directed_diff'] = df['avg_neighbors_1_directed'] - df['avg_neighbors_2_directed']
    df['avg_neighbors_undirected_diff'] = df['avg_neighbors_1_undirected'] - df['avg_neighbors_2_undirected']
    

    df['avg_node2_from_count'] = df[['node1_id', 'num_contacts_to_node1']].groupby('node1_id').transform('mean')
    df['avg_node1_from_count'] = df[['node2_id', 'num_contacts_from_node2']].groupby('node2_id').transform('mean')
    df['avg_node2_to_count'] = df[['node1_id', 'num_contacts_to_node1']].groupby('node1_id').transform('mean')
    df['avg_node1_to_count'] = df[['node2_id', 'num_contacts_to_node2']].groupby('node2_id').transform('mean')

    node1_connections = graph_df[graph_df.is_chat == 1]['node1_id'].value_counts().to_dict()
    node2_connections = graph_df[graph_df.is_chat == 1]['node2_id'].value_counts().to_dict()


    df['node1_connection_from_count'] = df['node1_id'].map(node1_connections)
    df['node2_connection_from_count'] = df['node2_id'].map(node1_connections)
    df['node1_connection_to_count'] = df['node1_id'].map(node2_connections)
    df['node2_connection_to_count'] = df['node2_id'].map(node2_connections)

    df['node_connection_from_sum'] = df['node1_connection_from_count'] + df['node2_connection_from_count']
    df['node_connection_to_sum'] = df['node1_connection_to_count'] + df['node2_connection_to_count']

    df['node1_connection_from_percentage'] = df['node1_connection_from_count'] / df['num_contacts_from_node1']
    df['node2_connection_from_percentage'] = df['node2_connection_from_count'] / df['num_contacts_from_node2']
    df['node1_connection_to_percentage'] = df['node1_connection_to_count'] / df['num_contacts_to_node1']
    df['node2_connection_to_percentage'] = df['node2_connection_to_count'] / df['num_contacts_to_node2']
    
    df['node_connection_from_diff'] = df['node1_connection_from_count'] - df['node2_connection_from_count']
    df['node_connection_to_diff'] = df['node1_connection_to_count'] - df['node2_connection_to_count']

    df['avg_node2_connection_from_count'] = df[['node1_id', 'node2_connection_from_count']].groupby('node1_id').transform('mean')
    df['avg_node1_connection_from_count'] = df[['node2_id', 'node1_connection_from_count']].groupby('node2_id').transform('mean')
    df['avg_node2_connection_to_count'] = df[['node1_id', 'node2_connection_to_count']].groupby('node1_id').transform('mean')
    df['avg_node1_connection_to_count'] = df[['node2_id', 'node1_connection_to_count']].groupby('node2_id').transform('mean')

    def get_num_common_neighbors(nodes, g):
        (u,v) = nodes
        try:
            return len(set(g.neighbors(u)).intersection(set(g.neighbors(v))))
        except:
            return 0
    def get_common_neighbors_similarity(nodes, g):
        (u,v) = nodes
        try:
            return len(set(g.neighbors(u)).intersection(set(g.neighbors(v)))) / len(
                set(g.neighbors(u)).union(set(g.neighbors(v))))
        except:
            return 0
        
    def get_shortest_path(nodes, g):
        (u,v) = nodes
        try:
            return nx.shortest_path_length(g, u,v)
        except:
            return 1e5

    df['num_common_neighbors_directed'] = [get_num_common_neighbors((row.node1_id, row.node2_id), user_graph_directed) for row in df[['node1_id', 'node2_id']].itertuples()]
    df['num_common_neighbors_undirected'] = [get_num_common_neighbors((row.node1_id, row.node2_id), user_graph_undirected) for row in df[['node1_id', 'node2_id']].itertuples()]
    df['common_neighbors_similarity_directed'] = [get_common_neighbors_similarity((row.node1_id, row.node2_id), user_graph_directed) for row in df[['node1_id', 'node2_id']].itertuples()]
    df['common_neighbors_similarity_undirected'] = [get_common_neighbors_similarity((row.node1_id, row.node2_id), user_graph_undirected) for row in df[['node1_id', 'node2_id']].itertuples()]
    df['shortest_path_length_directed'] = [get_shortest_path((row.node1_id, row.node2_id), user_graph_directed) for row in df[['node1_id', 'node2_id']].itertuples()]
    df['shortest_path_length_undirected'] = [get_shortest_path((row.node1_id, row.node2_id), user_graph_undirected) for row in df[['node1_id', 'node2_id']].itertuples()]


    df = df.merge(user_features.rename(columns = {'node_id' : 'node1_id'}), on = 'node1_id', how = 'left').merge(
                user_features.rename(columns = {'node_id' : 'node2_id'}), on = 'node2_id', how = 'left').fillna(-1)

    def cosine_similarity(vec1, vec2):
        vec1_norm = vec1 * vec1
        vec1_norm = np.sqrt(vec1_norm.sum(axis = 1))
        vec2_norm = vec2 * vec2
        vec2_norm = np.sqrt(vec2_norm.sum(axis = 1))
        cossim = vec1 * vec2 / (vec1_norm * vec2_norm)[:, None]
        return cossim.sum(axis = 1)

    df['cossim'] = cosine_similarity(df[['f{}_x'.format(i) for i in range(1,14)]].values, df[['f{}_y'.format(i) for i in range(1,14)]].values)
    
    feats = [12, 9, 3, 13,6]
    for i in range(len(feats)):
        for j in range(i, len(feats)):
            if i != j:
                df["f{}_x_minus_f{}_x".format(feats[i],feats[j])] = (df["f{}_x".format(feats[i])] - df["f{}_x".format(feats[j])]).astype(np.int8)
                df["f{}_y_minus_f{}_y".format(feats[i],feats[j])] = (df["f{}_y".format(feats[i])] - df["f{}_y".format(feats[j])]).astype(np.int8)

    df['f_sum_x'] = df[['f{}_x'.format(i) for i in range(1,14)]].sum(axis = 1)
    df['f_min_x'] = df[['f{}_x'.format(i) for i in range(1,14)]].min(axis = 1)
    df['f_max_x'] = df[['f{}_x'.format(i) for i in range(1,14)]].max(axis = 1)
    df['f_mean_x'] = df[['f{}_x'.format(i) for i in range(1,14)]].mean(axis = 1)
    df['f_sum_y'] = df[['f{}_y'.format(i) for i in range(1,14)]].sum(axis = 1)
    df['f_min_y'] = df[['f{}_y'.format(i) for i in range(1,14)]].min(axis = 1)
    df['f_max_y'] = df[['f{}_y'.format(i) for i in range(1,14)]].max(axis = 1)
    df['f_mean_y'] = df[['f{}_y'.format(i) for i in range(1,14)]].mean(axis = 1)

    for i in range(1,14):
        df["f{}_x_minus_f{}_y".format(i,i)] = (df['f{}_x'.format(i)] - df['f{}_y'.format(i)]).astype(np.int8)
    print("Total time taken is:", time.time() - start_time)
    return df

i = int(sys.argv[1])

if i < 0:
    create_features(i).to_csv("../Data/test_features.csv", index = False)
else:
    create_features(i).to_csv("../Data/train_features_fold_{}.csv".format(i), index = False)