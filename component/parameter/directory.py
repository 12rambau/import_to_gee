from pathlib import Path

module_res_dir = Path("~", "module_results").expanduser()
module_res_dir.mkdir(exist_ok=True)

down_dir = module_res_dir.joinpath("aoi")
down_dir.mkdir(exist_ok=True)
