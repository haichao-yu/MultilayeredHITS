import numpy as np


def ranking_get_input_matrices(selected_layers=("book", "dvd", "music", "video", "customer")):

    """
    Step 3: Get input adjacency matrices from selected layers.
    """

    # Given seleced layers
    # selected_layers = ("book", "dvd", "music", "video", "customer")

    # Load data+knowledge graph (Book, DVD, Music, Video, Customer)
    data = np.load("../AmazonDataProcessing/datasets/amazon-data-knowledge-graph.npy").item()
    adjacency_matrix = data["adjacency_matrix"]
    index2Id = data["index2Id"]
    # indices_book = data["indices_book"]
    # indices_dvd = data["indices_dvd"]
    # indices_music = data["indices_music"]
    # indices_video = data["indices_video"]
    # indices_customer = data["indices_customer"]

    # print type(adjacency_matrix)  # <class 'scipy.sparse.csr.csr_matrix'>

    # Get input for multi-layered HITS algorithm according to selected layers
    selectedWithinLayerNets = []
    selectedWithinLayerNetsDict = []
    for l in selected_layers:
        # https://stackoverflow.com/questions/7609108/slicing-sparse-scipy-matrix
        # A = B.tocsr()[np.array(list1), :].tocsc()[:, np.array(list2)]
        selectedWithinLayerNets.append(adjacency_matrix[data["indices_"+l], :].tocsc()[:, data["indices_"+l]])
        selectedWithinLayerNetsDict.append(index2Id[data["indices_"+l]])
    selectedWithinLayerNets = np.array(selectedWithinLayerNets)
    selectedWithinLayerNetsDict = np.array(selectedWithinLayerNetsDict)

    GroupNet = np.zeros((len(selected_layers), len(selected_layers)), dtype=int)
    GroupDict = np.array(selected_layers)
    selectedCrossLayerDependencies = []
    position = 0
    for i in range(len(selected_layers)):
        for j in range(i + 1, len(selected_layers)):
            position += 1
            GroupNet[i, j] = GroupNet[j, i] = position
            selectedCrossLayerDependencies.append(adjacency_matrix[data["indices_"+selected_layers[i]], :].tocsc()[:, data["indices_"+selected_layers[j]]])
    selectedCrossLayerDependencies = np.array(selectedCrossLayerDependencies)

    # Return
    data = {
        "GroupNet": GroupNet,
        "GroupDict": GroupDict,
        "WithinLayerNets": selectedWithinLayerNets,
        "WithinLayerNetsDict": selectedWithinLayerNetsDict,
        "CrossLayerDependencies": selectedCrossLayerDependencies,
    }
    return data