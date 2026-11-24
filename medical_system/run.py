"""应用入口：python medical_system/run.py"""
from __future__ import annotations

import os

from medical_system.app_factory import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
