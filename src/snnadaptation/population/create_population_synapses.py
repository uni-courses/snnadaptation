"""Creates the different redundant population neurons, per neruon type.

TODO: check multiplies with 0, e.g. vth*red_level with vth =0.
"""

import networkx as nx
from snnbackends.networkx.LIF_neuron import Synapse
from typeguard import typechecked


@typechecked
def add_population_synapses(
    *,
    adaptation_graph: nx.DiGraph,
    original_edges: nx.classes.reportviews.OutEdgeView,
    redundancy: int,
) -> None:
    """Creates fully connected synapses.

    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param node_name: Node of the name of a networkx graph.
    """
    # pylint: disable=R1702
    # Loop through original edges:
    for original_edge in original_edges:
        if (  # Else: recurrent edges do not need to be fully connected.
            original_edge[0] != original_edge[1]
            and "connector" not in original_edge[1]
        ):
            original_weight: float = adaptation_graph[original_edge[0]][
                original_edge[1]
            ]["synapse"].weight
            for left_red_level in range(0, redundancy + 1):
                for right_red_level in range(0, redundancy + 1):
                    # else: original synapse already exists.
                    if not (left_red_level == 0 and right_red_level == 0):
                        if left_red_level == 0:
                            left_node_name = original_edge[0]
                        else:
                            left_node_name = (
                                f"r_{left_red_level}_{original_edge[0]}"
                            )
                        if right_red_level == 0:
                            right_node_name = original_edge[1]
                        else:
                            right_node_name = (
                                f"r_{right_red_level}_{original_edge[1]}"
                            )
                        add_synapse(
                            adaptation_graph=adaptation_graph,
                            left_node_name=left_node_name,
                            original_weight=original_weight,
                            right_node_name=right_node_name,
                        )
        else:
            print("TODO: add recurrent edge to redundant node.")


@typechecked
def add_synapse(
    *,
    adaptation_graph: nx.DiGraph,
    left_node_name: str,
    original_weight: float,
    right_node_name: str,
    # redundancy: int,
) -> None:
    """Adds a synapse within the population."""

    if left_node_name in adaptation_graph.nodes:
        print(f"add:{left_node_name, right_node_name}")
        adaptation_graph.add_edges_from(
            [(left_node_name, right_node_name)],
            synapse=Synapse(
                weight=original_weight,
                delay=0,
                change_per_t=0,
            ),
            is_redundant=True,
        )
    else:
        print(f"skip:{left_node_name}")
