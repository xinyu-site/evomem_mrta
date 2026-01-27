from ablation_runner import run_ablation


if __name__ == "__main__":
    run_ablation(
        tag="no_memory",
        # num_problems=25,
        num_problems=10,
        use="false",
        useab="false",
        record="false",
        evolve="false",
        forget="false",
        check="false",
    )
