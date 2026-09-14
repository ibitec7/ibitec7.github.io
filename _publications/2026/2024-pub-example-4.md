---
title:         "BXINT4: Geometry-Preserving Block-Scaled INT4 Training with Structured Sparsity" 
date:           2026-07-24 00:00:00 +0800
selected:       true
pub:            "Currently working in collaboration with NVIDIA AI Technology Center"
#  pub_pre:        "Currently working in collaboration with NVIDIA AI Technology Center"
    # pub_post:       'Pending decision.'
# pub_last:       ' <span class="badge badge-pill badge-publication badge-success">Spotlight</span>'
pub_date:       "2026"
# semantic_scholar_id: 204e3073870fae3d05bcbc2f6a8e263d9b72e776  # use this to retrieve citation count
# abstract: "Low-precision datatypes have accelerated the training of large language models. However, the dominant 4-bit training formats are available only on modern GPU architectures such as NVIDIA’s Blackwell GPUs. Legacy Ampere and Turing GPUs contain a dormant INT4 tensor core path, exploited for inference but never for training. We propose BXINT4, a training-grade 4-bit datatype that combines signed INT4 codes with a shared FP16 block scale along the reduction dimension, structurally equivalent to microscaling (Appendix A) but adapted for integer codes on legacy hardware. The core scientific insight is operator geometry preservation: rather than minimizing pointwise weight error, BXINT4 preserves each layer’s input–output behavior under the data-weighted metric dµ (Section 1.2), ensuring that the quantized network computes approximately what the full-precision network would compute. We operationalize this via Hadamard-CASS: a blockwise randomized Hadamard transform applied before quantization reduces the within-block crest factor, enabling exact covariance-weighted scale selection on better-conditioned coordinates. On the systems side, BXINT4 targets Ampere’s INT4 tensor core instruction, which combined with 2:4 structured sparsity delivers an 8× arithmetic ceiling over FP16. The sparse extension, G4 (Section 3.4), applies S-STE continuous soft-threshold on Hadamard-transformed weights together with a log-barrier regularizer whose functional form is drawn from recent implicit-bias theory. BXINT4 is the first datatype designed for the legacy INT4 MMA + Sparse Tensor Core computation path, making competitive 4-bit training available on the enormous installed base of Ampere and Turing GPUs."
#  Photo by Pineapple Supply Co. on Unsplash. Please put a tldr (too-long-didnt-read, 1~2 sentences) of your publication here. It is not recommended to put the actual abstract here because it is usually too long to fit in. $\LaTeX$ is supported. $a=b+c$.
# cover:          /assets/images/covers/cover3.jpg
authors:
  - Syed Ibrahim Omer
  - Ginny Y. Wong
  - Haoliang Li
links:
  # Work in progress: the repository and manuscript stay private until the
  # paper is out, so no public link is published here yet.
---
