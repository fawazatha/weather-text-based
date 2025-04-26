```mermaid
flowchart TD
    subgraph KANLinear_Unit
        X[Input x_i] --> ACT[SiLU Activation]
        ACT --> B[Linear Transform W_base_ji]
        X --> BS[B-Spline Basis B(x_i)]
        
        %% parameters subgraph
        subgraph Parameters
            Wb[W_base_ji]
            Ws[W_spline_ji…]
            Ss[S_spline_ji]
            Grid[Adaptive Grid G_i]
            Bias[b_kan_j]
        end
        
        %% combine spline terms
        BS --> SC[Scaled Spline Combination]
        Wb --> B
        Ws --> SC
        Ss --> SC
        Grid --> BS
        
        %% sum and output
        B --> SUM((Σ))
        SC --> SUM
        Bias --> SUM
        SUM --> Y[Output y_j]
    end

    %% styling
    style B fill:#f9f,stroke:#333,stroke-width:1px
    style BS fill:#ccf,stroke:#333,stroke-width:1px
    style SC fill:#ccf,stroke:#333,stroke-width:1px
    style ACT fill:#fef,stroke:#333,stroke-width:1px
    style Parameters stroke-dasharray:5 5,fill:#fff
```
