import sys, json, time, os
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from app.stage5_translate import translate_irac

TEST_CASES = [
    {
        "name": "Case 1: Counterfeit Currency (BNS 180)",
        "irac": {
            "issue": "Whether a person found in possession of counterfeit currency notes on September 5, 2024, can be prosecuted under BNS 2023.",
            "rule": "Whoever has in his possession any forged or counterfeit coin, stamp, currency-note or bank-note, knowing or having reason to believe the same to be forged or counterfeit and intending to use the same as genuine or that it may be used as genuine, shall be punished with imprisonment of either description for a term which may extend to seven years, or with fine, or with both.",
            "application": "On September 5, 2024, the individual was found in possession of counterfeit currency notes with knowledge of their nature, which directly satisfies the elements under Section 180 of BNS 2023.",
            "conclusion": "The individual may be punished under Section 180 of BNS 2023 for possession of counterfeit currency notes."
        }
    },
    {
        "name": "Case 2: Riot Liability of Agent (BNS 193)",
        "irac": {
            "issue": "The issue is whether the law governing the agent's liability for a riot that occurred on August 10, 2024, can be determined based on the provided statutory text.",
            "rule": "Whenever a riot is committed for the benefit or on behalf of any person who is the owner or occupier of any land respecting which such riot takes place, the agent or manager of such person shall be punishable with fine, if such agent or manager, having reason to believe that such riot was likely to be committed, shall not use all lawful means in his power to prevent such assembly or riot.",
            "application": "The statutory text establishes that if a riot is committed for the benefit of a landowner on August 10, 2024, the agent who fails to take all lawful means to prevent it is punishable with fine.",
            "conclusion": "The law governing the agent's liability for a riot occurring on August 10, 2024, is governed by Section 193 of BNS 2023."
        }
    },
    {
        "name": "Case 3: Obscene Magazines / Books (IPC 292)",
        "irac": {
            "issue": "The issue is whether the law applicable to a bookstore owner who sold obscene magazines on June 25, 2024, for the first time.",
            "rule": "Whoever sells, lets to hire, distributes, publicly exhibits or in any manner puts into circulation any obscene book, pamphlet, paper, drawing, painting, representation or figure shall be punished on first conviction with imprisonment for a term which may extend to two years, and with fine.",
            "application": "The bookstore owner sold obscene magazines on June 25, 2024, prior to the July 1 cutoff, which falls directly under IPC Section 292 for a first-time offense.",
            "conclusion": "Therefore, the law applicable to the bookstore owner is IPC Section 292."
        }
    }
]

print("=== RUNNING MULTILINGUAL TRANSLATION (HINDI & MARATHI) ===\n")

for idx, case in enumerate(TEST_CASES, 1):
    print("=" * 80)
    print(f"CASE {idx}: {case['name']}")
    print("=" * 80)
    
    t_start = time.time()
    hi_irac, _, _, _ = translate_irac(case["irac"], "hi")
    mr_irac, _, _, _ = translate_irac(case["irac"], "mr")
    elapsed = time.time() - t_start
    print(f"[Translation time: {elapsed:.2f}s]\n")
    
    for field in ["issue", "rule", "application", "conclusion"]:
        print(f"--- {field.upper()} ---")
        print(f"[English]:\n{case['irac'][field]}\n")
        print(f"[Hindi (hi)]:\n{hi_irac[field]}\n")
        print(f"[Marathi (mr)]:\n{mr_irac[field]}\n")
    print("\n")
