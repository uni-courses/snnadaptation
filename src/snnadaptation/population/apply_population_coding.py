"""Applies population coding to an incoming algorithm."""
import copy
from typing import Dict

import networkx as nx
from snnbackends.networkx.LIF_neuron import LIF_neuron
from snncompare.export_plots.Plot_config import Plot_config
from typeguard import typechecked

from snnadaptation.population.create_population_neurons import (
    get_population_neuron_properties,
)


@typechecked
def apply_population_coding(
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
            create_redundant_population_node(
                adaptation_graph=adaptation_graph,
                node_name=node_name,
                plot_config=plot_config,
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
def create_redundant_population_node(
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

    ori_lif = adaptation_graph.nodes[node_name]["nx_lif"][0]
    bare_node_name = ori_lif.name
    identifiers = ori_lif.identifiers

    redundant_neuron_properties: Dict[
        str, float
    ] = get_population_neuron_properties(
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
