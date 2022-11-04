# Brain-Adaptation for Spiking Neural Networks

[![Python 3.10][python_badge]](https://www.python.org/downloads/release/python-3106/)
[![License: AGPL v3][agpl3_badge]](https://www.gnu.org/licenses/agpl-3.0)
[![Code Style: Black][black_badge]](https://github.com/ambv/black)
[![Code Coverage][codecov_badge]](https://codecov.io/gh/a-t-0/snnadaptation)

This repository contains brain-adaptation mechanisms to spiking neural networks
with the purpose of increasing their radiation robustness.

## Parent Repository

These algorithms can be analysed using
[this parent repository](https://github.com/a-t-0/snncompare).
Together, these repos can be used to investigate the effectivity of various
[brain-adaptation] mechanisms applied to these algorithms, in order to increase
their [radiation] robustness. You can run it on various backends, as well as on
a custom LIF-neuron simulator.

## Algorithms

Different SNN implementations may use different encoding schemes, such as
sparse coding, population coding and/or rate coding. In population coding,
adaptation may be realised in the form of larger populations, whereas in rate
coding, adaptation may be realised through varying the spike-rate. This implies
that different algorithms may benefit from different types of adaptation.
Hence, an overview is included of the implemented SNN algorithms and their
respective compatibilities with adaptation and radiation implementations:

| Algorithm                            | Encoding | Adaptation | Radiation    |
| ------------------------------------ | -------- | ---------- | ------------ |
| Minimum Dominating Set Approximation | Sparse   | Redundancy | Neuron Death |
|                                      |          |            |              |
|                                      |          |            |              |

<!-- Un-wrapped URL's (Badges and Hyperlinks) -->

[agpl3_badge]: https://img.shields.io/badge/License-AGPL_v3-blue.svg
[black_badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[brain-adaptation]: https://github.com/a-t-0/snnadaptation
[codecov_badge]: https://codecov.io/gh/a-t-0/snn/branch/main/graph/badge.svg
[python_badge]: https://img.shields.io/badge/python-3.10-blue.svg
[radiation]: https://github.com/a-t-0/snnradiation
