import subprocess

import dotenv

dotenv.load_dotenv(".env.test")
subprocess.run(["prisma", "migrate", "dev"], check=True)  # noqa: S607
