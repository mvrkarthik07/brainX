import argparse
import logging
import os
import sys
from pathlib import Path

import uvicorn

# Ensure project root is importable when running as a sidecar.
# sidecar_main.py is at: brainX/apps/api/sidecar_main.py
# parents[2] = brainX project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.api.main import app  # noqa: E402


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("brainx.sidecar")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="BrainX backend sidecar")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("BRAINX_PORT", "8765")),
    )

    args = parser.parse_args(argv)

    logger.info("Starting BrainX sidecar on %s:%s", args.host, args.port)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=False,
        access_log=False,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))