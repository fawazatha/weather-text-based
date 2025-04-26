```mermaid
graph TD
    subgraph KANLinear_Unit
        X[Input x_i] --> ACT[SiLU Activation]
        ACT --> B[Linear Transform W_base_ji]
        X --> BS[B-Spline Basis B(x_i)]
        subgraph Parameters
            Wb[W_base_ji] --> B
            Ws[W_spline_ji...] --> SC
            Ss[S_spline_ji] --> SC
            Grid[Adaptive Grid G_i] --> BS
            Bias[b_kan_j] --> SUM
        end
        BS --> SC[Scaled Spline Combination]
        B --> SUM((Σ))
        SC --> SUM
        SUM --> Y[Output y_j]
    end

    style B fill:#f9f,stroke:#333,stroke-width:1px
    style BS fill:#ccf,stroke:#333,stroke-width:1px
    style SC fill:#ccf,stroke:#333,stroke-width:1px
    style ACT fill:#fef,stroke:#333,stroke-width:1px
    style Parameters stroke-dasharray: 5 5, fill: #fff

```
