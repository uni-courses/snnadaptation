"""Applies brain adaptation to a MDSA SNN graph."""
import copy
from typing import Dict, List, Tuple

import networkx as nx
from snnbackends.networkx.LIF_neuron import Identifier, LIF_neuron, Synapse
from snncompare.export_plots.Plot_config import Plot_config
from typeguard import typechecked


@typechecked
def apply_redundancy(
    *,
    adaptation_graph: nx.DiGraph,
    redundancy: int,
    plot_config: Plot_config,
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
                plot_config=plot_config,
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
            add_inhibitory_outgoing_synapses(
                adaptation_graph=adaptation_graph,
                node_name=node_name,
                max_red_level=redundancy,
            )

            # Add inhibitory synapse from node to redundant node.
            # add_inhibitory_synapse(
            #    adaptation_graph=adaptation_graph,
            #    node_name=node_name,
            #    red_level=red_level,
            # )

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
    *,
    adaptation_graph: nx.DiGraph,
    node_name: str,
    plot_config: Plot_config,
    red_level: int,
) -> None:
    """Create neuron and set coordinate position.

    :param d: Unit length of the spacing used in the positions of the nodes for
    plotting.
    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.
    """

    # TODO: include spike={}, is_redundant=True,
    ori_lif = adaptation_graph.nodes[node_name]["nx_lif"][0]
    bare_node_name = ori_lif.name
    identifiers = ori_lif.identifiers

    redundant_neuron_properties: Dict[
        str, float
    ] = computer_red_neuron_properties(
        adaptation_graph=adaptation_graph,
        node_name=node_name,
        red_level=red_level,
    )
    lif_neuron = LIF_neuron(
        name=f"r_{red_level}_{bare_node_name}",
        bias=redundant_neuron_properties["bias"],
        du=redundant_neuron_properties["du"],
        dv=redundant_neuron_properties["dv"],
        vth=redundant_neuron_properties["vth"],
        pos=(
            float(
                adaptation_graph.nodes[node_name]["nx_lif"][0].pos[0]
                + (plot_config.dx_redundant * red_level)
                * (1.0 + plot_config.redundant_curve_factor)
                ** red_level  # Curve to right
            ),
            float(
                adaptation_graph.nodes[node_name]["nx_lif"][0].pos[1]
                + (plot_config.dy_redundant * red_level)
                * (1.0 - plot_config.redundant_curve_factor)
                ** red_level  # Curve down
            ),
        ),
        identifiers=identifiers,
    )

    adaptation_graph.add_node(lif_neuron.full_name)
    adaptation_graph.nodes[lif_neuron.full_name]["nx_lif"] = [lif_neuron]


@typechecked
def computer_red_neuron_properties(
    *, adaptation_graph: nx.DiGraph, node_name: str, red_level: int
) -> Dict[str, float]:
    """Computes the redundant neuron properties such that they take over in the
    right settings."""
    if node_name[:9] != "selector_" and node_name[:11] != "next_round_":
        # if node_name[:9] != "selector_":
        bias = adaptation_graph.nodes[node_name]["nx_lif"][0].bias.get()
        du = adaptation_graph.nodes[node_name]["nx_lif"][0].du.get()
        dv = adaptation_graph.nodes[node_name]["nx_lif"][0].dv.get()
        vth = compute_vth_for_delay(  # Different vals for different neurons.
            adaptation_graph=adaptation_graph,
            node_name=node_name,
            red_level=red_level,
        )
    elif node_name[:11] == "next_round_":
        bias = adaptation_graph.nodes[node_name]["nx_lif"][0].bias.get()
        du = adaptation_graph.nodes[node_name]["nx_lif"][0].du.get()
        dv = adaptation_graph.nodes[node_name]["nx_lif"][0].dv.get()
        vth = adaptation_graph.nodes[node_name]["nx_lif"][0].vth.get()
    else:
        m_val_identifier: Identifier = adaptation_graph.nodes[node_name][
            "nx_lif"
        ][0].identifiers[1]
        if m_val_identifier.description == "m_val":
            if m_val_identifier.value == 0:
                bias = 1.0
                du = 0.1
                dv = 0.0
                vth = float(red_level)
            else:
                # Designed using neuron discovery grid search. Limited to a
                # redundancy of max 4, because after that adding +1 to vth
                # does not result in the selector neuron spiking 1 timestep
                # later (w.r.t. an incoming spike at fixed arbitrary time t).
                bias = 0.0
                du = 0.1
                dv = 0.0
                vth = float(red_level)  # Add delay in when redundant redundant
                # etc. neurons take over.
        else:
            raise ValueError(
                "Error, node identifier was not m_val for selector node."
            )

    return {
        "bias": bias,
        "du": du,
        "dv": dv,
        "vth": vth,
    }


@typechecked
def compute_vth_for_delay(
    *, adaptation_graph: nx.DiGraph, node_name: str, red_level: int
) -> float:
    """Increases vth with 1 to realise a delay of t=1 for the redundant
    spike_once neurons, rand neurons and selector neurons.

    Returns dv of default node otherwise.

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.
    """
    if node_name[:11] == "next_round_":
        vth = adaptation_graph.nodes[node_name]["nx_lif"][0].vth.get() + 1
    elif (
        node_name[:16] == "degree_receiver_"
        or node_name[:11] == "spike_once_"
        or node_name[:5] == "rand_"
    ):
        vth = (
            adaptation_graph.nodes[node_name]["nx_lif"][0].vth.get()
            + red_level
        )
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

        if node_name[:9] == "selector_" and edge[0][:11] == "next_round_":
            # The redundant selector neurons only start firing n seconds after
            # the next_round neuron has fired.
            weight = 1
        else:
            weight = adaptation_graph[edge[0]][edge[1]]["synapse"].weight

        edges: List[Tuple[str, str]] = [(left_node_name, right_node_name)]
        if left_node_name[:11] == "next_round_":
            # print(f'add:{(left_node_name, right_node_name)}')
            edges.append((f"r_{red_level}_{left_node_name}", right_node_name))

        # Create edge
        adaptation_graph.add_edges_from(
            edges,
            synapse=Synapse(
                weight=weight,
                delay=0,
                change_per_t=0,
            ),
            is_redundant=True,
        )
    # if node_name == "selector_0_1":
    # exit()


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
def add_inhibitory_outgoing_synapses(
    *, adaptation_graph: nx.DiGraph, node_name: str, max_red_level: int
) -> None:
    """Adds inhibitory synapse for selector neuron."""

    edges = []
    # Add edge from selector into redundant selectors
    for red_level in range(1, max_red_level + 1):
        edges.append((node_name, f"r_{red_level}_{node_name}"))

        # Add edge from redundant selector to remaining redundant selectors
        for right_red_level in range(red_level + 1, max_red_level + 1):
            edges.append(
                (
                    f"r_{red_level}_{node_name}",
                    f"r_{right_red_level}_{node_name}",
                )
            )
    adaptation_graph.add_edges_from(
        edges,
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
            synapse=Synapse(
                weight=adaptation_graph.nodes[node_name]["recur"],
                delay=0,
                change_per_t=0,
            ),
        )
    if node_name[:9] == "selector_":
        adaptation_graph.add_edges_from(
            [
                (
                    f"r_{red_level}_{node_name}",
                    f"r_{red_level}_{node_name}",
                )
            ],
            synapse=Synapse(
                weight=4,
                delay=0,
                change_per_t=0,
            ),
        )
