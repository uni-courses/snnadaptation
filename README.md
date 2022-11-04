# SNN Adaptation

This repository contains brain-adaptation mechanisms to spiking neural networks
with the purpose of increasing their radiation robustness.

## Parent Repository

These algorithms can be analysed using
[this parent repository](https://github.com/a-t-0/snncompare).
Together, these repos can be used to investigate the effectivity of various
brain-adaptation mechanisms applied to these algorithms, in order to increase
their radiation robustness. You can run it on various backends, as well as on
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
