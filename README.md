flowchart TD
  %% Backbone
  subgraph ResNet-18 Backbone
    A["Input: 32×32×3 Image"]
    A -->|Conv3×3,64, ReLU| B1["Conv1 + BN + ReLU"]
    B1 -->|2×| RB1["ResBlock (64 ch)"]
    RB1 -->|2×| RB2["ResBlock (128 ch), stride=2"]
    RB2 -->|2×| RB3["ResBlock (256 ch), stride=2"]
    RB3 -->|2×| RB4["ResBlock (512 ch), stride=2"]
    RB4 --> C["AdaptiveAvgPool2d (1×1)"]
    C --> D["Flatten → 512-D Vector"]
  end

  %% Choice of head
  subgraph Head Choice
    direction LR
    D --> E1["Linear Head\n(if is_kan=False)"]
    D --> E2["KANLinear Head\n(if is_kan=True)"]
  end

  %% MLP Path
  subgraph MLP Head
    E1 --> F1["Logits (100-D)"]
    F1 --> G1["Softmax → Class Probabilities"]
  end

  %% KAN Path
  subgraph KAN Head
    E2 --> H1["Base Path: SiLU → Linear"]
    E2 --> H2["Spline Path: B-Spline → Linear"]
    H1 & H2 --> I["Sum → Logits (100-D)"]
    I --> G2["Softmax → Class Probabilities"]
  end
