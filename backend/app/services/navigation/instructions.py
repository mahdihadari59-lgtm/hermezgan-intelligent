from __future__ import annotations

from typing import Any


class InstructionExtractor:
    MANEUVERS = {
        ("turn", "left"): "به چپ بپیچید",
        ("turn", "right"): "به راست بپیچید",
        ("turn", "slight left"): "کمی به چپ بروید",
        ("turn", "slight right"): "کمی به راست بروید",
        ("turn", "sharp left"): "تند به چپ بپیچید",
        ("turn", "sharp right"): "تند به راست بپیچید",
        ("merge", ""): "مسیر را ادغام کنید",
        ("on ramp", ""): "وارد رمپ شوید",
        ("off ramp", ""): "از رمپ خارج شوید",
        ("fork", "left"): "در دو راهی به چپ بروید",
        ("fork", "right"): "در دو راهی به راست بروید",
        ("roundabout", ""): "وارد میدان شوید",
        ("new name", ""): "ادامه مسیر",
        ("continue", ""): "مستقیم ادامه دهید",
        ("depart", ""): "حرکت کنید",
        ("arrive", ""): "به مقصد رسیدید",
        ("uturn", ""): "دور بزنید",
    }

    @classmethod
    def _text(cls, step: dict[str, Any]) -> str:
        maneuver = step.get("maneuver") or {}
        mtype = str(maneuver.get("type") or "")
        modifier = str(maneuver.get("modifier") or "")
        name = str(step.get("name") or "").strip()

        base = cls.MANEUVERS.get(
            (mtype, modifier),
            cls.MANEUVERS.get((mtype, ""), "ادامه مسیر"),
        )

        distance = float(step.get("distance") or 0)

        if mtype == "arrive":
            return "به مقصد رسیدید."

        if name:
            if mtype in {"turn", "merge", "fork", "on ramp", "off ramp"}:
                base = f"{base} به مسیر {name}"

        if distance > 0 and mtype != "depart":
            if distance >= 1000:
                return f"{base}؛ حدود {distance / 1000:.1f} کیلومتر دیگر."
            return f"{base}؛ حدود {int(distance)} متر دیگر."

        return base

    @classmethod
    def extract(cls, route_data: dict[str, Any]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []

        for leg in route_data.get("route", {}).get("legs", []):
            for step in leg.get("steps", []):
                maneuver = step.get("maneuver") or {}
                output.append(
                    {
                        "text": cls._text(step),
                        "distance_m": round(float(step.get("distance") or 0), 1),
                        "duration_s": round(float(step.get("duration") or 0), 1),
                        "name": step.get("name"),
                        "maneuver": maneuver,
                        "geometry": step.get("geometry"),
                    }
                )

        return output
