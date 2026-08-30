from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import traceback

from app import main


root = Path(__file__).resolve().parent
log_path = root / "data" / "app.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
with log_path.open("a", encoding="utf-8") as log, redirect_stdout(log), redirect_stderr(log):
    try:
        main()
    except Exception:
        traceback.print_exc(file=log)

