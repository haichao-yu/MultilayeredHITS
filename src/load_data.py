import numpy as np
from subgraph_from_bfs import subgraph_from_bfs
from subgraph_from_rwr import subgraph_from_rwr


def load_data_multilayered_hits_ranking(dataset, selected_layers):

    # Load data
    data = np.load(dataset).item()
    adjacency_matrix = data["adjacency_matrix"]
    # print type(adjacency_matrix)  # <class 'scipy.sparse.csr.csr_matrix'>

    # Get input for multi-layered HITS algorithm according to selected layers
    WithinLayerNets = []
    WithinLayerNetsDict = []
    for l in selected_layers:
        # https://stackoverflow.com/questions/7609108/slicing-sparse-scipy-matrix
        # A = B.tocsr()[np.array(list1), :].tocsc()[:, np.array(list2)]
        WithinLayerNets.append(adjacency_matrix[data['indices_range_' + l][0]:data['indices_range_' + l][1], :].tocsc()[:, data['indices_range_' + l][0]:data['indices_range_' + l][1]])
        WithinLayerNetsDict.append(data['index2Id_'+l])
    WithinLayerNets = np.array(WithinLayerNets)
    WithinLayerNetsDict = np.array(WithinLayerNetsDict)

    GroupNet = np.zeros((len(selected_layers), len(selected_layers)), dtype=int)
    GroupDict = np.array(selected_layers)
    CrossLayerDependencies = []
    position = 0
    for i in range(len(selected_layers)):
        for j in range(i + 1, len(selected_layers)):
            position += 1
            GroupNet[i, j] = GroupNet[j, i] = position
            CrossLayerDependencies.append(adjacency_matrix[data['indices_range_' + selected_layers[i]][0]:data['indices_range_' + selected_layers[i]][1], :].tocsc()[:, data['indices_range_' + selected_layers[j]][0]:data['indices_range_' + selected_layers[j]][1]])
    CrossLayerDependencies = np.array(CrossLayerDependencies)

    # Return
    input_data = {
        "QueryProductId": -1,

        "GroupNet": GroupNet,
        "GroupDict": GroupDict,
        "WithinLayerNets": WithinLayerNets,
        "WithinLayerNetsDict": WithinLayerNetsDict,
        "CrossLayerDependencies": CrossLayerDependencies,
    }
    return input_data


def load_data_multilayered_hits_query(dataset, query_node_index, selected_layers):

    # Load data
    data = np.load(dataset).item()

    # Get query product ID
    query_product_id = -1
    for l in ("book", "dvd", "music", "video"):
        if data["indices_range_" + l][0] <= query_node_index < data["indices_range_" + l][1]:
            query_product_id = data["index2Id_" + l][query_node_index - data["indices_range_" + l][0]]

    adjacency_matrix = data["adjacency_matrix"]
    print type(adjacency_matrix)  # <class 'scipy.sparse.csr.csr_matrix'>

    # Get subgraph w.r.t the query node
    # subgraph_node_indices = subgraph_from_bfs(adjacency_matrix, query_node_index)
    subgraph_node_indices = subgraph_from_rwr(adjacency_matrix, query_node_index)

    # Get input for multi-layered HITS algorithm according to selected layers
    temp = {"subgraph_indices_" + l: [] for l in selected_layers}
    for idx in subgraph_node_indices:
        for l in selected_layers:
            if data["indices_range_" + l][0] <= idx < data["indices_range_" + l][1]:
                temp["subgraph_indices_" + l].append(idx)
                break

    WithinLayerNets = []
    WithinLayerNetsDict = []
    for l in selected_layers:
        WithinLayerNets.append(adjacency_matrix[temp["subgraph_indices_" + l], :].tocsc()[:, temp["subgraph_indices_" + l]])
        WithinLayerNetsDict.append(data['index2Id_' + l][np.array(temp["subgraph_indices_" + l], dtype=int) - int(data["indices_range_" + l][0])])
    WithinLayerNets = np.array(WithinLayerNets)
    WithinLayerNetsDict = np.array(WithinLayerNetsDict)

    GroupNet = np.zeros((len(selected_layers), len(selected_layers)), dtype=int)
    GroupDict = np.array(selected_layers)
    CrossLayerDependencies = []
    position = 0
    for i in range(len(selected_layers)):
        for j in range(i + 1, len(selected_layers)):
            position += 1
            GroupNet[i, j] = GroupNet[j, i] = position
            CrossLayerDependencies.append(adjacency_matrix[temp["subgraph_indices_" + selected_layers[i]], :].tocsc()[:, temp["subgraph_indices_" + selected_layers[j]]])
    CrossLayerDependencies = np.array(CrossLayerDependencies)

    # Return
    input_data = {
        "QueryProductId": query_product_id,

        "GroupNet": GroupNet,
        "GroupDict": GroupDict,
        "WithinLayerNets": WithinLayerNets,
        "WithinLayerNetsDict": WithinLayerNetsDict,
        "CrossLayerDependencies": CrossLayerDependencies,
    }
    return input_data


def load_data_regular_hits_ranking(dataset, selected_layers):

    data = np.load(dataset).item()
    adjacency_matrix = data["adjacency_matrix"]
    subgraph_indices = [item for l in selected_layers for item in range(data["indices_range_" + l][0], data["indices_range_" + l][1])]

    input_data = {
        "QueryProductId": -1,
        "adjacency_matrix": adjacency_matrix[subgraph_indices, :].tocsc()[:, subgraph_indices]
    }

    for l in selected_layers:
        input_data["index2Id_" + l] = data["index2Id_" + l]

    input_data["indices_range_" + selected_layers[0]] = [0, 0 + len(input_data["index2Id_" + selected_layers[0]])]
    for i in range(1, len(selected_layers)):
        input_data["indices_range_" + selected_layers[i]] = [input_data["indices_range_" + selected_layers[i - 1]][1], input_data["indices_range_" + selected_layers[i - 1]][1] + len(input_data["index2Id_" + selected_layers[i]])]

    return input_data


def load_data_regular_hits_query(dataset, query_node_index, selected_layers):

    # Load data
    data = np.load(dataset).item()

    # Get query product ID
    query_product_id = -1
    for l in ("book", "dvd", "music", "video"):
        if data["indices_range_" + l][0] <= query_node_index < data["indices_range_" + l][1]:
            query_product_id = data["index2Id_" + l][query_node_index - data["indices_range_" + l][0]]

    adjacency_matrix = data["adjacency_matrix"]
    # print type(adjacency_matrix)  # <class 'scipy.sparse.csr.csr_matrix'>

    # Get subgraph w.r.t the query node
    # subgraph_node_indices = subgraph_from_bfs(adjacency_matrix, query_node_index)
    subgraph_node_indices = subgraph_from_rwr(adjacency_matrix, query_node_index)

    # Get input for multi-layered HITS algorithm according to selected layers
    temp = {"subgraph_indices_" + l: [] for l in selected_layers}
    for idx in subgraph_node_indices:
        for l in selected_layers:
            if data["indices_range_" + l][0] <= idx < data["indices_range_" + l][1]:
                temp["subgraph_indices_" + l].append(idx)
                break

    input_data = {
        "QueryProductId": query_product_id,
        "adjacency_matrix": adjacency_matrix[subgraph_node_indices, :].tocsc()[:, subgraph_node_indices],
    }

    for l in selected_layers:
        input_data["index2Id_" + l] = data['index2Id_' + l][np.array(temp["subgraph_indices_" + l], dtype=int) - int(data["indices_range_" + l][0])]

    input_data["indices_range_" + selected_layers[0]] = [0, 0 + len(temp["subgraph_indices_" + selected_layers[0]])]
    for i in range(1, len(selected_layers)):
        input_data["indices_range_" + selected_layers[i]] = [input_data["indices_range_" + selected_layers[i - 1]][1], input_data["indices_range_" + selected_layers[i - 1]][1] + len(temp["subgraph_indices_" + selected_layers[i]])]

    return input_data
