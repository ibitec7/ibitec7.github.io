---
title:          "MaRK: Markov-adapted Recurrent Kernels for Dynamic Operator Conditioning in State Space Models"
date:           2026-05-05 00:00:00 +0800
selected:       true
pub:            "Submitted to NeurIPS 2026 (Pending Decision)"
#  pub_pre:        "Submitted to NeurIPS 2026"
#  pub_post:       'Pending decision.'
# pub_last:       ' <span class="badge badge-pill badge-publication badge-success">Spotlight</span>'
pub_date:       "2026"
# semantic_scholar_id: 204e3073870fae3d05bcbc2f6a8e263d9b72e776  # use this to retrieve citation count
# abstract: "State Space Models (SSMs) offer an efficient alternative to Transformers for sequence modeling, yet  conditioning pre-trained SSMs for iterative generation typically operates outside the recurrent operator, through input injection or activation modulation. While such mechanisms expose the model to conditioning information, they leave the underlying temporal dynamics fixed. We introduce MaRK (Markov-adapted Recurrent Kernels), a dynamic operator-conditioning framework that maps context vectors directly into bounded modulations of a frozen SSM's recurrence ($A$), read-in ($B$), read-out ($C$), skip ($D$), and discretization ($/Delta$) parameters. Viewed through the lens of Linear Parameter-Varying systems, MaRK induces a context-indexed family of Markov parameter sequences, allowing each diffusion timestep to reshape the model's input-output memory kernel. We instantiate MaRK on a frozen 111M-parameter Hydra SSM backbone and study three adapter geometries Hypernet, Chebyshev polynomial, and Discrete Cosine Transform kernels. Since these adapters modify the Markov parameter sequence through low-rank auxiliary maps on the frozen backbone, parameter-efficient fine-tuning arises as a structural consequence of the adaptation mechanism itself, requiring only 7.5--13M trainable auxiliary parameters to transition from a bidirectional objective to an iterative diffusion regime. The bounded recurrence parameterization further yields an analytic Affine Quadratic Stability certificate for the modulated recurrence. Through synthetic LPV recovery experiments and Markov-operator diagnostics, we show that MaRK recovers coordinate-invariant temporal operators under matched assumptions and produces distinct, stable timestep-conditioned memory profiles. Empirically, the Chebyshev variant yields the strongest performance, achieving an average validation loss of 2.63, followed by the DCT (2.66) and Hypernet (3.60) geometries. Together, these results provide initial evidence that dynamic operator modulation is a principled operator-level conditioning mechanism for adapting SSMs beyond input-stream injection and adaptive normalization."
#  Photo by Pineapple Supply Co. on Unsplash. Please put a tldr (too-long-didnt-read, 1~2 sentences) of your publication here. It is not recommended to put the actual abstract here because it is usually too long to fit in. $\LaTeX$ is supported. $a=b+c$.
# cover:          /assets/images/covers/cover3.jpg
authors:
  - Syed Ibrahim Omer
  - Ginny Y. Wong
  - Xiangyu Zhao
links:
  Code: https://github.com/ibitec7/mark
  Paper: https://openreview.net/pdf?id=yIjFWwvG7b
  OpenReview: https://openreview.net/forum?id=yIjFWwvG7b#discussion
---
