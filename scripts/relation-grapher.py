import argparse
import matplotlib.pyplot as plt
import networkx as nx
import subprocess
import numpy as np
import utils
import sys

parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('filename')  
parser.add_argument('-r', '--root')      
parser.add_argument('-d', '--depth')
parser.add_argument('-w', '--width')



browser_path = "./bin/browser"
def get_data(data_fname : str, node : str, width : int) -> dict:
    width += 1
    cat_fd = subprocess.run(["cat", data_fname],
                capture_output=True,
                text=True)
    
    out_fd = subprocess.run([browser_path, node],
                input=cat_fd.stdout,
                capture_output=True,
                text=True)
    
    res_fd = subprocess.run(["head", "-n", str(width)],
                input=out_fd.stdout,
                capture_output=True,
                text=True)
    results = res_fd.stdout
    results = results.split("\n")[1:]
    res_dict = {}
    for r in results:
        if len(r) <= 1:
            continue
        split_r = r.split(" ")
        res_dict[split_r[0]] = float(split_r[1])
    return res_dict
    
def explore(data_fname : str, node : str, width : int, max_depth : int, edges : dict = None, depth : int = 1) -> dict:
    if edges == None:
        edges = {}
    if(depth > max_depth):
        return edges
    if(node in edges.keys()):
        return edges
    data = get_data(data_fname, node, width)

    edges[node] = data

    for k in data.keys():
        explore(data_fname, k, width, max_depth, edges, depth + 1)
    return edges

def transform_w(minw : float, maxw : float, w : float) -> float:
    #w *= 0.03
    w = utils.normalize(minw, maxw, w)
    #w = utils.ease_outexpo(w)
    return utils.lerp(0.001, 10, w)

def main():
    args = parser.parse_args()
    root_node = args.root
    if args.width == None:
        args.width = 15
    if args.depth == None:
        args.depth = 5
    edges = explore(args.filename, root_node, int(args.width), int(args.depth))
    G = nx.Graph()

    processed = set()
    unregistered_set = set()
    for k1 in edges.keys():
        for k2 in edges[k1].keys():
            if not k2 in edges.keys():
                unregistered_set.add(k2)
    for k in unregistered_set:
        edges[k] = {}

    for k1 in edges.keys():
        for k2 in edges[k1].keys():
            if k2 in processed:
                continue
            v1 = edges[k1][k2]

            if not k1 in edges[k2].keys():
                edges[k2][k1] = 0.0

            v2 = edges[k2][k1]
            
            #g.add_node(k1)
            #g.add_node(k2)
            avg = (v1 + v2) * 0.5 
            G.add_edge(k1, k2, color="r", weight=avg)

        processed.add(k1)
    weights = nx.get_edge_attributes(G,'weight').values()
    minw = min(weights)
    maxw = max(weights)
    nodes_weights = {}
    nodes_w_list = []
    node_colors = []
    for u,v,a in G.edges(data=True):
        if not u in nodes_weights.keys():
            nodes_weights[u] = 0.0
        if not v in nodes_weights.keys():
            nodes_weights[v] = 0.0
        
        weight = a["weight"]
        nodes_weights[u] += edges[u][v]
        nodes_weights[v] += edges[v][u]
        a['color'] = utils.color_from_weight(utils.normalize(minw, maxw, weight), [1, 0, 0, 0.3], [0, 1, 0, 1])
        a["weight"] = transform_w(minw, maxw, weight)
    
    nodes_min = min(nodes_weights.values())
    nodes_max = max(nodes_weights.values())

    for n in G.nodes():
        nodes_w_list.append(utils.lerp(25, 500, utils.normalize(nodes_min, nodes_max, nodes_weights[n])))
        perc = utils.normalize(nodes_min, nodes_max, nodes_weights[n])
        node_colors.append(utils.color_from_weight(perc, [0, 0, 1, 1], [0, 1, 1, 1]))
    colors = nx.get_edge_attributes(G,'color').values()
    widths = nx.get_edge_attributes(G,'weight').values()
    #layout_fn = 
    #pos = nx.random_layout(G)
    pos = utils.random_layout_spaced(G.nodes(), 0.1, 0.02)
    fig=plt.figure()
    nx.draw(G, pos, 
            edge_color=colors, 
            width=list(widths),
            with_labels=True,
            node_color=node_colors,
            node_size=nodes_w_list,
            font_size=7,
            font_color="white")
    fig.set_facecolor("#00000F")
    plt.show()

main()
