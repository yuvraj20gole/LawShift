# Split-Offense Review — Batch 1 (1-20 of 161)

For each case, judge:
1. Is this GENUINELY a split/continuing-offense case (real conduct straddling 1 July 2024), or a false positive (e.g. two unrelated dates, one procedural)?
2. If genuine: does the correct answer need TWO periods (IPC for early acts, BNS for later/continuing acts), or does it actually resolve to ONE law despite having two dates?
3. Note if GovIntel's own reply is internally inconsistent or self-corrects (as seen in Case 3/4 before) — don't treat their answer as automatic gold truth.

---

## Case 1

**Split:** train

**Dates found in question:** July 5, 2024, June 25, 2024

**Parsed dates:** 2024-06-25, 2024-07-05

**Question:**
A person accepted money to recover stolen property on June 25, 2024, and recovered the property on July 5, 2024, without apprehending the offender. Which law applies?

**Assistant reply:**
The offense was committed when the money was accepted on June 25, 2024, with the subsequent failure to apprehend. Therefore, IPC Section 215 applies. BNS Section 252 corresponds to IPC Section 215.

Legal Analysis (IRAC):
Issue: Determining applicable law when payment was accepted before July 1 but recovery occurred after.
Rule: The offense is complete upon acceptance of payment for recovery without intent to apprehend.
Application: The acceptance on June 25, 2024, completed the offense. The subsequent recovery on July 5 does not change the date of offense.
Conclusion: IPC Section 215 applies as the offense was committed on June 25, 2024.

Core legal principle: The offense is complete upon acceptance of payment with failure to apprehend, determining the applicable law.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 2

**Split:** train

**Dates found in question:** August 15, 2024, January 10, 2024

**Parsed dates:** 2024-01-10, 2024-08-15

**Question:**
A company accountant is accused of forging a valuable security (promissory note) on January 10, 2024, possessing it until March 2024, and using it to obtain bank credit on August 15, 2024. The prosecution seeks to introduce electronic records of the forged document. What is the complete procedural and evidentiary framework governing this multi-phase offense?

**Assistant reply:**
This involves three distinct phases with different legal frameworks: (1) Creation (January 10, 2024): Governed by IPC Section 467 as substantive law; (2) Possession (March 2024): IPC Section 473 (possession of forged document) or BNS Section 339 if continuing into post-July period; (3) Use (August 15, 2024): BNS Section 340 (using forged document as genuine). Under BNSS Section 176, the investigation must follow procedure for cognizable offenses. Under BNSS Section 105, search and seizure of electronic records must be recorded through audio-video electronic means. Under BSA Section 63, electronic records are admissible if produced by computer or communication device. Under BSA Section 39, expert opinion is required to authenticate electronic forgery. Under BSA Section 41, handwriting expert opinion is relevant for the physical document. Under BNSS Section 349, specimen signatures may be ordered for comparison. The trial would be before a Magistrate under BNSS Section 21, with charges framed under BNSS Section 234-236.

Legal Analysis (IRAC):
Issue: What legal framework applies to creation, possession, and use of forged document spanning IPC-BNS transition with electronic evidence?
Rule: Each phase governed by law in force at that time; electronic evidence requires BNSS 105 procedural compliance and BSA 63/39 expert authentication.
Application: Creation: IPC 467; Possession: IPC 473/BNS 339; Use: BNS 340. Electronic records require BNSS 105 audio-video recording, BSA 63 admissibility, BSA 39 expert opinion, BSA 41 handwriting analysis.
Conclusion: Multi-layered legal framework applies with temporal segmentation for substantive law and integrated procedural/evidentiary requirements under BNSS/BSA.

Core legal principle: Multi-phase document offenses spanning IPC-BNS transition require separate analysis of each phase; electronic evidence requires BNSS 105 audio-video recording and BSA 63/39 expert authentication.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 3

**Split:** train

**Dates found in question:** July 15, 2024, June 15, 2024

**Parsed dates:** 2024-06-15, 2024-07-15

**Question:**
If the same bookstore owner had sold the obscene magazines on July 15, 2024 instead of June 15, 2024, which statute would apply and what would be the key procedural differences?

**Assistant reply:**
On July 15, 2024, BNS 2023 Section 294 would apply instead of IPC 1860 Section 292, as the BNS came into force on July 1, 2024. The substantive offense elements remain substantially similarâ€”sale of obscene books with the same Hicklin-based obscenity test. Procedurally, BNSS Section 98 forfeiture and BNSS Section 501 destruction orders remain applicable. However, BNS Section 294 now explicitly consolidates the punishment provision (previously in IPC Section 294), providing imprisonment up to two years, or fine, or both for first conviction, and up to five years for subsequent convictions. The BSA evidence framework remains unchanged.

Legal Analysis (IRAC):
Issue: Which statute governs obscene book sales after July 1, 2024?
Rule: BNS 2023 came into force July 1, 2024, repealing IPC 1860. BNS Section 294 corresponds to IPC 292 with consolidated punishment.
Application: July 15, 2024 falls under BNS jurisdiction. The offense structure remains similar but punishment is now explicitly in BNS 294 rather than cross-referenced.
Conclusion: BNS Section 294 applies post-July 1, 2024, with BNSS 98 and 501 procedures remaining constant.

Core legal principle: Temporal jurisdiction determines IPC vs. BNS applicability with July 1, 2024 as the cutoff; BNS 294 consolidates punishment previously in IPC 294.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 4

**Split:** train

**Dates found in question:** July 10, 2024, July 5, 2024, June 28, 2024

**Parsed dates:** 2024-06-28, 2024-07-05, 2024-07-10

**Question:**
A person removed revenue stamps from documents on June 28, 2024, but was not discovered until July 10, 2024. The stamps were reused on July 5, 2024. Which law governs the removal and the reuse?

**Assistant reply:**
The removal on June 28, 2024 is governed by the Indian Penal Code because it occurred before July 1, 2024. The reuse on July 5, 2024 constitutes a separate act of using Government stamp known to have been before used under BNS Section 184, because it occurred after the BNS came into force. The removal and reuse are distinct acts with different dates. The BNS applies to the reuse even though the removal was pre-BNS. The prosecution must charge the removal under the IPC and the reuse under BNS Section 184. The temporal jurisdiction depends on the date of each specific act.

Legal Analysis (IRAC):
Issue: Which law applies when removal is pre-July 1 but reuse is post-July 1?
Rule: The BNS applies to acts committed on or after July 1, 2024. Removal and reuse are separate acts.
Application: The removal is a completed offense under the IPC on June 28. The reuse on July 5 is a new offense under BNS Section 184. The date of the reuse determines the applicable law for that specific act. The pre-BNS removal does not immunize the post-BNS reuse.
Conclusion: The removal is charged under the IPC and the reuse under BNS Section 184.

Core legal principle: Removal before July 1, 2024 is governed by the IPC, while reuse after July 1, 2024 is governed by BNS Section 184.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 5

**Split:** train

**Dates found in question:** August 1, 2024, June 25, 2024

**Parsed dates:** 2024-06-25, 2024-08-01

**Question:**
A servant was entrusted with cash for business purchases on June 25, 2024. He deposited part in his personal account and used part for personal expenses. The employer discovered this on August 1, 2024. Does IPC or BNS apply, and what is the significance of the offense date for determining the applicable substantive law?

**Assistant reply:**
IPC 1860 Section 408 applies because the entrustment and breach occurred on June 25, 2024, before the BNS 2023 commencement date of July 1, 2024. The BNS 2023 Section 316 (criminal breach of trust) would apply only if the offense had been committed on or after July 1, 2024. The determining factor is the date of the criminal act (entrustment and misappropriation), not the date of discovery or complaint. The BNSS 2023 applies procedurally to the trial regardless of when the offense was committed. The temporal jurisdiction principle ensures that no person is subjected to a law that did not exist at the time of their conduct, protecting against ex post facto application. The punishment under IPC 408 (up to 7 years) remains applicable despite the BNS 2023 having come into force before trial begins.

Legal Analysis (IRAC):
Issue: Which substantive law applies to a servant's breach of trust committed June 25, 2024 but discovered August 1, 2024?
Rule: BNS Section 1(2) fixes July 1, 2024 commencement. Offense date, not discovery date, determines applicable law. BNSS applies procedurally to all trials.
Application: June 25, 2024 offense predates BNS commencement, so IPC 408 applies substantively. August discovery and any post-July 1, 2024 trial proceedings are governed by BNSS procedurally. BNS 316 would apply only for post-July 1, 2024 conduct.
Conclusion: IPC 408 governs substantively; BNSS governs procedure; June 25, 2024 is the decisive offense date for temporal jurisdiction.

Core legal principle: Offense date determines applicable substantive law; BNS applies prospectively from July 1, 2024; pre-July 1, 2024 offenses governed by IPC regardless of discovery or trial date.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 6

**Split:** train

**Dates found in question:** July 3, 2024, June 28, 2024

**Parsed dates:** 2024-06-28, 2024-07-03

**Question:**
A defendant colluded with a plaintiff to suffer a false decree on June 28, 2024. The decree was passed on July 3, 2024. Which law applies to the defendant's conduct and what is the IPC equivalent?

**Assistant reply:**
The offense of fraudulently suffering a decree was committed through the collusive acts on June 28, 2024, before the BNS came into force on July 1, 2024. Therefore, IPC Section 208 applies. BNS Section 245 corresponds to IPC Section 208. Both carry punishment of imprisonment up to two years or fine or both, with no substantive changes in the provision.

Legal Analysis (IRAC):
Issue: Determining applicable law for collusion occurring on June 28, 2024.
Rule: BNS effective July 1, 2024. IPC Section 208 corresponds to BNS Section 245.
Application: The collusive agreement and acts occurred before transition. The decree date is irrelevant to the offense date which is when the collusion occurred.
Conclusion: IPC Section 208 applies with no change in punishment.

Core legal principle: Collusive acts on June 28, 2024, fall under IPC Section 208 with identical punishment to BNS Section 245.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 7

**Split:** train

**Dates found in question:** July 1, 2024, March 10, 2024

**Parsed dates:** 2024-03-10, 2024-07-01

**Question:**
A dacoity with murder occurred on March 10, 2024. Does IPC 1860 or BNS 2023 apply, and what is the significance of the July 1, 2024 cutoff date?

**Assistant reply:**
IPC 1860 Section 396 applies because the offense was committed on March 10, 2024, before the BNS 2023 came into force on July 1, 2024. The Bharatiya Nyaya Sanhita 2023 replaced the IPC effective July 1, 2024. For offenses committed before that date, the IPC continues to apply. The equivalent BNS provision is Section 310 (dacoity) read with Section 103 (punishment for murder), but the specific offense of 'dacoity with murder' as a composite offense with its severe punishment structure is not identically replicated in BNS.

Legal Analysis (IRAC):
Issue: Which code applies to dacoity with murder committed March 10, 2024?
Rule: BNS 2023 Section 1 provides it comes into force July 1, 2024. Offenses before that date are tried under IPC 1860.
Application: March 10, 2024 predates July 1, 2024, so IPC Section 396 applies. BNS equivalent provisions are Section 310 (dacoity) and Section 103 (murder punishment), but not as a single composite offense.
Conclusion: IPC 1860 Section 396 applies; BNS does not apply retrospectively.

Core legal principle: BNS 2023 came into force July 1, 2024; offenses committed before that date are governed by IPC 1860; dacoity with murder as a distinct composite offense exists in IPC but not identically in BNS.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 8

**Split:** train

**Dates found in question:** July 1, 2024, June 15, 2024

**Parsed dates:** 2024-06-15, 2024-07-01

**Question:**
A person committed obscene acts in a public park on June 15, 2024. Would IPC Section 294 or BNS Section 296 apply, and what is the legal significance of the July 1, 2024 cutoff date?

**Assistant reply:**
IPC Section 294 would apply, not BNS Section 296. The Bharatiya Nyaya Sanhita, 2023 came into force on July 1, 2024. For offenses committed before this date, the Indian Penal Code 1860 continues to apply. IPC Section 294 (obscene acts and songs) was the governing provision with identical language to BNS Section 296. The temporal jurisdiction is determined by the date of commission, not the date of trial or investigation. This follows the general principle that penal statutes do not apply retrospectively to prejudicial effect.

Legal Analysis (IRAC):
Issue: Which code applies to an offense committed on June 15, 2024?
Rule: BNS Section 1 provides that the Sanhita comes into force on July 1, 2024. Penal statutes apply prospectively.
Application: The act occurred on June 15, 2024, before BNS commencement. Therefore IPC Section 294 applies with identical substantive content.
Conclusion: IPC Section 294 governs; BNS Section 296 does not apply retrospectively.

Core legal principle: The BNS applies prospectively from July 1, 2024; pre-July 1, 2024 offenses are governed by corresponding IPC provisions.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 9

**Split:** train

**Dates found in question:** July 10, 2024, June 15, 2024

**Parsed dates:** 2024-06-15, 2024-07-10

**Question:**
A person violated a quarantine order on June 15, 2024. The police filed the charge sheet on July 10, 2024, citing BNS Section 273. The defense objects that the IPC should apply. Which IPC section corresponds to BNS Section 273, and is the charge sheet correctly framed?

**Assistant reply:**
The charge sheet is incorrectly framed. The IPC section corresponding to BNS Section 273 is IPC Section 271 (Disobedience to quarantine rule). Since the offense was committed on June 15, 2024, before the BNS came into force on July 1, 2024, the IPC applies under Section 358(2)(c) of the BNS. The police should have cited IPC Section 271. However, under Section 358(3), anything done under the IPC is deemed done under the corresponding BNS provision, so the defect may be curable by treating the charge as having been filed under the IPC, or the court may direct amendment of the charge to cite IPC Section 271.

Legal Analysis (IRAC):
Issue: Whether a charge sheet filed post-BNS commencement for a pre-commencement quarantine violation is correctly framed under BNS Section 273.
Rule: Section 358(2)(c) preserves IPC penalties for pre-July 1, 2024 offenses. Section 358(3) provides a deeming provision.
Application: The charge citing BNS Section 273 is technically defective. However, Section 358(3) may cure the defect by deeming the charge filed under the corresponding IPC section (271). Alternatively, the court may permit amendment of the charge to cite IPC Section 271.
Conclusion: The charge sheet should be amended to cite IPC Section 271, though the error may not be fatal under Section 358(3)'s savings provision.

Core legal principle: Pre-July 1, 2024 quarantine violations must be charged under IPC Section 271, not BNS Section 273.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 10

**Split:** train

**Dates found in question:** July 1, 2024, June 30, 2024

**Parsed dates:** 2024-06-30, 2024-07-01

**Question:**
An accused claims they were compelled by threats of instant death to commit an offence on June 30, 2024. Under IPC Section 94, this was a valid defense subject to exceptions. How does BNS Section 32 treat this claim for acts committed before July 1, 2024?

**Assistant reply:**
For acts committed on June 30, 2024, the IPC Section 94 would apply, which provided that acts compelled by threats of instant death were not offences, except for murder and offences against the State. BNS Section 32, effective from July 1, 2024, maintains the same structure and exceptions. Since the act was committed before the BNS came into force, IPC Section 94 governs the defense. The BNS Section 32 preserves the same limitations, ensuring continuity in the treatment of compulsion by threats.

Legal Analysis (IRAC):
Issue: Which law governs compulsion defenses for pre-July 1, 2024 acts.
Rule: IPC Section 94 applies to acts before July 1, 2024; BNS Section 32 applies after.
Application: The accused's act on June 30 falls under IPC Section 94. The substantive defense is identical in BNS Section 32, ensuring no disadvantage from the transition.
Conclusion: IPC Section 94 governs; BNS Section 32 maintains continuity.

Core legal principle: BNS Section 32 maintains the IPC Section 94 framework for compulsion by threats.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 11

**Split:** train

**Dates found in question:** July 1, 2024, June 20, 2024

**Parsed dates:** 2024-06-20, 2024-07-01

**Question:**
If the act of enticing away the married woman occurred on June 20, 2024, which substantive law applies and what is the significance of the July 1, 2024 cutoff date for determining jurisdiction and punishment?

**Assistant reply:**
If the act occurred on June 20, 2024, the Indian Penal Code 1860 Section 498 applies, not BNS Section 84. The July 1, 2024 cutoff date is the commencement date of the Bharatiya Nyaya Sanhita 2023, Bharatiya Nagarik Suraksha Sanhita 2023, and Bharatiya Sakshya Adhiniyam 2023. Under BNSS Section 5 (saving clause), the repealed Code of Criminal Procedure 1973 continues to apply to investigations, inquiries, and trials commenced before July 1, 2024. Therefore, for the June 20, 2024 offense: (1) IPC Section 498 defines the offense; (2) CrPC 1973 governs procedure including complaint requirements; (3) the punishment is identical (2 years maximum). The temporal jurisdiction is determined by the date of the offense, not the date of complaint or trial. This ensures no ex post facto application of harsher laws and maintains legal certainty.

Legal Analysis (IRAC):
Issue: Which law applies to offense committed June 20, 2024 and what is the significance of July 1, 2024?
Rule: Date of offense determines law; July 1, 2024 is BNS commencement; BNSS 5 saves CrPC for pending proceedings.
Application: June 20, 2024 is before July 1, 2024, so IPC 498 applies. CrPC 1973 governs procedure per BNSS 5. Punishment identical under both regimes.
Conclusion: IPC 498 applies; July 1, 2024 is critical cutoff; no retrospective application.

Core legal principle: Date of offense determines applicable substantive law; July 1, 2024 is cutoff; BNSS 5 saves CrPC 1973 for pre-commencement proceedings; no ex post facto application.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 12

**Split:** train

**Dates found in question:** July 2, 2024, June 29, 2024

**Parsed dates:** 2024-06-29, 2024-07-02

**Question:**
A person erased usage marks from stamps on June 29, 2024, and sold the stamps on July 2, 2024. Which law applies to the erasure and the sale?

**Assistant reply:**
The erasure on June 29, 2024 is governed by the Indian Penal Code because it occurred before July 1, 2024. The sale on July 2, 2024 is governed by BNS Section 185 because it occurred after the BNS came into force. The erasure and sale are distinct acts. Even though the sale is of the same stamps altered before July 1, the act of selling occurs after the transition and is governed by the BNS. The BNS Section 185 explicitly covers selling or disposing of stamps from which marks have been erased, regardless of when the erasure occurred. Therefore, the sale charge falls under BNS Section 185 while the erasure charge falls under the IPC.

Legal Analysis (IRAC):
Issue: Which law applies when erasure is pre-July 1 but sale is post-July 1?
Rule: The BNS applies to acts committed on or after July 1, 2024. Erasure and sale are separate acts.
Application: The erasure is a completed offense under the IPC. The subsequent sale is a new act under BNS Section 185. The BNS provision explicitly criminalizes selling stamps from which marks have been erased, making the sale itself the punishable act regardless of when the erasure occurred.
Conclusion: The erasure is charged under the IPC and the sale under BNS Section 185.

Core legal principle: The sale of stamps with erased marks after July 1, 2024 is governed by BNS Section 185, while the erasure before that date is governed by the IPC.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 13

**Split:** train

**Dates found in question:** July 1, 2024, July 15, 2024, June 28, 2024

**Parsed dates:** 2024-06-28, 2024-07-01, 2024-07-15

**Question:**
An incident involving an assembly with common object to resist execution of a legal process occurred on June 28, 2024. The investigation was pending on July 1, 2024, and the charge sheet was filed on July 15, 2024. Compare the applicable provisions of IPC Section 141 and BNS Section 189, and explain the effect of Section 358 of the BNS on the proceedings and punishment.

**Assistant reply:**
For the incident occurring on June 28, 2024, IPC Section 141 would apply as the substantive law governing the charge because the offense was committed before the BNS came into force on July 1, 2024. However, Section 358(2) of the BNS provides that any investigation, proceeding, or remedy in respect of any penalty or punishment incurred under the repealed IPC may be instituted, continued, or enforced as if the IPC had not been repealed. Consequently, the charge sheet filed on July 15, 2024, would properly cite IPC Section 141 despite being filed after the transition date. Section 358(3) further provides that anything done or any action taken under the IPC shall be deemed to have been done or taken under the corresponding provisions of the BNS, meaning that for procedural purposes after July 1, 2024, the court may treat the charge as if it were under BNS Section 189, though the substantive punishment would be determined by IPC Section 141 which carried imprisonment up to six months or fine or both, identical to BNS Section 189(2).

Legal Analysis (IRAC):
Issue: Whether a charge sheet filed after July 1, 2024, for a pre-transition offense must cite the IPC or BNS section numbers.
Rule: Section 358(2) permits continuation of proceedings as if the IPC had not been repealed, while Section 358(3) deems actions taken under the IPC to be taken under corresponding BNS provisions.
Application: A practical tension arises in drafting charge sheets where prosecutors must decide whether to cite the IPC section for accuracy of the substantive offense or the BNS section for current procedural regularity. The conservative approach requires citing the IPC section for pre-transition offenses to ensure the accused is charged under the law in force at the time of the offense, while relying on Section 358(3) for procedural validity.
Conclusion: The charge sheet should cite IPC Section 141 for the substantive offense committed on June 28, 2024, but the proceedings are validly continued under the BNS procedural framework.

Core legal principle: Offenses committed before July 1, 2024, remain governed by the IPC, but investigations and proceedings may continue under the BNS framework through the savings clause in Section 358.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 14

**Split:** train

**Dates found in question:** July 2, 2024, July 5, 2024, June 30, 2024

**Parsed dates:** 2024-06-30, 2024-07-02, 2024-07-05

**Question:**
On June 30, 2024, a civilian abetted an assault by a sailor on his superior officer, and the assault was committed on July 2, 2024. The civilian is apprehended on July 5, 2024. Under which provision should the civilian be charged, and why does the date of the assault matter?

**Assistant reply:**
The civilian should be charged under BNS Section 162 because the assault, which is the gravamen of the offence under this section, was committed on July 2, 2024, after the BNS came into force on July 1, 2024. While the abetment occurred on June 30, 2024, under the IPC, Section 162 specifically punishes the consequence of the abetment when the assault is committed. Since the assault occurred after the BNS commencement date, the completed offence falls under the BNS. The date of the assault matters because Section 162 is not complete until the assault is committed, and the law in force at the time of the completed offence governs the charge.

Legal Analysis (IRAC):
Issue: Which law applies when abetment occurs before but the consequence occurs after the transition date.
Rule: The law in force at the time of the completed offence governs for consequence-based crimes.
Application: Section 162 is a result crime requiring the assault to be committed. The assault occurred on July 2, 2024, when BNS was in force. Therefore, BNS Section 162 applies despite the earlier abetment. The IPC Section 134 would apply only if the assault had occurred before July 1, 2024.
Conclusion: Charge under BNS Section 162.

Core legal principle: For consequence-based crimes, the law in force at the time of the completed offence governs.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 15

**Split:** train

**Dates found in question:** February 20, 2024, October 15, 2024

**Parsed dates:** 2024-02-20, 2024-10-15

**Question:**
A clerk in a government office creates a false entry in a land registry record on February 20, 2024, intending that it appear in evidence in a pending boundary dispute. The case comes to light during trial on October 15, 2024. Identify the applicable offense, the BNSS summary procedure, and the BSA rules for proving the fabricated electronic record.

**Assistant reply:**
The applicable offense is IPC 1860 Section 192 (fabricating false evidence) as the act of fabrication occurred on February 20, 2024, before July 1, 2024. The equivalent BNS provision is Section 228. Under BNSS Section 383, the summary procedure for trial for giving false evidence extends to fabricating false evidence - if at the time of delivering judgment, the court expresses opinion that false evidence was fabricated, it may take cognizance and proceed summarily. For proving the fabricated electronic record, BSA provides: (1) BSA Section 61 (electronic or digital record) - defines electronic records; (2) BSA Section 62 (special provisions as to evidence relating to electronic record) - requires certificate under Section 63; (3) BSA Section 63 (admissibility of electronic records) - conditions for admissibility; (4) BSA Section 56 (proof of contents of documents) - primary and secondary evidence rules; (5) BSA Section 57 (primary evidence) - original electronic record; (6) BSA Section 58 (secondary evidence) - certified copies; (7) BSA Section 72 (comparison of signature, writing or seal) - forensic comparison; and (8) BSA Section 73 (proof as to verification of digital signature). The prosecution must prove the original authentic record, the falsity of the entry, the accused's authorship, and the intent for it to appear in evidence.

Legal Analysis (IRAC):
Issue: What law governs fabrication of electronic records in February 2024, what procedure applies in October 2024, and how is the electronic record proved?
Rule: IPC 192 applies to the act; BNSS 383 applies to the October 2024 judgment; BSA 61-63, 56-58, 72-73 govern electronic record proof.
Application: The fabrication occurred pre-July 2024 so IPC 192 applies. The October 2024 trial allows BNSS 383 summary procedure. The electronic record requires certificate under BSA 63 and may need forensic comparison under BSA 72.
Conclusion: IPC 192 governs the offense, BNSS 383 provides the procedure, and BSA electronic record rules govern proof.

Core legal principle: Fabricating false evidence in electronic records is punishable under IPC 192/BNS 228, subject to BNSS 383 summary procedure, with proof governed by BSA electronic record admissibility rules.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 16

**Split:** train

**Dates found in question:** July 1, 2024, July 10, 2024, June 25, 2024

**Parsed dates:** 2024-06-25, 2024-07-01, 2024-07-10

**Question:**
An FIR registered on July 10, 2024, alleges that on June 25, 2024, five persons acting in concert murdered a victim based on his caste. The prosecution seeks to apply Section 103(2) of the BNS, which mandates death or life imprisonment for such concerted murders on grounds of caste. The defense argues that since the offence was committed before July 1, 2024, only IPC Section 302 applies. Advise the court on the applicable law.

**Assistant reply:**
The defense argument is correct. Section 358(2)(c) explicitly preserves any penalty or punishment incurred in respect of offences committed against the repealed IPC, and Section 358(2)(e) preserves any proceeding in respect of such punishment as if the IPC had not been repealed. The offence was committed on June 25, 2024, when the IPC was in force. While Section 103(2) of the BNS introduces a specific enhancement for concerted murders on grounds of caste, race, or community, this provision was not in force at the time of the alleged offence. Applying Section 103(2) retrospectively would constitute an ex post facto application of a harsher penalty, which is barred by the savings clause. The accused must be tried and punished under IPC Section 302, which provided for death or imprisonment for life, but without the specific statutory mandate regarding the caste-based concerted killing enhancement found in BNS Section 103(2).

Legal Analysis (IRAC):
Issue: Whether the enhanced punishment for group murders based on caste grounds under BNS Section 103(2) applies to an offence committed on June 25, 2024, when the IPC was in force.
Rule: Section 358(2)(c) preserves penalties incurred under the repealed IPC, and Section 103(2) introduces a new mandatory enhancement for concerted murders on specified grounds that was not present in IPC Section 302.
Application: The offence was committed before the BNS commencement date, triggering the savings clause. While Section 358(3) deems the act as done under BNS for procedural purposes, the substantive punishment is governed by the law in force at the time of commission. The enhanced provision in Section 103(2) represents a harsher penalty than available under IPC Section 302, and applying it retrospectively would violate the principle against ex post facto laws, despite the procedural continuity established by Section 358.
Conclusion: The IPC Section 302 punishment applies. The Section 103(2) enhancement does not apply retrospectively.

Core legal principle: Savings clauses preserve the substantive law applicable at the time of offence commission, preventing retrospective application of enhanced penalties.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 17

**Split:** train

**Dates found in question:** August 10, 2024, March 20, 2024

**Parsed dates:** 2024-03-20, 2024-08-10

**Question:**
A complaint of intent to disrobe is filed on August 10, 2024, alleging an incident on March 20, 2024. Which substantive law applies and why?

**Assistant reply:**
IPC 1860 Section 354B applies because the alleged offense occurred on March 20, 2024, before the BNS 2023 came into force on July 1, 2024. Under Section 5 of the BNS 2023 (savings clause), the IPC continues to apply to offenses committed before commencement. The complaint filed on August 10, 2024 is governed by BNSS 2023 procedures, but the substantive offense is determined by the date of the act, not the date of complaint. If the incident had occurred on or after July 1, 2024, BNS 2023 Section 76 would apply.

Legal Analysis (IRAC):
Issue: Does IPC or BNS govern an offense committed before July 1, 2024 but complained after?
Rule: BNS Section 5 saves IPC for pre-commencement offenses. Date of act determines applicable substantive law.
Application: March 20, 2024 is pre-July 1, 2024, so IPC 354B applies. August 10, 2024 complaint date is procedurally relevant under BNSS but does not change substantive law.
Conclusion: IPC 354B applies to the substantive offense; BNSS governs procedural aspects of the complaint.

Core legal principle: Substantive criminal law applies based on date of offense, not date of complaint or trial.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 18

**Split:** train

**Dates found in question:** June 20, 2024, September 5, 2024

**Parsed dates:** 2024-06-20, 2024-09-05

**Question:**
A forged will was created on June 20, 2024 and used to claim property on September 5, 2024. Does the IPC or BNS govern this offense, and what is the legal test for determining temporal applicability?

**Assistant reply:**
The BNS governs this offense. The Bharatiya Nyaya Sanhita, 2023 came into force on July 1, 2024. Since the forged will was created on June 20, 2024 (before July 1, 2024), technically the IPC Section 467 would apply to the act of creation. However, the continuous offense doctrine may apply if the forgery was used on September 5, 2024. More precisely, under the general principles of temporal jurisdiction, the law in force at the time of the offense governs. Since the creation (the substantive offense) occurred June 20, 2024, IPC 467 applies to the forgery creation. However, the use on September 5, 2024 would be governed by BNS Section 340 (using forged document as genuine) as a separate offense. The Supreme Court has held that when an offense is continuing or has multiple components, the law at the time of each component applies. The CBI passport scam case (SC_0024) illustrates how courts analyze document forgery cases with multiple temporal elements.

Legal Analysis (IRAC):
Issue: Does IPC or BNS govern a forgery created before July 1, 2024 but used after?
Rule: Law in force at offense commission governs; separate acts may have separate governing laws; BNS effective July 1, 2024.
Application: Creation on June 20, 2024 governed by IPC 467; use on September 5, 2024 as separate offense governed by BNS 340; continuing offense doctrine may apply to link temporal components.
Conclusion: IPC 467 governs creation; BNS 340 governs post-July use; court must analyze whether single transaction or separate offenses.

Core legal principle: The law in force at the time of offense commission governs; for continuing offenses or separate acts (creation vs. use), different laws may apply to different temporal components.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 19

**Split:** train

**Dates found in question:** August 1, 2024, March 15, 2024

**Parsed dates:** 2024-03-15, 2024-08-01

**Question:**
A person sends fraudulent emails on March 15, 2024 promising investment returns and induces the victim to transfer â‚¹50,000. Identify the applicable IPC section, explain whether BNS 2023 would apply if the same act occurred on August 1, 2024, and state the mandatory BNSS procedure and BSA evidence rule for electronic records.

**Assistant reply:**
For the March 15, 2024 act, IPC 1860 Section 417 (punishment for cheating) applies with imprisonment up to 1 year or fine or both. If the same act occurred on August 1, 2024, BNS 2023 Section 318 would apply instead as the BNS came into force on July 1, 2024. Under BNSS Section 283, cheating is triable summarily by Chief Judicial Magistrate or Magistrate of first class. Under BNSS Section 202, when cheating is committed by electronic communications, it is triable where such communications were sent or received. Under BSA Section 61, electronic records are admissible as documentary evidence, and Section 63 specifies the conditions for admissibility of electronic records including computer output.

Legal Analysis (IRAC):
Issue: Which law governs cheating by electronic means and what are the procedural and evidentiary rules?
Rule: IPC 417/BNS 318 define cheating. BNSS 283 permits summary trial. BNSS 202 provides special territorial jurisdiction for electronic cheating. BSA 61-63 govern electronic evidence admissibility.
Application: Pre-July 1, 2024: IPC 417 applies. Post-July 1, 2024: BNS 318 applies. Both scenarios permit summary trial under BNSS 283. Electronic communications trigger BNSS 202 jurisdiction. Email evidence admissible under BSA 61 and 63.
Conclusion: IPC 417 for March 2024; BNS 318 for August 2024; BNSS 283 (summary trial), BNSS 202 (territorial jurisdiction), BSA 61-63 (electronic evidence) apply to both.

Core legal principle: Cheating offenses transitioned from IPC to BNS on July 1, 2024; electronic cheating has special territorial jurisdiction under BNSS 202 and summary trial under BNSS 283; electronic evidence is admissible under BSA 61-63.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

## Case 20

**Split:** train

**Dates found in question:** July 15, 2024, June 15, 2024

**Parsed dates:** 2024-06-15, 2024-07-15

**Question:**
Under IPC Section 77, a Judge acting judicially was immune from prosecution. If a Judge passed an order on June 15, 2024, and is prosecuted on July 15, 2024, under BNS Section 257 for corruptly making a report contrary to law, how does the transition affect the defense under Section 15?

**Assistant reply:**
The act occurred when IPC Section 77 was in force. Under Section 358(3) of BNS, the act is deemed done under BNS Section 15. However, if the prosecution under Section 257 alleges corrupt intent (knowing the act was contrary to law), the defense under Section 15 fails because the Judge did not act in good faith or within believed lawful authority. The transition preserves the defense only for legitimate judicial acts, not corrupt ones. The IPC equivalent is Section 77, but the BNS adds Section 257 as an exception to such immunity.

Legal Analysis (IRAC):
Issue: Whether judicial immunity survives the transition to BNS when the Judge is accused of corruption.
Rule: Section 358(3) deems acts done under IPC Section 77 as done under BNS Section 15. Section 257 criminalizes corrupt judicial acts.
Application: The Judge's act on June 15, 2024, is deemed under BNS Section 15. However, Section 257 applies to corrupt acts. If the Judge acted corruptly, he loses Section 15 protection because good faith is negated. The transition does not protect corrupt acts that fall under Section 257.
Conclusion: The defense under Section 15 is unavailable if the act was corrupt, as Section 257 applies to override the immunity.

Core legal principle: Section 358 preserves IPC Section 77 defenses under BNS Section 15, but Section 257 overrides immunity for corrupt acts.

**Judgment:** [ ] Genuine split (2 periods)  [ ] Genuine but single law  [ ] False positive  [ ] Ambiguous/inconsistent

---

