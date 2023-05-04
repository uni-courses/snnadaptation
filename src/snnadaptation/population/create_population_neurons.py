"""Creates the different redundant population neurons, per neruon type.

TODO: check multiplies with 0, e.g. vth*red_level with vth =0.
"""
from typing import Dict, List

import networkx as nx
from typeguard import typechecked


@typechecked
def get_population_neuron_properties(
    *, adaptation_graph: nx.DiGraph, node_name: str, red_level: int
) -> Dict[str, float]:
    """Returns the neuron properties for population coding, per neuron type."""

    unchanged_neuron_identifiers: List[str] = [
        "spike_once",
        "rand",
        "degree_receiver",
    ]
    red_neuron_props: Dict[str, float] = {}
    set_unchanged_neuron_properties(
        adaptation_graph=adaptation_graph,
        node_name=node_name,
        red_neuron_props=red_neuron_props,
    )
    if any(
        unchanged_node_name in node_name
        for unchanged_node_name in unchanged_neuron_identifiers
    ):
        return red_neuron_props
    if "selector" in node_name:
        set_population_selector_neuron_properties(
            red_level=red_level,
            red_neuron_props=red_neuron_props,
        )
    elif "counter" in node_name:
        set_population_counter_neuron_properties(
            red_level=red_level,
            red_neuron_props=red_neuron_props,
        )
    elif "next_round" in node_name:
        set_population_next_round_neuron_properties(
            red_level=red_level,
            red_neuron_props=red_neuron_props,
        )
    elif "terminator" in node_name:
        set_population_terminator_neuron_properties(
            red_level=red_level,
            red_neuron_props=red_neuron_props,
        )
    else:
        raise ValueError(f"Error, {node_name} not supported.")
    return red_neuron_props


@typechecked
def set_unchanged_neuron_properties(
    *,
    adaptation_graph: nx.DiGraph,
    node_name: str,
    red_neuron_props: Dict[str, float],
) -> None:
    """These neuron types are unchanged for the MDSA algorithm."""
    red_neuron_props["bias"] = adaptation_graph.nodes[node_name]["nx_lif"][
        0
    ].bias.get()
    red_neuron_props["du"] = adaptation_graph.nodes[node_name]["nx_lif"][
        0
    ].du.get()
    red_neuron_props["dv"] = adaptation_graph.nodes[node_name]["nx_lif"][
        0
    ].dv.get()
    red_neuron_props["vth"] = adaptation_graph.nodes[node_name]["nx_lif"][
        0
    ].vth.get()


@typechecked
def set_population_selector_neuron_properties(
    *,
    red_level: int,
    red_neuron_props: Dict[str, float],
) -> None:
    """The selector neuron needs a bias and vth multiplication with red_level.

    The selector neurons for m=0 should fire at t=0. The selector
    neurons for m=1 should fire when the next round neuron(s) have
    fired.
    """
    red_neuron_props["bias"] = red_neuron_props["bias"] * red_level
    red_neuron_props["vth"] = red_neuron_props["vth"] * red_level


@typechecked
def set_population_counter_neuron_properties(
    *,
    red_level: int,
    red_neuron_props: Dict[str, float],
) -> None:
    """The counter_y_neurons need a vth of red_level-1 because they should
    spike as soon as the accompanying  (population of) degree_receiver_x_y_z
    neuron(s) has fired."""
    red_neuron_props["vth"] = float(red_level - 1)


@typechecked
def set_population_next_round_neuron_properties(
    *,
    red_level: int,
    red_neuron_props: Dict[str, float],
) -> None:
    """The next_round neurons need a vth multiplication with red_level because
    they should spike as soon as 1 degree_receiver neuron per node-circuit has
    fired."""
    red_neuron_props["vth"] = red_neuron_props["vth"] * red_level


@typechecked
def set_population_terminator_neuron_properties(
    *,
    red_level: int,
    red_neuron_props: Dict[str, float],
) -> None:
    """The counter_y_neurons need a vth multiplication with red_level because
    they should spike as soon as 1 degree_receiver neuron per node-circuit has
    fired."""
    red_neuron_props["vth"] = red_neuron_props["vth"] * red_level
