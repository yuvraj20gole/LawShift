# Error Analysis: 108 misses out of 635 val questions (17.0% miss rate)

For each miss: the question, the gold (expected) section, and what the model actually retrieved instead. Read each one and judge: is the retrieved answer plausibly also correct/related (defensible miss), or clearly wrong (real error)?

## Miss 1 — consequence

**Question:** What is the consequence of this tie-breaking rule?

**Gold section (BNSS_411):**
> [Context: This section is from BNSS 2023, CHAPTER XXX SUBMISSION OF DEATH SENTENCES FOR CONFIRMATION. It covers Section 411: Procedure in case of difference of opinion.]

411. Procedure in case of difference of opinion.—Where any such case is heard before a Bench of
Judges and such Judges are equally divided in opinion, the case shall be decided in the manner provided by
section 433....

**Gold answer (reference):** The consequence is preventing arbitrary executions based on bench composition; if a tie just resulted in the lower court's death sentence standing, a man could be executed simply because he drew a two-judge bench that couldn't agree. Bringing in a third tie-breaking judge ensures a true majority con...

**Top-5 retrieved instead:**
- `BNSS_433`: [Context: This section is from BNSS 2023, CHAPTER XXXI APPEALS. It covers Section 433: Procedure where Judges of Court of appeal are equally divided.]

433. Procedure where Judges of Court of appeal a...
- `BNSS_243`: [Context: This section is from BNSS 2023, CHAPTER XVIII THE CHARGE. It covers Section 243: Trial for more than one offence.]

243. Trial for more than one offence.—(1) If, in one series of acts so con...
- `BNSS_204`: [Context: This section is from BNSS 2023, CHAPTER XIV JURISDICTION OF THE CRIMINAL COURTS IN INQUIRIES AND TRIALS. It covers Section 204: Place of trial for offences triable together.]

204. Place of ...
- `BNSS_246`: [Context: This section is from BNSS 2023, CHAPTER XVIII THE CHARGE. It covers Section 246: What persons may be charged jointly.]

246. What persons may be charged jointly.—The following persons may be...
- `BNSS_247`: [Context: This section is from BNSS 2023, CHAPTER XVIII THE CHARGE. It covers Section 247: Withdrawal of remaining charges on conviction on one of several charges.]

247. Withdrawal of remaining charg...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 2 — consequence

**Question:** What is the jurisdictional consequence of this single-sentence section?

**Gold section (BNSS_79):**
> [Context: This section is from BNSS 2023, CHAPTER VI PROCESSES TO COMPEL APPEARANCE. It covers Section 79: Where warrant may be executed.]

79. Where warrant may be executed.—A warrant of arrest may be executed at any place in India....

**Gold answer (reference):** The consequence is that it eliminates safe havens within the country, allowing the legal reach of any issuing court to span the entirety of India. [Source: Section 79, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNS_7`: [Context: This section is from BNS 2023, CHAPTER II OF PUNISHMENTS. It covers Section 7: Sentence may be (in certain cases of imprisonment) wholly or partly rigorous or simple.]

7. Sentence may be (i...
- `BNSS_513`: [Context: This section is from BNSS 2023, CHAPTER XXXVIII LIMITATION FOR TAKING COGNIZANCE OF CERTAIN OFFENCES. It covers Section 513: Definitions.]

513. Definitions.—For the purposes of this Chapter...
- `BNSS_514`: [Context: This section is from BNSS 2023, CHAPTER XXXVIII LIMITATION FOR TAKING COGNIZANCE OF CERTAIN OFFENCES. It covers Section 514: Bar to taking cognizance after lapse of period of limitation.]

5...
- `BNS_4`: [Context: This section is from BNS 2023, CHAPTER II OF PUNISHMENTS. It covers Section 4: Punishments.]

4. Punishments. —The punishments to which offenders are liable under the provisions of this
Sanh...
- `BNSS_467`: [Context: This section is from BNSS 2023, CHAPTER XXXIV EXECUTION, SUSPENSION, REMISSION AND COMMUTATION OF SENTENCES. It covers Section 467: Sentence on offender already sentenced for another offence...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 3 — consequence

**Question:** What is the consequence of escalating the punishment in clause (b)?

**Gold section (BNS_222):**
> [Context: This section is from BNS 2023, CHAPTER XIII OF CONTEMPTS OF THE LAWFUL AUTHORITY OF PUBLIC SERVANTS. It covers Section 222: Omission to assist public servant when bound by law to give assistance.]

222. Omission to assist public servant when bound by law to give assistance.—Whoever, being
bound by law to render or furnish assistance to any public servant in the execution of his public du...

**Gold answer (reference):** The consequence is that the law treats refusing to help during acute public safety emergencies (riots, violent arrests) as a much more serious dereliction of civic duty than failing to assist in routine administrative tasks. [Source: Section 222, BNS 2023]...

**Top-5 retrieved instead:**
- `BNS_231`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 231: Giving or fabricating false evidence with intent to procure convictio...
- `BNS_229`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 229: Punishment for false evidence.]

229. Punishment for false evidence.—...
- `BNS_206`: [Context: This section is from BNS 2023, CHAPTER XIII OF CONTEMPTS OF THE LAWFUL AUTHORITY OF PUBLIC SERVANTS. It covers Section 206: Absconding to avoid service of summons or other proceeding.]

206....
- `BNSS_388`: [Context: This section is from BNSS 2023, CHAPTER XXVIII PROVISIONS AS TO OFFENCES AFFECTING THE ADMINISTRATION OF JUSTICE. It covers Section 388: Imprisonment or committal of person refusing to answe...
- `BNS_257`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 257: Public servant in judicial proceeding corruptly making report, etc., ...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 4 — consequence

**Question:** What is the consequence of this mandatory check for the fairness of the trial?

**Gold section (BNSS_261):**
> [Context: This section is from BNSS 2023, CHAPTER XX TRIAL OF WARRANT-CASES BY MAGISTRATES. It covers Section 261: Compliance with section 230.]

261. Compliance with section 230.—When, in any warrant-case instituted on a police report, the
accused appears or is brought before a Magistrate at the commencement of the trial, the Magistrate shall
satisfy himself that he has complied with the provisio...

**Gold answer (reference):** The consequence is the prevention of "trial by ambush"; it guarantees the accused's fundamental right to know the evidence against them is upheld right at the starting line, ensuring they can prepare an adequate defense. [Source: Section 261, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNSS_510`: [Context: This section is from BNSS 2023, CHAPTER XXXVII IRREGULAR PROCEEDINGS. It covers Section 510: Effect of omission to frame, or absence of, or error in, charge.]

510. Effect of omission to fra...
- `BNSS_345`: [Context: This section is from BNSS 2023, CHAPTER XXVI GENERAL PROVISIONS AS TO INQUIRIES AND TRIALS. It covers Section 345: Trial of person not complying with conditions of pardon.]

345. Trial of pe...
- `BNSS_277`: [Context: This section is from BNSS 2023, CHAPTER XXI TRIAL OF SUMMONS-CASES BY MAGISTRATES. It covers Section 277: Procedure when not convicted.]

277. Procedure when not convicted.—(1) If the Magist...
- `BNSS_253`: [Context: This section is from BNSS 2023, CHAPTER XIX TRIAL BEFORE A COURT OF SESSION. It covers Section 253: Date for prosecution evidence.]

253. Date for prosecution evidence.—If the accused refuse...
- `BNSS_400`: [Context: This section is from BNSS 2023, CHAPTER XXIX THE JUDGMENT. It covers Section 400: Order to pay costs in non-cognizable cases.]

400. Order to pay costs in non-cognizable cases.—(1) Whenever ...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 5 — definitional_topic

**Question:** In a private complaint case, what happens if the complainant's initial evidence *does* show there are grounds to presume the accused committed the crime?

**Gold section (BNSS_269):**
> [Context: This section is from BNSS 2023, CHAPTER XX TRIAL OF WARRANT-CASES BY MAGISTRATES. It covers Section 269: Procedure where accused is not discharged.]

269. Procedure where accused is not discharged.—(1) If, when such evidence has been taken, or at
any previous stage of the case, the Magistrate is of opinion that there is ground for presuming that the
accused has committed an offence triab...

**Gold answer (reference):** The Magistrate will officially write down the charge, read it to the accused, ask how they plead, and if they plead not guilty, allow the accused to cross-examine the complainant's witnesses. [Source: Section 269, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNSS_272`: [Context: This section is from BNSS 2023, CHAPTER XX TRIAL OF WARRANT-CASES BY MAGISTRATES. It covers Section 272: Absence of complainant.]

272. Absence of complainant.—When the proceedings have been...
- `BNSS_236`: [Context: This section is from BNSS 2023, CHAPTER XVIII THE CHARGE. It covers Section 236: When manner of committing offence must be stated.]

236. When manner of committing offence must be stated.—Wh...
- `BNSS_274`: [Context: This section is from BNSS 2023, CHAPTER XXI TRIAL OF SUMMONS-CASES BY MAGISTRATES. It covers Section 274: Substance of accusation to be stated.]

274. Substance of accusation to be stated.—W...
- `BNSS_268`: [Context: This section is from BNSS 2023, CHAPTER XX TRIAL OF WARRANT-CASES BY MAGISTRATES. It covers Section 268: When accused shall be discharged.]

268. When accused shall be discharged.—(1) If, up...
- `BNSS_233`: [Context: This section is from BNSS 2023, CHAPTER XVII COMMENCEMENT OF PROCEEDINGS BEFORE MAGISTRATES. It covers Section 233: Procedure to be followed when there is a complaint case and police investi...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 6 — definitional_topic

**Question:** What happens if a person just ignores a Magistrate's order to remove a public nuisance?

**Gold section (BNSS_155):**
> [Context: This section is from BNSS 2023, CHAPTER XI MAINTENANCE OF PUBLIC ORDER AND TRANQUILLITY. It covers Section 155: Penalty for failure to comply with section 154.]

155. Penalty for failure to comply with section 154.—If the person against whom an order is made
under section 154 does not perform such act or appear and show cause, he shall be liable to the penalty
specified in that behalf in...

**Gold answer (reference):** If the person does not perform the act or appear to show cause, they become liable to a penalty under section 223 of the Bharatiya Nyaya Sanhita, 2023, and the Magistrate's order is made absolute. [Source: Section 155, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNSS_163`: [Context: This section is from BNSS 2023, CHAPTER XI MAINTENANCE OF PUBLIC ORDER AND TRANQUILLITY. It covers Section 163: Power to issue order in urgent cases of nuisance or apprehended danger.]

163....
- `BNSS_162`: [Context: This section is from BNSS 2023, CHAPTER XI MAINTENANCE OF PUBLIC ORDER AND TRANQUILLITY. It covers Section 162: Magistrate may prohibit repetition or Continuance of public nuisance.]

162. M...
- `BNSS_152`: [Context: This section is from BNSS 2023, CHAPTER XI MAINTENANCE OF PUBLIC ORDER AND TRANQUILLITY. It covers Section 152: Conditional order for removal of nuisance.]

152. Conditional order for remova...
- `BNSS_160`: [Context: This section is from BNSS 2023, CHAPTER XI MAINTENANCE OF PUBLIC ORDER AND TRANQUILLITY. It covers Section 160: Procedure on order being made absolute and consequences of disobedience.]

160...
- `BNSS_156`: [Context: This section is from BNSS 2023, CHAPTER XI MAINTENANCE OF PUBLIC ORDER AND TRANQUILLITY. It covers Section 156: Procedure where existence of public right is denied.]

156. Procedure where ex...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 7 — definitional_topic

**Question:** What does the crime of "assault" actually mean under Indian law?

**Gold section (BNS_130):**
> [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 130: Assault.]

130. Assault.—Whoever makes any gesture, or any preparation intending or knowing it to be likely
that such gesture or preparation will cause any person present to apprehend that he who makes that
gesture or preparation is about to use criminal force to that person, is said to...

**Gold answer (reference):** In Indian law, "assault" is not the act of hitting someone (that is criminal force or hurt); assault is merely making a gesture or preparation that makes someone reasonably fear that you are about to use criminal force against them (like raising a fist). [Source: Section 130, BNS 2023]...

**Top-5 retrieved instead:**
- `BNS_133`: [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 133: Assault or criminal force with intent to dishonour person, otherwise than on grave.]

1...
- `BNS_135`: [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 135: Assault or criminal force in attempt to wrongfully confine a person.]

135. Assault or ...
- `BNS_136`: [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 136: Assault or criminal force on grave provocation.]

136. Assault or criminal force on gra...
- `BNS_38`: [Context: This section is from BNS 2023, CHAPTER III GENERAL EXCEPTIONS. It covers Section 38: When right of private defence of body extends to causing death.]

38. When right of private defence of bo...
- `BNS_76`: [Context: This section is from BNS 2023, CHAPTER V OF OFFENCES AGAINST WOMAN AND CHILD. It covers Section 76: Assault or use of criminal force to woman with intent to disrobe.]

76. Assault or use of ...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 8 — definitional_topic

**Question:** What is the penalty for a police officer or judge who illegally locks someone up?

**Gold section (BNS_258):**
> [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 258: Commitment for trial or confinement by person having authority who knows that he is.]

258. Commitment for trial or confinement by person having authority who knows that he is
acting contrary to law.—Whoever, being in any office which gives him legal authority to commi...

**Gold answer (reference):** A person with legal authority to commit individuals to confinement who corruptly or maliciously does so, knowing it is contrary to law, is punishable by up to seven years in prison or a fine. [Source: Section 258, BNS 2023]...

**Top-5 retrieved instead:**
- `BNS_261`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 261: Escape from confinement or custody negligently suffered by public ser...
- `BNS_198`: [Context: This section is from BNS 2023, CHAPTER XII OF OFFENCES BY OR RELATING TO PUBLIC SERVANTS. It covers Section 198: Public servant disobeying law, with intent to cause injury to any person.]

1...
- `BNS_260`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 260: Intentional omission to apprehend on part of public servant bound to ...
- `BNS_255`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 255: Public servant disobeying direction of law with intent to save person...
- `BNS_127`: [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 127: Wrongful confinement.]

127. Wrongful confinement.—(1) Whoever wrongfully restrains any...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 9 — elements

**Question:** What condition triggers the duty to report under this section?

**Gold section (BNSS_33):**
> [Context: This section is from BNSS 2023, CHAPTER IV POWERS OF SUPERIOR OFFICERS OF POLICE AND AID TO THE MAGISTRATES AND THE POLICE. It covers Section 33: Public to give information of certain offences.]

33. Public to give information of certain offences.—(1) Every person, aware of the commission of,
or of the intention of any other person to commit, any offence punishable under any of the follo...

**Gold answer (reference):** The duty is triggered when a person becomes aware of the commission of, or of the intention of any other person to commit, any of the specifically enumerated offences. [Source: Section 33, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNSS_188`: [Context: This section is from BNSS 2023, CHAPTER XIII INFORMATION TO THE POLICE AND THEIR POWERS TO INVESTIGATE. It covers Section 188: Report of investigation by subordinate police officer.]

188. R...
- `BNSS_177`: [Context: This section is from BNSS 2023, CHAPTER XIII INFORMATION TO THE POLICE AND THEIR POWERS TO INVESTIGATE. It covers Section 177: Report how submitted.]

177. Report how submitted.—(1) Every re...
- `BNSS_176`: [Context: This section is from BNSS 2023, CHAPTER XIII INFORMATION TO THE POLICE AND THEIR POWERS TO INVESTIGATE. It covers Section 176: Procedure for investigation.]

176. Procedure for investigation...
- `BNSS_59`: [Context: This section is from BNSS 2023, CHAPTER V ARREST OF PERSONS. It covers Section 59: Police to report apprehensions.]

59. Police to report apprehensions.— Officers in charge of police station...
- `BNSS_193`: [Context: This section is from BNSS 2023, CHAPTER XIII INFORMATION TO THE POLICE AND THEIR POWERS TO INVESTIGATE. It covers Section 193: Report of police officer on completion of investigation.]

193....

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 10 — elements

**Question:** What condition justifies the issuance of this summons or order?

**Gold section (BNSS_94):**
> [Context: This section is from BNSS 2023, CHAPTER VII PROCESSES TO COMPEL THE PRODUCTION OF THINGS. It covers Section 94: Summons to produce document or other thing.]

94. Summons to produce document or other thing.—(1) Whenever any Court or any officer in
charge of a police station considers that the production of any document, electronic communication,
including communication devices, which is l...

**Gold answer (reference):** The Court or officer must consider that the production is "necessary or desirable for the purposes of any investigation, inquiry, trial or other proceeding under this Sanhita." [Source: Section 94, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNSS_133`: [Context: This section is from BNSS 2023, CHAPTER IX SECURITY FOR KEEPING THE PEACE AND FOR GOOD BEHAVIOUR. It covers Section 133: Copy of order to accompany summons or warrant.]

133. Copy of order t...
- `BNSS_153`: [Context: This section is from BNSS 2023, CHAPTER XI MAINTENANCE OF PUBLIC ORDER AND TRANQUILLITY. It covers Section 153: Service or notification of order.]

153. Service or notification of order.—(1)...
- `BNSS_71`: [Context: This section is from BNSS 2023, CHAPTER VI PROCESSES TO COMPEL APPEARANCE. It covers Section 71: Service of summons on witness.]

71. Service of summons on witness.—(1) Notwithstanding anyth...
- `BNSS_90`: [Context: This section is from BNSS 2023, CHAPTER VI PROCESSES TO COMPEL APPEARANCE. It covers Section 90: Issue of warrant in lieu of, or in addition to, summons.]

90. Issue of warrant in lieu of, o...
- `BNSS_67`: [Context: This section is from BNSS 2023, CHAPTER VI PROCESSES TO COMPEL APPEARANCE. It covers Section 67: Procedure when service cannot be effected as before provided.]

67. Procedure when service ca...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 11 — elements

**Question:** What specific intent or context must accompany the hurt to trigger the enhanced penalties of this section rather than standard assault laws?

**Gold section (BNS_121):**
> [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 121: Voluntarily causing hurt or grievous hurt to deter public servant from his duty.]

121. Voluntarily causing hurt or grievous hurt to deter public servant from his duty.—(1)
Whoever voluntarily causes hurt to any person being a public servant in the discharge of his duty as such
public s...

**Gold answer (reference):** The hurt must be caused to a public servant while they are discharging their duty, or with the intent to prevent/deter them from discharging their duty, or in consequence of something they did in the lawful discharge of their duty. [Source: Section 121, BNS 2023]...

**Top-5 retrieved instead:**
- `BNS_115`: [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 115: Voluntarily causing hurt.]

115. Voluntarily causing hurt.—(1) Whoever does any act wit...
- `BNS_133`: [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 133: Assault or criminal force with intent to dishonour person, otherwise than on grave.]

1...
- `BNS_122`: [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 122: Voluntarily causing hurt or grievous hurt on provocation.]

122. Voluntarily causing hu...
- `BNS_38`: [Context: This section is from BNS 2023, CHAPTER III GENERAL EXCEPTIONS. It covers Section 38: When right of private defence of body extends to causing death.]

38. When right of private defence of bo...
- `BNS_116`: [Context: This section is from BNS 2023, CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY. It covers Section 116: Grievous hurt.]

116. Grievous hurt.—The following kinds of hurt only are designated as...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 12 — elements

**Question:** What distinguishes the punishment under clause (a) and clause (b) in this section?

**Gold section (BNS_264):**
> [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 264: Omission to apprehend, or sufferance of escape, on part of public servant, in cases not.]

264. Omission to apprehend, or sufferance of escape, on part of public servant, in cases not
otherwise provided for.—Whoever, being a public servant legally bound as such public ...

**Gold answer (reference):** Clause (a) covers "intentionally" suffering escape (punishable by up to 3 years of either description), while clause (b) covers "negligently" doing so (punishable by up to 2 years of simple imprisonment). [Source: Section 264, BNS 2023]...

**Top-5 retrieved instead:**
- `BNS_231`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 231: Giving or fabricating false evidence with intent to procure convictio...
- `BNS_229`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 229: Punishment for false evidence.]

229. Punishment for false evidence.—...
- `BNS_257`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 257: Public servant in judicial proceeding corruptly making report, etc., ...
- `BNS_206`: [Context: This section is from BNS 2023, CHAPTER XIII OF CONTEMPTS OF THE LAWFUL AUTHORITY OF PUBLIC SERVANTS. It covers Section 206: Absconding to avoid service of summons or other proceeding.]

206....
- `BNS_266`: [Context: This section is from BNS 2023, CHAPTER XIV OF FALSE EVIDENCE AND OFFENCES AGAINST PUBLIC JUSTICE. It covers Section 266: Violation of condition of remission of punishment.]

266. Violation o...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 13 — exceptions

**Question:** Does this section reverse the burden of proof if a person buys a car from a completely unknown, random stranger?

**Gold section (BSA_114):**
> [Context: This section is from BSA 2023, CHAPTER VII OF THE BURDEN OF PROOF. It covers Section 114: Proof of good faith in transactions where one party is in relation of active confidence.]

114. Proof of good faith in transactions where one party is in relation of active confidence.—
Where there is a question as to the good faith of a transaction between parties, one of whom stands to the
other i...

**Gold answer (reference):** No, it only applies when there is a question of good faith between parties where one is 'in relation of active confidence.' [Source: Section 114, BSA 2023]...

**Top-5 retrieved instead:**
- `BSA_113`: [Context: This section is from BSA 2023, CHAPTER VII OF THE BURDEN OF PROOF. It covers Section 113: Burden of proof as to ownership.]

113. Burden of proof as to ownership.—When the question is whethe...
- `BSA_19`: [Context: This section is from BSA 2023, CHAPTER II RELEVANCY OF FACTS. It covers Section 19: Proof of admissions against persons making them, and by or on their behalf.]

19. Proof of admissions agai...
- `BSA_109`: [Context: This section is from BSA 2023, CHAPTER VII OF THE BURDEN OF PROOF. It covers Section 109: Burden of proving fact especially within knowledge.]

109. Burden of proving fact especially within ...
- `BSA_106`: [Context: This section is from BSA 2023, CHAPTER VII OF THE BURDEN OF PROOF. It covers Section 106: Burden of proof as to particular fact.]

106. Burden of proof as to particular fact.—The burden of p...
- `BSA_11`: [Context: This section is from BSA 2023, CHAPTER II RELEVANCY OF FACTS. It covers Section 11: Facts relevant when right or custom is in question.]

11. Facts relevant when right or custom is in questi...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 14 — exceptions

**Question:** Is there any scenario where a tie results in an automatic acquittal without going to a third judge?

**Gold section (BNSS_411):**
> [Context: This section is from BNSS 2023, CHAPTER XXX SUBMISSION OF DEATH SENTENCES FOR CONFIRMATION. It covers Section 411: Procedure in case of difference of opinion.]

411. Procedure in case of difference of opinion.—Where any such case is heard before a Bench of
Judges and such Judges are equally divided in opinion, the case shall be decided in the manner provided by
section 433....

**Gold answer (reference):** Not under this section. The mandate is clear: "the case shall be decided in the manner provided by section 433." [Source: Section 411, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNSS_433`: [Context: This section is from BNSS 2023, CHAPTER XXXI APPEALS. It covers Section 433: Procedure where Judges of Court of appeal are equally divided.]

433. Procedure where Judges of Court of appeal a...
- `BNSS_337`: [Context: This section is from BNSS 2023, CHAPTER XXVI GENERAL PROVISIONS AS TO INQUIRIES AND TRIALS. It covers Section 337: Person once convicted or acquitted not to be tried for same offence.]

337....
- `BNSS_247`: [Context: This section is from BNSS 2023, CHAPTER XVIII THE CHARGE. It covers Section 247: Withdrawal of remaining charges on conviction on one of several charges.]

247. Withdrawal of remaining charg...
- `BNSS_25`: [Context: This section is from BNSS 2023, CHAPTER III POWER OF COURTS. It covers Section 25: Sentence in cases of conviction of several offences at one trial.]

25. Sentence in cases of conviction of ...
- `BNSS_421`: [Context: This section is from BNSS 2023, CHAPTER XXXI APPEALS. It covers Section 421: Special right of appeal in certain cases.]

421. Special right of appeal in certain cases.—Notwithstanding anythi...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 15 — exceptions

**Question:** Does this section absolutely ban the use of secondary evidence?

**Gold section (BSA_59):**
> [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 59: Proof of documents by primary evidence.]

59. Proof of documents by primary evidence.— Documents shall be proved by primary
evidence except in the cases hereinafter mentioned....

**Gold answer (reference):** No, the section includes the caveat 'except in the cases hereinafter mentioned,' acknowledging that secondary evidence is permitted under specific conditions. [Source: Section 59, BSA 2023]...

**Top-5 retrieved instead:**
- `BSA_56`: [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 56: Proof of contents of documents.]

56. Proof of contents of documents.—The contents of documents may be...
- `BSA_58`: [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 58: Secondary evidence.]

58. Secondary evidence.—Secondary evidence includes—
(i) certified copies given ...
- `BSA_107`: [Context: This section is from BSA 2023, CHAPTER VII OF THE BURDEN OF PROOF. It covers Section 107: Burden of proving fact to be proved to make evidence admissible.]

107. Burden of proving fact to be...
- `BSA_139`: [Context: This section is from BSA 2023, CHAPTER IX OF WITNESSES. It covers Section 139: Number of witnesses.]

139. Number of witnesses.—No particular number of witnesses shall in any case be require...
- `BSA_60`: [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 60: Cases in which secondary evidence relating to documents may be given.]

60. Cases in which secondary e...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 16 — exceptions

**Question:** Is the Magistrate *forced* to send the case up every single time?

**Gold section (BNSS_363):**
> [Context: This section is from BNSS 2023, CHAPTER XXVI GENERAL PROVISIONS AS TO INQUIRIES AND TRIALS. It covers Section 363: Trial of persons previously convicted of offences against coinage, stamp-law or.]

363. Trial of persons previously convicted of offences against coinage, stamp-law or
property.—(1) Where a person, having been convicted of an offence punishable under Chapter X or
years or up...

**Gold answer (reference):** No, there is an exception: "unless the Magistrate is competent to try the case and is of opinion that he can himself pass an adequate sentence". [Source: Section 363, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNSS_228`: [Context: This section is from BNSS 2023, CHAPTER XVII COMMENCEMENT OF PROCEEDINGS BEFORE MAGISTRATES. It covers Section 228: Magistrate may dispense with personal attendance of accused.]

228. Magist...
- `BNSS_190`: [Context: This section is from BNSS 2023, CHAPTER XIII INFORMATION TO THE POLICE AND THEIR POWERS TO INVESTIGATE. It covers Section 190: Cases to be sent to Magistrate, when evidence is sufficient.]

...
- `BNSS_267`: [Context: This section is from BNSS 2023, CHAPTER XX TRIAL OF WARRANT-CASES BY MAGISTRATES. It covers Section 267: Evidence for prosecution.]

267. Evidence for prosecution.—(1) When, in any warrant-c...
- `BNSS_261`: [Context: This section is from BNSS 2023, CHAPTER XX TRIAL OF WARRANT-CASES BY MAGISTRATES. It covers Section 261: Compliance with section 230.]

261. Compliance with section 230.—When, in any warrant...
- `BNSS_227`: [Context: This section is from BNSS 2023, CHAPTER XVII COMMENCEMENT OF PROCEEDINGS BEFORE MAGISTRATES. It covers Section 227: Issue of process.]

227. Issue of process.—(1) If in the opinion of a Magi...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 17 — scenario

**Question:** If a person claims that a website or a voice mail message stored on a digital device is a document, is this legally correct?

**Gold section (BSA_2):**
> [Context: This section is from BSA 2023, CHAPTER I PRELIMINARY. It covers Section 2: Definitions.]

2. Definitions.— (1) In this Adhiniyam, unless the context otherwise requires,—
(a) “Court” includes all Judges and Magistrates, and all persons, except arbitrators, legally
authorised to take evidence;
(b) “conclusive proof” means when one fact is declared by this Adhiniyam to be conclusive proof
o...

**Gold answer (reference):** Yes, under clause (d), an electronic record on emails, server logs, documents on computers, laptops or smartphones, messages, websites, locational evidence, and voice mail messages stored on digital devices are all explicitly considered documents. [Source: Section 2, BSA 2023]...

**Top-5 retrieved instead:**
- `BSA_81`: [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 81: Presumption as to Gazettes in electronic or digital record.]

81. Presumption as to Gazettes in electr...
- `BSA_61`: [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 61: Electronic or digital record.]

61. Electronic or digital record.—Nothing in this Adhiniyam shall appl...
- `BSA_63`: [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 63: Admissibility of electronic records.]

63. Admissibility of electronic records.—(1) Notwithstanding an...
- `BSA_90`: [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 90: Presumption as to electronic messages.]

90. Presumption as to electronic messages.—The Court may pres...
- `BSA_80`: [Context: This section is from BSA 2023, CHAPTER V OF DOCUMENTARY EVIDENCE. It covers Section 80: Presumption as to Gazettes, newspapers, and other documents.]

80. Presumption as to Gazettes, newspap...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 18 — scenario

**Question:** A lawyer argues that a search warrant was executed improperly because it was sent by post to an outside jurisdiction, claiming that rule only applies to arrest warrants. Is the lawyer correct?

**Gold section (BNSS_102):**
> [Context: This section is from BNSS 2023, CHAPTER VII PROCESSES TO COMPEL THE PRODUCTION OF THINGS. It covers Section 102: Direction, etc., of search-warrants.]

102. Direction, etc., of search-warrants.—The provisions of sections 32, 72, 74, 76, 79, 80 and 81
shall, so far as may be, apply to all search-warrants issued under section 96, section 97, section 98 or
section 100....

**Gold answer (reference):** No, Section 102 explicitly makes the provisions of Section 80 (which allows forwarding warrants outside jurisdiction) applicable "to all search-warrants issued under section 96, section 97, section 98 or section 100." [Source: Section 102, BNSS 2023]...

**Top-5 retrieved instead:**
- `BNSS_79`: [Context: This section is from BNSS 2023, CHAPTER VI PROCESSES TO COMPEL APPEARANCE. It covers Section 79: Where warrant may be executed.]

79. Where warrant may be executed.—A warrant of arrest may b...
- `BNSS_80`: [Context: This section is from BNSS 2023, CHAPTER VI PROCESSES TO COMPEL APPEARANCE. It covers Section 80: Warrant forwarded for execution outside jurisdiction.]

80. Warrant forwarded for execution o...
- `BNSS_462`: [Context: This section is from BNSS 2023, CHAPTER XXXIV EXECUTION, SUSPENSION, REMISSION AND COMMUTATION OF SENTENCES. It covers Section 462: Effect of such warrant.]

462. Effect of such warrant.—A w...
- `BNSS_104`: [Context: This section is from BNSS 2023, CHAPTER VII PROCESSES TO COMPEL THE PRODUCTION OF THINGS. It covers Section 104: Disposal of things found in search beyond jurisdiction.]

104. Disposal of th...
- `BNSS_110`: [Context: This section is from BNSS 2023, CHAPTER VII PROCESSES TO COMPEL THE PRODUCTION OF THINGS. It covers Section 110: Reciprocal arrangements regarding processes.]

110. Reciprocal arrangements r...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 19 — scenario

**Question:** A citizen alleges a police officer beat him during a riot control operation. The citizen tries to file a case in court. The officer claims he was discharging his official duty. Does the court need permission to try the officer?

**Gold section (BNSS_218):**
> [Context: This section is from BNSS 2023, CHAPTER XV CONDITIONS REQUISITE FOR INITIATION OF PROCEEDINGS. It covers Section 218: Prosecution of Judges and public servants.]

218. Prosecution of Judges and public servants.—(1) When any person who is or was a Judge or
Magistrate or a public servant not removable from his office save by or with the sanction of the Government
is accused of any offence ...

**Gold answer (reference):** Yes, if the officer is a public servant not removable from office save by government sanction, and the act was "while acting or purporting to act in the discharge of his official duty," the court cannot take cognizance "except with the previous sanction" of the relevant Government. [Source: Section ...

**Top-5 retrieved instead:**
- `BNSS_340`: [Context: This section is from BNSS 2023, CHAPTER XXVI GENERAL PROVISIONS AS TO INQUIRIES AND TRIALS. It covers Section 340: Right of person against whom proceedings are instituted to be defended.]

3...
- `BNSS_339`: [Context: This section is from BNSS 2023, CHAPTER XXVI GENERAL PROVISIONS AS TO INQUIRIES AND TRIALS. It covers Section 339: Permission to conduct prosecution.]

339. Permission to conduct prosecution...
- `BNSS_175`: [Context: This section is from BNSS 2023, CHAPTER XIII INFORMATION TO THE POLICE AND THEIR POWERS TO INVESTIGATE. It covers Section 175: Police officer’s power to investigate cognizable case.]

175. P...
- `BNSS_223`: [Context: This section is from BNSS 2023, CHAPTER XVI COMPLAINTS TO MAGISTRATES. It covers Section 223: Examination of complainant.]

223. Examination of complainant.—(1) A Magistrate having jurisdict...
- `BNSS_215`: [Context: This section is from BNSS 2023, CHAPTER XV CONDITIONS REQUISITE FOR INITIATION OF PROCEEDINGS. It covers Section 215: Prosecution for contempt of lawful authority of public servants, for off...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

## Miss 20 — scenario

**Question:** A highly organized gang of six armed men storms a bank. Three hold the tellers at gunpoint, two guard the doors, and one waits in the getaway car outside. They steal cash and flee. What is their specific offence?

**Gold section (BNS_310):**
> [Context: This section is from BNS 2023, CHAPTER XVII OF OFFENCES AGAINST PROPERTY. It covers Section 310: Dacoity.]

310. Dacoity.—(1) When five or more persons conjointly commit or attempt to commit a robbery, or
where the whole number of persons conjointly committing or attempting to commit a robbery, and

persons present and aiding such commission or attempt, amount to five or more, every pers...

**Gold answer (reference):** Because five or more persons conjointly committed a robbery (including those present and aiding), every person involved is said to commit dacoity, punishable under Section 310. [Source: Section 310, BNS 2023]...

**Top-5 retrieved instead:**
- `BNS_189`: [Context: This section is from BNS 2023, CHAPTER XI OF OFFENCES AGAINST THE PUBLIC TRANQUILLITY. It covers Section 189: Unlawful assembly.]

189. Unlawful assembly.—(1) An assembly of five or more per...
- `BNS_57`: [Context: This section is from BNS 2023, CHAPTER IV OF ABETMENT, CRIMINAL CONSPIRACY AND ATTEMPT. It covers Section 57: Abetting commission of offence by public or by more than ten persons.]

57. Abet...
- `BNSS_148`: [Context: This section is from BNSS 2023, CHAPTER XI MAINTENANCE OF PUBLIC ORDER AND TRANQUILLITY. It covers Section 148: Dispersal of assembly by use of civil force.]

148. Dispersal of assembly by u...
- `BNS_313`: [Context: This section is from BNS 2023, CHAPTER XVII OF OFFENCES AGAINST PROPERTY. It covers Section 313: Punishment for belonging to gang of robbers, etc.]

313. Punishment for belonging to gang of ...
- `BNS_32`: [Context: This section is from BNS 2023, CHAPTER III GENERAL EXCEPTIONS. It covers Section 32: Act to which a person is compelled by threats.]

32. Act to which a person is compelled by threats.—Excep...

**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read

---

