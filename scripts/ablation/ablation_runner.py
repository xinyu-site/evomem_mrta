import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

# Dataset list reused across all ablations
DATASETS = [
    "MT_MR_TA",
    "MT_SR_TA",
    "ST_SR_IA",
    "MT_MR_IA",
    "ST_SR_TA",
    "ST_MR_TA",
    "ST_MR_IA",
    "MT_SR_IA",
]

RUNNER_NAME = "run_exp_batch_insist.py"


def run_ablation(tag, num_problems, *, use, useab, record, evolve, forget, check):
    """
    Patch run_exp_batch_insist.py in a temp copy with the given flags and run it.
    """
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    runner_path = repo_root / RUNNER_NAME
    code = runner_path.read_text(encoding="utf-8")

    block = "datasets_configs = [\n" + ",\n".join(
        f"    {{'dataset': '{ds}', 'useab': '{useab}','use': '{use}','record': '{record}','check':'{check}','evolve':'{evolve}','forget':'{forget}'}}"
        for ds in DATASETS
    ) + "\n]\n"

    code = re.sub(r"datasets_configs = \[[\s\S]*?\]\n", block, code, count=1)
    code = re.sub(r"num_problems_per_dataset = \d+", f"num_problems_per_dataset = {num_problems}", code, count=1)

    print(f"[{tag}] use={use} useab={useab} record={record} evolve={evolve} forget={forget} check={check} num={num_problems}")
    run_cmd = [sys.executable, "-c", code]
    try:
        tmp_dir = pathlib.Path(tempfile.gettempdir())
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp = tmp_dir / f"{runner_path.stem}_{tag}.py"
        tmp.write_text(code, encoding="utf-8")
        run_cmd = [sys.executable, str(tmp)]
    except Exception as exc:
        print(f"[{tag}] temp file unavailable; running inline. ({type(exc).__name__})")

    subprocess.run(run_cmd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Run an ablation by patching run_exp_batch_insist.py in a temp copy.",
    )
    parser.add_argument("--tag", required=True, help="Name suffix for the temp script file")
    parser.add_argument("--num", type=int, default=25, help="Number of problems per dataset")
    parser.add_argument("--use", default="true", help="use memory (true/false)")
    parser.add_argument("--useab", default="true", help="use abstract memory (true/false)")
    parser.add_argument("--record", default="true", help="record/evolve memory (true/false)")
    parser.add_argument("--evolve", default="true", help="evolve abstract memory (true/false)")
    parser.add_argument("--forget", default="true", help="enable forgetting mechanism (true/false)")
    parser.add_argument("--check", default="true", help="enable memory check/correction (true/false)")
    args = parser.parse_args()

    run_ablation(
        tag=args.tag,
        num_problems=args.num,
        use=args.use.lower(),
        useab=args.useab.lower(),
        record=args.record.lower(),
        evolve=args.evolve.lower(),
        forget=args.forget.lower(),
        check=args.check.lower(),
    )


if __name__ == "__main__":
    main()
