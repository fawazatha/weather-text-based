```mermaid
graph TD
    subgraph KANLinear_Unit_Mapping_Input_i_to_Output_j
        X[Input Feature x_i] --> ACT[Base Activation: SiLU(x_i)]
        ACT --> B[Linear Transform: W_base_ji]
        X --> BS[B-Spline Bases: B(x_i, G_i)]
        subgraph Learnable_Parameters
            Wb[W_base_ji] --> B
            Ws[W_spline_ji...] --> SC
            Ss[S_spline_ji] --> SC
            Grid[Adaptive Grid G_i] --> BS
            Bias[Bias b_kan_j] --> SUM
        end
        BS --> SC[Scaled Spline Combination]
        B --> SUM((Sum))]
        SC --> SUM
        SUM --> Y[Output y_j]
    end

    style B fill:#f9f,stroke:#333,stroke-width:1px
    style BS fill:#ccf,stroke:#333,stroke-width:1px
    style SC fill:#ccf,stroke:#333,stroke-width:1px
    style ACT fill:#fef,stroke:#333,stroke-width:1px
    style Learnable_Parameters stroke-dasharray: 5 5, fill: #fff
```
