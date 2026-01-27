from ablation_runner import run_ablation


if __name__ == "__main__":
    run_ablation(
        tag="no_forget",
        # num_problems=25,
        num_problems=10,
        use="true",
        useab="true",
        record="true",
        evolve="true",
        forget="false",
        check="true",
    )
