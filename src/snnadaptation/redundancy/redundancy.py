"""Applies brain adaptation to a MDSA SNN graph."""
import copy

import networkx as nx
from snnalgorithms.sparse.MDSA.layout import (
    Node_layout,
    get_hori_redundant_redundancy_spacing,
)
from snnbackends.networkx.LIF_neuron import LIF_neuron, Synapse
from typeguard import typechecked


@typechecked
def apply_redundancy(
    *,
    adaptation_graph: nx.DiGraph,
    redundancy: int
    # m,
) -> None:
    """
    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param m: The amount of approximation iterations used in the MDSA
    approximation.
    """
    adaptation_graph.graph["red_level"] = redundancy

    # Create a copy of the original list of nodes of the input graph.
    original_nodes = copy.deepcopy(adaptation_graph.nodes)
    for node_name in original_nodes:
        # Get input synapses as dictionaries, one per node, store as node
        # attribute.
        store_input_synapses(
            adaptation_graph=adaptation_graph, node_name=node_name
        )

        # Get output synapses as dictionaries, one per node, store as node
        # attribute.
        store_output_synapses(
            adaptation_graph=adaptation_graph, node_name=node_name
        )
        for red_level in range(1, redundancy + 1):
            # Create redundant neurons.
            create_redundant_node(
                adaptation_graph=adaptation_graph,
                node_name=node_name,
                red_level=red_level,
            )

    for red_level in range(1, redundancy + 1):
        # Start new loop before adding edges, because all redundant neurons
        # need to exist before creating synapses.
        for node_name in original_nodes:
            # Add input synapses to redundant node.
            add_input_synapses(
                adaptation_graph=adaptation_graph,
                node_name=node_name,
                red_level=red_level,
            )

            # Add output synapses to redundant node.
            add_output_synapses(
                adaptation_graph=adaptation_graph,
                node_name=node_name,
                red_level=red_level,
            )

            # Add inhibitory synapse from node to redundant node.
            add_inhibitory_synapse(
                adaptation_graph=adaptation_graph,
                node_name=node_name,
                red_level=red_level,
            )

            add_recurrent_inhibitiory_synapses(
                adaptation_graph=adaptation_graph,
                node_name=node_name,
                red_level=red_level,
            )


@typechecked
def store_input_synapses(
    *, adaptation_graph: nx.DiGraph, node_name: str
) -> None:
    """

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.

    """
    input_edges = []
    for edge in adaptation_graph.edges:
        if edge[1] == node_name:
            input_edges.append(edge)
    adaptation_graph.nodes[node_name]["input_edges"] = input_edges


@typechecked
def store_output_synapses(
    *, adaptation_graph: nx.DiGraph, node_name: str
) -> None:
    """

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.

    """
    output_edges = []
    for edge in adaptation_graph.edges:
        if edge[0] == node_name:
            output_edges.append(edge)
    adaptation_graph.nodes[node_name]["output_edges"] = output_edges


@typechecked
def create_redundant_node(
    *, adaptation_graph: nx.DiGraph, node_name: str, red_level: int
) -> None:
    """Create neuron and set coordinate position.

    :param d: Unit length of the spacing used in the positions of the nodes for
    plotting.
    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.
    """

    # TODO: include
    #    spike={},
    #    is_redundant=True,
    ori_lif = adaptation_graph.nodes[node_name]["nx_lif"][0]
    bare_node_name = ori_lif.name
    identifiers = ori_lif.identifiers
    node_layout = Node_layout(ori_lif.name)

    lif_neuron = LIF_neuron(
        name=f"r_{red_level}_{bare_node_name}",
        bias=adaptation_graph.nodes[node_name]["nx_lif"][0].bias.get(),
        du=adaptation_graph.nodes[node_name]["nx_lif"][0].du.get(),
        dv=adaptation_graph.nodes[node_name]["nx_lif"][0].dv.get(),
        vth=compute_vth_for_delay(
            adaptation_graph=adaptation_graph, node_name=node_name
        ),
        pos=(
            float(
                adaptation_graph.nodes[node_name]["nx_lif"][0].pos[0]
                + get_hori_redundant_redundancy_spacing(
                    bare_node_name=bare_node_name
                )
                * red_level
            ),
            float(
                adaptation_graph.nodes[node_name]["nx_lif"][0].pos[1]
                + node_layout.eff_height * red_level
            ),
        ),
        identifiers=identifiers,
    )
    adaptation_graph.add_node(lif_neuron.full_name)
    adaptation_graph.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]


@typechecked
def compute_vth_for_delay(
    *, adaptation_graph: nx.DiGraph, node_name: str
) -> float:
    """Increases vth with 1 to realise a delay of t=1 for the redundant
    spike_once neurons, rand neurons and selector neurons.

    Returns dv of default node otherwise.

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.
    """
    if (
        node_name[:11] == "spike_once_"
        or node_name[:5] == "rand_"
        or node_name[:9] == "selector_"
        or node_name[:16] == "degree_receiver_"
    ):
        vth = adaptation_graph.nodes[node_name]["nx_lif"][0].vth.get() + 1
    else:
        vth = adaptation_graph.nodes[node_name]["nx_lif"][0].vth.get()
    return vth


@typechecked
def add_input_synapses(
    *, adaptation_graph: nx.DiGraph, node_name: str, red_level: int
) -> None:
    """

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.

    """
    for edge in adaptation_graph.nodes[node_name]["input_edges"]:
        # Compute set edge weight
        left_node_name = edge[0]
        right_node_name = f"r_{red_level}_{node_name}"
        weight = adaptation_graph[edge[0]][edge[1]]["synapse"].weight

        # Create edge
        # adaptation_graph.add_edge(
        #    left_node_name, right_node_name, weight=weight, is_redundant=True
        # )

        adaptation_graph.add_edges_from(
            [(left_node_name, right_node_name)],
            synapse=Synapse(
                weight=weight,
                delay=0,
                change_per_t=0,
            ),
            is_redundant=True,
        )


@typechecked
def add_output_synapses(
    *, adaptation_graph: nx.DiGraph, node_name: str, red_level: int
) -> None:
    """

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.

    """
    adaptation_graph.add_edges_from(
        adaptation_graph.nodes[node_name]["output_edges"]
    )
    for edge in adaptation_graph.nodes[node_name]["output_edges"]:
        # Compute set edge weight
        left_node_name = f"r_{red_level}_{node_name}"
        right_node_name = edge[1]
        weight = adaptation_graph[edge[0]][edge[1]]["synapse"].weight

        # Create edge
        # adaptation_graph.add_edge(
        # left_node_name, right_node_name, weight=weight, is_redundant=True
        # )
        adaptation_graph.add_edges_from(
            [(left_node_name, right_node_name)],
            synapse=Synapse(
                weight=weight,
                delay=0,
                change_per_t=0,
            ),
            is_redundant=True,
        )


@typechecked
def add_inhibitory_synapse(
    *, adaptation_graph: nx.DiGraph, node_name: str, red_level: int
) -> None:
    """

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.

    """
    for left_index in range(1, red_level + 1):

        # TODO: compute what minimum inhibitory weight should be in network to
        # prevent all neurons from spiking.
        if left_index == 1:
            left_node_name = node_name
        elif left_index > 1:
            left_node_name = f"r_{red_level-1}_{node_name}"
        adaptation_graph.add_edges_from(
            [(left_node_name, f"r_{red_level}_{node_name}")],
            synapse=Synapse(
                weight=-100,
                delay=0,
                change_per_t=0,
            ),
            is_redundant=True,
        )


@typechecked
def add_recurrent_inhibitiory_synapses(
    *, adaptation_graph: nx.DiGraph, node_name: str, red_level: int
) -> None:
    """

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.

    """
    if "recur" in adaptation_graph.nodes[node_name].keys():
        adaptation_graph.add_edges_from(
            [
                (
                    f"r_{red_level}_{node_name}",
                    f"r_{red_level}_{node_name}",
                )
            ],
            weight=adaptation_graph.nodes[node_name]["recur"],
        )
