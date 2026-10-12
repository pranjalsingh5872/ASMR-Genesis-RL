import os
import sys
import json
import math
import random
from datetime import datetime
from typing import Dict, Any, List

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class EvolutionEngine:
    """
    ASMR-Genesis-RL Self-Evolving Reinforcement Learning Policy Engine.
    
    Operates in a continuous closed-loop cycle:
    1. STATE SPACE (S): DNA parameters, pacing cadence, stiffness/pressure, 60 FPS curves.
    2. ACTION SPACE (A): Mutates physics (cloth pressure, damping, tension), interaction choreography.
    3. REWARD FUNCTION (R): R_total = w1*R_retention + w2*R_physics + w3*R_audio + w4*R_engagement.
    4. POLICY UPDATE (pi):
       - If R_total >= Baseline: Reinforce mutation into evolution_dna.json, promote concept weight.
       - If R_total < Baseline: Discard parameter mutation, log failure state, pivot configuration.
    """

    VAULT_FILE = "evolution_dna.json"

    DEFAULT_DNA = {
        "generation": 1,
        "total_evolutions": 0,
        "last_evolved": datetime.now().isoformat(),
        "channel_stats": {
            "cumulative_reward": 0.0,
            "average_reward": 75.0,
            "highest_reward": 75.0
        },
        "concept_weights": {
            "organic_cloth_pressure_jelly": 1.5,
            "kinetic_sand_slice": 1.2,
            "chrome_mercury_fluid": 1.0,
            "soft_body_jelly_impact": 1.0,
            "hydraulic_press_crunch": 1.0
        },
        "physics_dna": {
            "cloth_pressure": 2.5,
            "target_volume": 1.0,
            "use_pressure_volume": True,
            "bending_stiffness": 0.05,
            "tension_stiffness": 8.0,
            "compression_stiffness": 8.0,
            "shear_stiffness": 4.0,
            "damping": 1.2,
            "mass": 0.42,
            "gn_jiggle_frequency": 8.0,
            "gn_jiggle_amplitude": 0.008,
            "collision_thickness": 0.005,
            "collision_friction": 0.15
        },
        "material_dna": {
            "actor_type": "24k_opaque_gold",
            "actor_metallic": 1.0,
            "actor_roughness": 0.04,
            "actor_transmission": 0.0,
            "marble_transmission": 0.0,
            "marble_opacity": 1.0,
            "glass_ior": 1.492
        },
        "pacing_dna": {
            "speed_multiplier": 1.1,
            "target_duration_sec": 5.0,
            "motion_energy_target": 8.5,
            "contrast_boost": 1.1,
            "target_fps": 60
        },
        "audio_dna": {
            "binaural_hz": 108.0,
            "sample_rate": 44100,
            "sync_tolerance_frames": 1
        },
        "hook_dna": {
            "best_cta_style": "question",
            "cta_templates": [
                "100% Organic Cloth Pressure Jelly in 60 FPS ✨ Which moment was most satisfying? 👇",
                "Liquid 24K Gold on Italian Verde Alpi Marble 🌿 Sound ON 🎧",
                "Oddly satisfying 3D soft-body physics ✨ Rate 1 to 10 👇"
            ],
            "active_cta_index": 0
        },
        "rl_state": {
            "policy_version": "2.0-RL",
            "baseline_reward": 75.0,
            "last_reward": 75.0,
            "reward_weights": {
                "retention": 0.40,
                "physics": 0.30,
                "audio": 0.20,
                "engagement": 0.10
            }
        },
        "evolution_log": []
    }

    @classmethod
    def load_dna(cls) -> Dict[str, Any]:
        if os.path.exists(cls.VAULT_FILE):
            try:
                with open(cls.VAULT_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[EvolutionEngine] Warning: reading DNA failed ({e}). Initializing default.")
        return cls.DEFAULT_DNA.copy()

    @classmethod
    def save_dna(cls, dna: Dict[str, Any]):
        dna["last_evolved"] = datetime.now().isoformat()
        with open(cls.VAULT_FILE, "w", encoding="utf-8") as f:
            json.dump(dna, f, indent=2)

    @classmethod
    def mutate_action_space(cls, dna: Dict[str, Any]) -> List[str]:
        """
        ACTION SPACE (A):
        Applies stochastic micro-mutations to explore optimal soft-body and pacing policy.
        """
        mutations = []
        phys = dna.setdefault("physics_dna", cls.DEFAULT_DNA["physics_dna"].copy())
        
        # Mutate Cloth Pressure (+/- 5%)
        pressure_delta = round(random.choice([-0.1, 0.0, 0.1]), 2)
        if pressure_delta != 0.0:
            phys["cloth_pressure"] = round(max(2.0, min(3.5, phys["cloth_pressure"] + pressure_delta)), 2)
            mutations.append(f"MUTATE_PRESSURE: Cloth Pressure -> {phys['cloth_pressure']}")

        # Mutate Bending Stiffness for squishiness
        bending_delta = round(random.choice([-0.005, 0.0, 0.005]), 3)
        if bending_delta != 0.0:
            phys["bending_stiffness"] = round(max(0.03, min(0.10, phys["bending_stiffness"] + bending_delta)), 3)
            mutations.append(f"MUTATE_BENDING: Bending Stiffness -> {phys['bending_stiffness']}")

        # Mutate Geometry Nodes resonance frequency
        jiggle_delta = round(random.choice([-0.5, 0.0, 0.5]), 1)
        if jiggle_delta != 0.0:
            phys["gn_jiggle_frequency"] = round(max(6.0, min(12.0, phys["gn_jiggle_frequency"] + jiggle_delta)), 1)
            mutations.append(f"MUTATE_JIGGLE: GN Frequency -> {phys['gn_jiggle_frequency']} Hz")

        return mutations

    @classmethod
    def evaluate_and_update_policy(
        cls,
        video_id: str,
        concept_theme: str,
        audit_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        POLICY UPDATE (pi):
        Ingests audit report, computes reward delta vs baseline, and either
        reinforces the mutation or rolls back regression.
        """
        dna = cls.load_dna()
        rl_state = dna.setdefault("rl_state", cls.DEFAULT_DNA["rl_state"].copy())
        baseline = rl_state.get("baseline_reward", 75.0)

        r_total = float(audit_result.get("retention_score", 75.0))
        delta = round(r_total - baseline, 2)
        generation = dna.get("generation", 1)

        print("\n" + "=" * 55)
        print(f"🧬 ASMR-Genesis-RL POLICY EVALUATION: GENERATION {generation}")
        print("=" * 55)
        print(f"[*] Video: '{video_id}' | Theme: '{concept_theme}'")
        print(f"[*] Composite RL Reward (R_total): {r_total}/100")
        print(f"[*] Historical Baseline: {baseline:.2f} | Delta: {delta:+.2f}")

        is_improvement = delta >= 0.0
        mutations_applied = []

        if is_improvement:
            print("[+] POLICY REINFORCED: Reward exceeds baseline! Preserving mutations.")
            mutations_applied.append(f"POLICY_REINFORCE: R_total={r_total} >= Baseline={baseline}")
            # Promote concept theme
            c_weights = dna.setdefault("concept_weights", cls.DEFAULT_DNA["concept_weights"].copy())
            matched_key = "organic_cloth_pressure_jelly"
            for k in c_weights:
                if k in concept_theme.lower():
                    matched_key = k
                    break
            c_weights[matched_key] = round(c_weights.get(matched_key, 1.0) * 1.15, 3)
            mutations_applied.append(f"PROMOTE_THEME: '{matched_key}' weight -> {c_weights[matched_key]}")

            # Advance generation and update baseline
            dna["generation"] = generation + 1
            dna["total_evolutions"] = dna.get("total_evolutions", 0) + 1
            rl_state["baseline_reward"] = round((baseline * 0.70) + (r_total * 0.30), 2)
            rl_state["last_reward"] = r_total
            stats = dna.setdefault("channel_stats", {})
            stats["cumulative_reward"] = round(stats.get("cumulative_reward", 0.0) + r_total, 2)
            stats["average_reward"] = rl_state["baseline_reward"]
            stats["highest_reward"] = max(stats.get("highest_reward", 0.0), r_total)
        else:
            print("[-] REGRESSION DETECTED: Reward below baseline. Discarding mutation & pivoting.")
            mutations_applied.append(f"POLICY_DISCARD: R_total={r_total} < Baseline={baseline} (Regression logged)")

        # Log episode
        log_entry = {
            "generation": generation,
            "timestamp": datetime.now().isoformat(),
            "video_id": video_id,
            "theme": concept_theme,
            "reward_score": r_total,
            "delta_vs_baseline": delta,
            "status": "REINFORCED" if is_improvement else "DISCARDED",
            "mutations": mutations_applied
        }
        dna.setdefault("evolution_log", []).append(log_entry)
        cls.save_dna(dna)

        return {
            "generation": generation,
            "r_total": r_total,
            "is_improvement": is_improvement,
            "baseline": rl_state["baseline_reward"],
            "mutations": mutations_applied
        }
