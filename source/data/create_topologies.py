import random
import networkx as nx
import pandas as pd


import os
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 2000
# get_ipython().system('pip3 install pygraphviz')

def max_flow_computation(Gbase, capacity_max):
    max_capacities = dict(zip(list(Gbase.edges), [capacity_max] * len(list(Gbase.edges))))
    nx.set_edge_attributes(Gbase, max_capacities, 'capacity')
    rand_source = list(Gbase.nodes)[random.randint(0, len(list(Gbase.nodes)))]
    rand_term = list(Gbase.nodes)[random.randint(0, len(list(Gbase.nodes)))]
    R = nx.max_flow_min_cost(Gbase, rand_source, rand_term)
    flows = {}
    G_copy = Gbase.copy()
    for edge in G_copy.edges:
        flows[(edge[0], edge[1])] = R[edge[0]][edge[1]]
    
    nx.set_edge_attributes(Gbase, flows, 'actual_capacity')


def process_graph_from_topology(file_path, 
                                excel_path, 
                                rtt_min, 
                                rtt_max, 
                                capacity_min, 
                                capacity_max, 
                                ip_capacity_final,
                                sample_bounds,
                                fp_max, 
                                spectrum_size, 
                                max_flow_flag=False,
                                c_min_flag=False):

    # leases and fibers stuff

    Gbase = nx.read_gml(file_path)
    #Gbase_cmin = find_edge_capacity_heuristic_centrality_betweeness(nx.DiGraph(Gbase))
    # quit()

    if max_flow_flag == False:
        Gbase_cmin = find_edge_capacity_heuristic_centrality_betweeness(Gbase)
    else:
        Gbase = nx.DiGraph(Gbase)
        max_flow_computation(Gbase, capacity_max)
        if c_min_flag:
            if c_min_flag == 1:
                Gbase_cmin = find_edge_capacity_heuristic_centrality_betweeness(Gbase)
            elif c_min_flag == 2:
                Gbase_cmin = find_edge_capacity_heuristic_flow_betweeness(Gbase)
            elif c_min_flag == 3:
                Gbase_cmin = find_edge_capacity_heuristic_flow_communicability_centrality(Gbase)
            else:
                print('invalid c_min option')
                quit()
    
    source_list = []
    dest_list = []
    rtt_list = []
    capacity_min_list = []
    capacity_max_list = []
    actual_capacity_list = []
    link_names_list = []
    cos_list = []

    max_fp_list = []
    spectrum_size_ghz_per_fp_list = []

    for i, edge in enumerate(Gbase.edges):
        source_list.append(edge[0])
        dest_list.append(edge[1])
        rtt_list.append(random.randint(rtt_min, rtt_max))
        # capacity_min_list.append(capacity_min)
        #capacity_min_list.append(Gbase_cmin.edges[edge]['weight'])
        capacity_max_list.append(capacity_max)
        link_names_list.append("Link_{}".format(i))

        # if c_min_flag:
        #     capacity_min_list.append(Gbase_cmin.edges[edge]['weight'])
        # else:
        #     capacity_min_list.append(capacity_min)
        cos_list.append('BRONZE') # not entirely sure what this is

        if max_flow_flag:
            actual_capacity_list.append(Gbase.edges[edge]['actual_capacity'])
            if c_min_flag:
                capacity_min_list.append(Gbase_cmin.edges[edge]['weight']* Gbase.edges[edge]['actual_capacity'])
            else:
                capacity_min_list.append(capacity_min)
        else:
            actual_capacity_list.append(random.randint(*sample_bounds))
            if c_min_flag:
                capacity_min_list.append(Gbase_cmin.edges[edge]['weight']*random.randint(*sample_bounds))
            else:
                capacity_min_list.append(capacity_min)


        max_fp_list.append(fp_max)
        spectrum_size_ghz_per_fp_list.append(spectrum_size)

    rtt_capacity_df = pd.DataFrame({
        'LinkName' : link_names_list,
        'Source' : source_list,
        'Destination' : dest_list,
        'RTT' : rtt_list,
        'CapacityMin' : capacity_min_list,
        'CapacityMax' : capacity_max_list,
    })

    flows_df = pd.DataFrame({
        'LinkName' : link_names_list,
        'Source' : source_list,
        'Destination' : dest_list,
        'COS' : cos_list,
        'ActualCapacity' : actual_capacity_list,
    })

    fibers_df = pd.DataFrame({
        'name' : link_names_list,
        'src' : source_list, 
        'dst' : dest_list,
        'rtt' : rtt_list,
        'max_fp' : max_fp_list,
        'spectrum_size_ghz_per_fp' : spectrum_size_ghz_per_fp_list
    })
    
    # ip, l3 stuff

    nodes = list(Gbase.nodes)
    IPGraph = Gbase.copy()

    ip_name_arr = nodes.copy()
    ip_l1_node_arr = nodes.copy()
    ip_stub_arr = ['FALSE'] * len(nodes)

    ip_source_list = []
    ip_dest_list = []
    ip_capacity_min_list = []
    ip_capacity_max_list = []
    ip_actual_capacity_list = []
    ip_link_names_list = []
    ip_fiber_name_map_spectrum_list = []
    igp_list = []

    for i, edge in enumerate(IPGraph.edges):
        ip_source_list.append(edge[0])
        ip_dest_list.append(edge[1])
        ip_capacity_min_list.append(capacity_min)
        ip_capacity_max_list.append(capacity_max)
        ip_link_names_list.append("ip_Link_{}".format(i))
        ip_fiber_name_map_spectrum_list.append("Link_{}:5".format(i))
        igp_list.append(0)
        
        if max_flow_flag:
            ip_actual_capacity_list.append(IPGraph.edges[edge]['actual_capacity'])
        else:
            ip_actual_capacity_list.append(ip_capacity_final) 
    
    ip_capacity_df = pd.DataFrame({
        'name' : ip_link_names_list,
        'src' : ip_source_list,
        'dst' : ip_dest_list,
        'min_capacity_gbps' : ip_capacity_min_list,
        'max_capacity_gbps' : ip_capacity_max_list,
        'final_capacity_gpbs' : ip_actual_capacity_list,
        'igp' : igp_list,
        'fiber_name_map_spectrum' : ip_fiber_name_map_spectrum_list,
    })

    ip_names_df = pd.DataFrame({
        'name' : ip_name_arr,
        'l1_node' : ip_l1_node_arr,
        'stub' : ip_stub_arr,
    })

    spofs_df = pd.DataFrame({
        'fiber_names' : [],
        'cos_to_protect' : [],
    })
    
    with pd.ExcelWriter(excel_path) as writer:
        rtt_capacity_df.to_excel(writer, sheet_name='RTT-Capacity')
        fibers_df.to_excel(writer, sheet_name='Fibers')
        flows_df.to_excel(writer, sheet_name='Flows')
        ip_names_df.to_excel(writer, sheet_name='L3Nodes')
        ip_capacity_df.to_excel(writer, sheet_name='L3Links')
        spofs_df.to_excel(writer, sheet_name='Spofs')


def find_edge_capacity_heuristic_centrality_betweeness(g):

    # edge_count = defaultdict(int)
    # m = nx.read_graphml(f).to_undirected()
    
    # g = nx.Graph(m)


    cut_edges = nx.edge_betweenness_centrality(g, normalized=True)
    max_val = max([val for val in cut_edges.values()])
    min_val = min([val for val in cut_edges.values()])


    for u, v, attr in g.edges(data=True):
        if (u,v) in cut_edges.keys():
            attr['weight'] = round((cut_edges[(u,v)]-min_val)/max_val,2)
        else:
            attr['weight'] = round((cut_edges[(v,u)]-min_val)/max_val,2)
    return(g)


def find_edge_capacity_heuristic_flow_betweeness(g):

    # edge_count = defaultdict(int)
    # m = nx.read_graphml(f).to_undirected()
    
    # g = nx.Graph(m)
    g = g.to_undirected()


    cut_edges = nx.edge_current_flow_betweenness_centrality(g, normalized=True)
    max_val = max([val for val in cut_edges.values()])
    min_val = min([val for val in cut_edges.values()])


    for u, v, attr in g.edges(data=True):
        if (u,v) in cut_edges.keys():
            attr['weight'] = round((cut_edges[(u,v)]-min_val)/max_val,2)
        else:
            attr['weight'] = round((cut_edges[(v,u)]-min_val)/max_val,2)
    return(g)


def find_edge_capacity_heuristic_flow_communicability_centrality(g):

    #edge_count = defaultdict(int)
    #m = nx.read_graphml(f).to_undirected()
    
    #g = nx.Graph(m)
    g = g.to_undirected()

    cut_edges = {}
    nodes = nx.communicability_exp(g)
    for u, v, attr in g.edges(data=True):
        cut_edges[(u,v)] = nodes[u][v]
        
    max_val = max([val for val in cut_edges.values()])
    min_val = min([val for val in cut_edges.values()])


    for u, v, attr in g.edges(data=True):
        if (u,v) in cut_edges.keys():
            attr['weight'] = round((cut_edges[(u,v)]-min_val)/max_val,2)
        else:
            attr['weight'] = round((cut_edges[(v,u)]-min_val)/max_val,2)
    return(g)


if __name__ == '__main__':
    for i, file in enumerate(['Tinet'] * 5):
    # for file in ['VisionNet', 'Globalcenter', 'Tinet', 'Cogentco', 'kdl']:
        # f = '/scratch/gpfs/ia3026/cos561/neuroplan/source/data/topologies/' + file
        file_path = 'topologies/gml_files/' + file + '_with_label_unique.gml'
        excel_path = 'topologies/test_tinet/' + file + '_topology_{}.xlsx'.format(i)
        rtt_min = 2
        rtt_max = 5
        capacity_min = 0
        capacity_max = 1000
        ip_capacity_final = 20
        sample_bounds = (750, 950)
        fp_max = 50
        spectrum_size = 10
        max_flow_flag = True
        # c_min_flag = 1 for find_edge_capacity_heuristic_centrality_betweeness
        # c_min_flag = 2 for find_edge_capacity_heuristic_flow_betweeness
        # c_min_flag = 3 for find_edge_capacity_heuristic_flow_communicability_centrality
        c_min_flag = False
        process_graph_from_topology(file_path, 
                                    excel_path, 
                                    rtt_min, 
                                    rtt_max, 
                                    capacity_min, 
                                    capacity_max, 
                                    ip_capacity_final,
                                    sample_bounds,
                                    fp_max, 
                                    spectrum_size,
                                    max_flow_flag,
                                    c_min_flag)