from ablation_runner import run_ablation


if __name__ == "__main__":
    run_ablation(
        tag="no_record_80",
        num_problems=10,  # 8 datasets * 10 problems = 80 tasks
        use="true",
        useab="true",
        record="false",
        evolve="false",
        forget="false",
        check="false",
    )
