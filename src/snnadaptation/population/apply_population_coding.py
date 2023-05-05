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
from snnadaptation.population.create_population_synapses import (
    add_population_synapses,
)


@typechecked
def apply_population_coding(
    *,
    adaptation_graph: nx.DiGraph,
    redundancy: int,
    plot_config: Plot_config,
    # m,
) -> nx.DiGraph:
    """
    :param adaptation_graph: Graph with the MDSA SNN approximation solution.
    :param m: The amount of approximation iterations used in the MDSA
    approximation.
    """
    adaptation_graph.graph["red_level"] = redundancy
    original_edges = copy.deepcopy(adaptation_graph.edges)
    # Create a copy of the original list of nodes of the input graph.
    original_nodes = copy.deepcopy(adaptation_graph.nodes)
    for node_name in original_nodes:
        # Get input synapses as dictionaries, one per node, store as node
        # attribute.
        for red_level in range(1, redundancy + 1):
            # Create redundant neurons.
            if "connector_" not in node_name:
                create_redundant_population_node(
                    adaptation_graph=adaptation_graph,
                    max_redundancy=redundancy,
                    node_name=node_name,
                    plot_config=plot_config,
                    red_level=red_level,
                )

    for node_name in original_nodes:
        if "connector_" not in node_name:
            # TODO: overwrite original neuron with new properties.
            ori_lif = adaptation_graph.nodes[node_name]["nx_lif"][0]
            r_1_lif = adaptation_graph.nodes[f"r_1_{node_name}"]["nx_lif"][0]
            ori_lif.bias = copy.deepcopy(r_1_lif.bias)
            ori_lif.du = copy.deepcopy(r_1_lif.du)
            ori_lif.dv = copy.deepcopy(r_1_lif.dv)
            ori_lif.vth = copy.deepcopy(r_1_lif.vth)
            # ori_lif.vth = Vth(red_neuron_props["vth"])

    add_population_synapses(
        adaptation_graph=adaptation_graph,
        original_edges=original_edges,
        redundancy=redundancy,
    )

    return adaptation_graph


@typechecked
def create_redundant_population_node(
    *,
    adaptation_graph: nx.DiGraph,
    max_redundancy: int,
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

    red_neuron_props: Dict[str, float] = get_population_neuron_properties(
        adaptation_graph=adaptation_graph,
        node_name=node_name,
        max_redundancy=max_redundancy,
    )

    # pylint: disable=R0801
    lif_neuron = LIF_neuron(
        name=f"r_{red_level}_{bare_node_name}",
        bias=red_neuron_props["bias"],
        du=red_neuron_props["du"],
        dv=red_neuron_props["dv"],
        vth=red_neuron_props["vth"],
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
