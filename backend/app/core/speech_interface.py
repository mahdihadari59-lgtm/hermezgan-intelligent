#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from pathlib import Path


class BandariSpeechInterface:

    def __init__(self):
        self.root = (
            Path.home()
            / "hermezgan-intelligent"
            / "bandari-engine-2026"
            / "bandari-engine"
        )

    async def analyze(self, text):
        process = await asyncio.create_subprocess_exec(
            "node",
            str(self.root / "index.js"),
            "analyze",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            cwd=str(self.root),
        )
        stdout, _ = await process.communicate(
            json.dumps({"text": text}).encode()
        )
        return json.loads(stdout.decode())
