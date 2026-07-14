from __future__ import annotations

import hashlib
import logging
import sys
import time
import uuid

from hybrid_retriever.config import HybridConfig
from hybrid_retriever.elasticsearch_client import ElasticsearchRetriever
from hybrid_retriever.qdrant_client import QdrantRetriever
from hybrid_retriever.embedding_provider import EmbedderWrapper
from hybrid_retriever.metadata_filter import extract_filters
from hybrid_retriever.fusion import reciprocal_rank_fusion
from hybrid_retriever.ranker import rank_and_truncate
from hybrid_retriever.citation_validator import validate_citations
from hybrid_retriever.validator import verify_output
from hybrid_retriever.response_builder import build_response
from hybrid_retriever.reporter import generate_reports
from hybrid_retriever.models import RetrievalTrace

logger = logging.getLogger("hybrid_retriever")

# ---------------------------------------------------------------------------
# In-memory mock corpus — 40 representative Indian legal chunks.
# Used ONLY when use_mock=True so Render (and CI) never touch the filesystem.
# Covers: GST, Income Tax, Constitution, Contract Law, Consumer Law,
#          Companies Act, Criminal Law, Labour Law, Evidence Law, RTI.
# ---------------------------------------------------------------------------
_MOCK_LEGAL_CHUNKS: list[dict] = [
    # ===== GST (5 chunks) =====
    {
        "chunk_id": "gst-001",
        "document_id": "doc-cgst-act-2017",
        "parent_document_id": "doc-cgst-act-2017",
        "document_title": "Central Goods and Services Tax Act, 2017 — Section 9",
        "category": "Acts / Statutes",
        "text": (
            "The Goods and Services Tax (GST) is a comprehensive, destination-based indirect tax "
            "levied on the supply of goods and services across India. Section 9 of the CGST Act, "
            "2017 provides the charging section and states that there shall be levied a tax called "
            "the Central Goods and Services Tax on all intra-State supplies of goods or services or "
            "both, except on the supply of alcoholic liquor for human consumption, at rates not "
            "exceeding twenty per cent as recommended by the GST Council. The tax is collected at "
            "every stage of the supply chain with the benefit of input tax credit available at each "
            "stage, thereby eliminating the cascading effect of taxes that existed under the previous "
            "regime of excise duty, service tax, and value added tax."
        ),
        "citation": "CGST Act, 2017 § 9",
        "cross_references": ["CGST Act, 2017 § 16", "IGST Act, 2017 § 5"],
        "page_start": 18,
        "page_end": 20,
        "hierarchy_level": 1,
        "chunk_hash": "gst001a1b2c3",
    },
    {
        "chunk_id": "gst-002",
        "document_id": "doc-cgst-act-2017",
        "parent_document_id": "doc-cgst-act-2017",
        "document_title": "Central Goods and Services Tax Act, 2017 — Section 16",
        "category": "Acts / Statutes",
        "text": (
            "Section 16 of the CGST Act, 2017 governs Input Tax Credit (ITC). Every registered "
            "person shall be entitled to take credit of input tax charged on any supply of goods or "
            "services or both which are used or intended to be used in the course or furtherance of "
            "his business. To claim ITC, the registered person must possess a valid tax invoice or "
            "debit note issued by a registered supplier, must have received the goods or services, "
            "the tax charged must have been actually paid to the Government by the supplier, and the "
            "registered person must have furnished the return under Section 39. Where goods are "
            "received in lots or instalments, the credit shall be available upon receipt of the "
            "last lot or instalment. ITC must be claimed before the due date of the return for "
            "September following the end of the financial year or the date of furnishing of the "
            "annual return, whichever is earlier."
        ),
        "citation": "CGST Act, 2017 § 16",
        "cross_references": ["CGST Act, 2017 § 17", "CGST Act, 2017 § 39"],
        "page_start": 32,
        "page_end": 35,
        "hierarchy_level": 1,
        "chunk_hash": "gst002d4e5f6",
    },
    {
        "chunk_id": "gst-003",
        "document_id": "doc-cgst-act-2017",
        "parent_document_id": "doc-cgst-act-2017",
        "document_title": "Central Goods and Services Tax Act, 2017 — Section 2(52)",
        "category": "Acts / Statutes",
        "text": (
            "Section 2(52) of the CGST Act defines 'goods' as every kind of movable property "
            "other than money and securities but includes actionable claims, growing crops, grass "
            "and things attached to or forming part of the land which are agreed to be severed "
            "before supply or under a contract of supply. GST replaced multiple indirect taxes "
            "including Central Excise Duty, Service Tax, VAT, Central Sales Tax, Entry Tax, "
            "Luxury Tax, and Entertainment Tax with a single unified tax. The GST Council, a "
            "constitutional body under Article 279A, recommends the rates, exemptions, and "
            "thresholds applicable under the GST regime."
        ),
        "citation": "CGST Act, 2017 § 2(52)",
        "cross_references": ["CGST Act, 2017 § 7", "Constitution of India Art. 279A"],
        "page_start": 5,
        "page_end": 7,
        "hierarchy_level": 1,
        "chunk_hash": "gst003g7h8i9",
    },
    {
        "chunk_id": "gst-004",
        "document_id": "doc-igst-act-2017",
        "parent_document_id": "doc-igst-act-2017",
        "document_title": "Integrated Goods and Services Tax Act, 2017 — Section 5",
        "category": "Acts / Statutes",
        "text": (
            "Section 5 of the IGST Act, 2017 provides that Integrated GST shall be levied on "
            "all inter-State supplies of goods or services or both. The IGST is collected by the "
            "Central Government and apportioned between the Centre and the destination State. This "
            "mechanism ensures that the tax revenue accrues to the consuming State rather than the "
            "producing State, fulfilling the destination principle. The IGST rate is generally equal "
            "to the sum of CGST and SGST rates. For import of goods, IGST is levied under the "
            "Customs Tariff Act in addition to basic customs duty."
        ),
        "citation": "IGST Act, 2017 § 5",
        "cross_references": ["CGST Act, 2017 § 9", "IGST Act, 2017 § 7"],
        "page_start": 10,
        "page_end": 12,
        "hierarchy_level": 1,
        "chunk_hash": "gst004j0k1l2",
    },
    {
        "chunk_id": "gst-005",
        "document_id": "doc-cgst-act-2017",
        "parent_document_id": "doc-cgst-act-2017",
        "document_title": "Central Goods and Services Tax Act, 2017 — Section 22",
        "category": "Acts / Statutes",
        "text": (
            "Section 22 of the CGST Act prescribes that every supplier whose aggregate turnover "
            "in a financial year exceeds the threshold limit of twenty lakh rupees (ten lakh rupees "
            "for special category States) is required to obtain GST registration. The composition "
            "scheme under Section 10 allows small taxpayers with turnover up to one and a half "
            "crore rupees to pay GST at a fixed rate on turnover without the benefit of input tax "
            "credit. Registered persons are required to file periodic returns including GSTR-1 for "
            "outward supplies and GSTR-3B as a summary return."
        ),
        "citation": "CGST Act, 2017 § 22",
        "cross_references": ["CGST Act, 2017 § 10", "CGST Act, 2017 § 25"],
        "page_start": 42,
        "page_end": 44,
        "hierarchy_level": 1,
        "chunk_hash": "gst005m3n4o5",
    },
    # ===== Income Tax (4 chunks) =====
    {
        "chunk_id": "itax-001",
        "document_id": "doc-it-act-1961",
        "parent_document_id": "doc-it-act-1961",
        "document_title": "Income Tax Act, 1961 — Section 4",
        "category": "Acts / Statutes",
        "text": (
            "Section 4 of the Income Tax Act, 1961 is the charging section which provides that "
            "income tax shall be charged for any assessment year at the rates laid down by the "
            "Finance Act for that year in respect of the total income of the previous year of "
            "every person. The total income is computed after allowing all deductions under "
            "Chapter VI-A (Sections 80C to 80U). The Act classifies income under five heads: "
            "salary, house property, profits and gains of business or profession, capital gains, "
            "and income from other sources. Tax liability depends on residential status which "
            "determines the scope of taxable income."
        ),
        "citation": "Income Tax Act, 1961 § 4",
        "cross_references": ["Income Tax Act, 1961 § 5", "Income Tax Act, 1961 § 80C"],
        "page_start": 3,
        "page_end": 5,
        "hierarchy_level": 1,
        "chunk_hash": "itax001p6q7r8",
    },
    {
        "chunk_id": "itax-002",
        "document_id": "doc-it-act-1961",
        "parent_document_id": "doc-it-act-1961",
        "document_title": "Income Tax Act, 1961 — Section 80C",
        "category": "Acts / Statutes",
        "text": (
            "Section 80C of the Income Tax Act allows individual and Hindu Undivided Family (HUF) "
            "assessees to claim deductions from gross total income up to a maximum of one lakh "
            "fifty thousand rupees per financial year. Eligible investments include life insurance "
            "premiums, contributions to the Public Provident Fund (PPF), Employee Provident Fund "
            "(EPF), Equity Linked Savings Scheme (ELSS) mutual funds, National Savings Certificates, "
            "five-year fixed deposits, tuition fees for children, and repayment of housing loan "
            "principal. This deduction is among the most widely used tax-saving provisions."
        ),
        "citation": "Income Tax Act, 1961 § 80C",
        "cross_references": ["Income Tax Act, 1961 § 80D", "Income Tax Act, 1961 § 80CCD"],
        "page_start": 145,
        "page_end": 148,
        "hierarchy_level": 1,
        "chunk_hash": "itax002s9t0u1",
    },
    {
        "chunk_id": "itax-003",
        "document_id": "doc-it-act-1961",
        "parent_document_id": "doc-it-act-1961",
        "document_title": "Income Tax Act, 1961 — Section 139",
        "category": "Acts / Statutes",
        "text": (
            "Section 139 of the Income Tax Act mandates the filing of income tax returns. Every "
            "person whose total income exceeds the basic exemption limit must furnish a return of "
            "income before the due date prescribed. Companies, firms, and persons required to get "
            "accounts audited under Section 44AB must file by October 31 of the assessment year. "
            "Belated returns may be filed under Section 139(4) before three months prior to the "
            "end of the relevant assessment year, subject to late fees under Section 234F."
        ),
        "citation": "Income Tax Act, 1961 § 139",
        "cross_references": ["Income Tax Act, 1961 § 44AB", "Income Tax Act, 1961 § 234F"],
        "page_start": 220,
        "page_end": 224,
        "hierarchy_level": 1,
        "chunk_hash": "itax003v2w3x4",
    },
    {
        "chunk_id": "itax-004",
        "document_id": "doc-it-act-1961",
        "parent_document_id": "doc-it-act-1961",
        "document_title": "Income Tax Act, 1961 — Section 45 (Capital Gains)",
        "category": "Acts / Statutes",
        "text": (
            "Section 45 of the Income Tax Act provides that any profits or gains arising from "
            "the transfer of a capital asset shall be chargeable to income tax under the head "
            "'Capital Gains' in the previous year in which the transfer took place. Capital gains "
            "are classified as short-term (where the asset is held for not more than 36 months, "
            "or 12 months for listed equity shares and equity-oriented mutual funds) and long-term. "
            "Long-term capital gains on listed equity shares exceeding one lakh rupees are taxed "
            "at ten per cent without the benefit of indexation under Section 112A."
        ),
        "citation": "Income Tax Act, 1961 § 45",
        "cross_references": ["Income Tax Act, 1961 § 112A", "Income Tax Act, 1961 § 54"],
        "page_start": 85,
        "page_end": 88,
        "hierarchy_level": 1,
        "chunk_hash": "itax004y5z6a7",
    },
    # ===== Constitution of India (5 chunks) =====
    {
        "chunk_id": "const-001",
        "document_id": "doc-constitution-india",
        "parent_document_id": "doc-constitution-india",
        "document_title": "Constitution of India — Article 14",
        "category": "Acts / Statutes",
        "text": (
            "Article 14 of the Constitution of India guarantees equality before the law and "
            "equal protection of the laws within the territory of India. The State shall not deny "
            "to any person equality before the law or the equal protection of the laws. This "
            "article embodies the concept of rule of law. The Supreme Court has held that Article "
            "14 prohibits class legislation but permits reasonable classification, provided the "
            "classification has a rational nexus with the object sought to be achieved by the "
            "statute. Arbitrariness is antithetical to equality and any arbitrary State action "
            "violates Article 14."
        ),
        "citation": "Constitution of India, Art. 14",
        "cross_references": ["Constitution of India, Art. 15", "Constitution of India, Art. 21"],
        "page_start": 8,
        "page_end": 9,
        "hierarchy_level": 0,
        "chunk_hash": "const001b8c9d0",
    },
    {
        "chunk_id": "const-002",
        "document_id": "doc-constitution-india",
        "parent_document_id": "doc-constitution-india",
        "document_title": "Constitution of India — Article 19",
        "category": "Acts / Statutes",
        "text": (
            "Article 19(1) of the Constitution of India confers upon all citizens six fundamental "
            "freedoms: (a) freedom of speech and expression, (b) freedom to assemble peaceably "
            "and without arms, (c) freedom to form associations or unions, (d) freedom to move "
            "freely throughout the territory of India, (e) freedom to reside and settle in any "
            "part of the territory of India, and (g) freedom to practise any profession, or to "
            "carry on any occupation, trade or business. These rights are subject to reasonable "
            "restrictions under Article 19(2) through 19(6) in the interests of sovereignty, "
            "security, public order, decency, morality, and other specified grounds."
        ),
        "citation": "Constitution of India, Art. 19",
        "cross_references": ["Constitution of India, Art. 14", "Constitution of India, Art. 21"],
        "page_start": 10,
        "page_end": 13,
        "hierarchy_level": 0,
        "chunk_hash": "const002e1f2g3",
    },
    {
        "chunk_id": "const-003",
        "document_id": "doc-constitution-india",
        "parent_document_id": "doc-constitution-india",
        "document_title": "Constitution of India — Article 21",
        "category": "Acts / Statutes",
        "text": (
            "Article 21 of the Constitution of India provides that no person shall be deprived "
            "of his life or personal liberty except according to the procedure established by law. "
            "The Supreme Court in Maneka Gandhi v. Union of India (1978) expanded its interpretation "
            "to require that the procedure must be fair, just, and reasonable. Article 21 has been "
            "interpreted to include the right to live with dignity, the right to livelihood, the "
            "right to privacy (K.S. Puttaswamy v. Union of India, 2017), the right to clean "
            "environment, the right to health, the right to education (reinforced by Article 21A), "
            "the right to shelter, and the right to speedy trial. It is the most expansively "
            "interpreted fundamental right in Indian constitutional jurisprudence."
        ),
        "citation": "Constitution of India, Art. 21",
        "cross_references": ["Constitution of India, Art. 14", "Constitution of India, Art. 21A"],
        "page_start": 14,
        "page_end": 16,
        "hierarchy_level": 0,
        "chunk_hash": "const003h4i5j6",
    },
    {
        "chunk_id": "const-004",
        "document_id": "doc-constitution-india",
        "parent_document_id": "doc-constitution-india",
        "document_title": "Constitution of India — Article 32",
        "category": "Acts / Statutes",
        "text": (
            "Article 32 of the Constitution of India guarantees the right to move the Supreme "
            "Court for enforcement of fundamental rights. Dr. B.R. Ambedkar described it as the "
            "'heart and soul of the Constitution.' The Supreme Court may issue directions, orders, "
            "or writs including habeas corpus, mandamus, prohibition, quo warranto, and certiorari "
            "for the enforcement of any of the fundamental rights conferred by Part III. This "
            "right cannot be suspended except during a proclamation of emergency under Article 359. "
            "The corresponding right to approach High Courts is provided under Article 226."
        ),
        "citation": "Constitution of India, Art. 32",
        "cross_references": ["Constitution of India, Art. 226", "Constitution of India, Art. 359"],
        "page_start": 22,
        "page_end": 24,
        "hierarchy_level": 0,
        "chunk_hash": "const004k7l8m9",
    },
    {
        "chunk_id": "const-005",
        "document_id": "doc-constitution-india",
        "parent_document_id": "doc-constitution-india",
        "document_title": "Constitution of India — Article 15",
        "category": "Acts / Statutes",
        "text": (
            "Article 15 of the Constitution of India prohibits the State from discriminating "
            "against any citizen on grounds only of religion, race, caste, sex, or place of birth. "
            "No citizen shall be subjected to any disability, liability, restriction, or condition "
            "with regard to access to shops, public restaurants, hotels, and places of public "
            "entertainment, or the use of wells, tanks, bathing ghats, roads, and places of public "
            "resort maintained wholly or partly out of State funds. However, the State may make "
            "special provisions for women, children, socially and educationally backward classes, "
            "Scheduled Castes, and Scheduled Tribes under Articles 15(3), 15(4), and 15(5)."
        ),
        "citation": "Constitution of India, Art. 15",
        "cross_references": ["Constitution of India, Art. 14", "Constitution of India, Art. 16"],
        "page_start": 9,
        "page_end": 10,
        "hierarchy_level": 0,
        "chunk_hash": "const005n0o1p2",
    },
    # ===== Contract Law (4 chunks) =====
    {
        "chunk_id": "contract-001",
        "document_id": "doc-ica-1872",
        "parent_document_id": "doc-ica-1872",
        "document_title": "Indian Contract Act, 1872 — Section 10",
        "category": "Acts / Statutes",
        "text": (
            "Section 10 of the Indian Contract Act, 1872 provides that all agreements are "
            "contracts if they are made by the free consent of parties competent to contract, for "
            "a lawful consideration, with a lawful object, and are not expressly declared to be "
            "void. A valid contract therefore requires: (1) an offer and acceptance constituting "
            "agreement, (2) free consent (not obtained by coercion, undue influence, fraud, "
            "misrepresentation, or mistake), (3) capacity of parties (persons of sound mind who "
            "have attained the age of majority), (4) lawful consideration, (5) lawful object, and "
            "(6) the agreement must not be one that the Act declares void."
        ),
        "citation": "Indian Contract Act, 1872 § 10",
        "cross_references": ["Indian Contract Act, 1872 § 2", "Indian Contract Act, 1872 § 14"],
        "page_start": 5,
        "page_end": 7,
        "hierarchy_level": 1,
        "chunk_hash": "con001q3r4s5",
    },
    {
        "chunk_id": "contract-002",
        "document_id": "doc-ica-1872",
        "parent_document_id": "doc-ica-1872",
        "document_title": "Indian Contract Act, 1872 — Section 2",
        "category": "Acts / Statutes",
        "text": (
            "Section 2 of the Indian Contract Act defines key terms. A 'proposal' or 'offer' is "
            "made when one person signifies to another his willingness to do or to abstain from "
            "doing anything with a view to obtaining the assent of that other. When the person to "
            "whom the proposal is made signifies his assent, the proposal is said to be accepted "
            "and becomes a 'promise.' An 'agreement' is every promise and every set of promises "
            "forming the consideration for each other. A 'contract' is an agreement enforceable by "
            "law. An agreement which is enforceable by law at the option of one party but not at "
            "the option of the other is a 'voidable contract.'"
        ),
        "citation": "Indian Contract Act, 1872 § 2",
        "cross_references": ["Indian Contract Act, 1872 § 10", "Indian Contract Act, 1872 § 25"],
        "page_start": 1,
        "page_end": 3,
        "hierarchy_level": 1,
        "chunk_hash": "con002t6u7v8",
    },
    {
        "chunk_id": "contract-003",
        "document_id": "doc-ica-1872",
        "parent_document_id": "doc-ica-1872",
        "document_title": "Indian Contract Act, 1872 — Sections 73-74 (Breach and Remedies)",
        "category": "Acts / Statutes",
        "text": (
            "When a contract has been broken, the party who suffers by such breach is entitled to "
            "receive compensation for any loss or damage caused to him thereby under Section 73 of "
            "the Indian Contract Act, 1872. The compensation is limited to loss or damage naturally "
            "arising in the usual course of things from such breach, or which the parties knew at "
            "the time of the contract to be likely to result from the breach. Section 74 provides "
            "that when a contract contains a stipulated sum payable as penalty or liquidated damages "
            "for breach, the party complaining of the breach is entitled to receive reasonable "
            "compensation not exceeding the amount so named."
        ),
        "citation": "Indian Contract Act, 1872 §§ 73-74",
        "cross_references": ["Indian Contract Act, 1872 § 39", "Specific Relief Act, 1963 § 10"],
        "page_start": 55,
        "page_end": 58,
        "hierarchy_level": 1,
        "chunk_hash": "con003w9x0y1",
    },
    {
        "chunk_id": "contract-004",
        "document_id": "doc-ica-1872",
        "parent_document_id": "doc-ica-1872",
        "document_title": "Indian Contract Act, 1872 — Section 27 (Restraint of Trade)",
        "category": "Acts / Statutes",
        "text": (
            "Section 27 of the Indian Contract Act declares that every agreement by which any one "
            "is restrained from exercising a lawful profession, trade, or business of any kind is "
            "to that extent void. The sole exception is the sale of goodwill where the seller may "
            "agree not to carry on a similar business within specified local limits, provided such "
            "limits are reasonable. Unlike English law, Indian law does not recognise partial "
            "restraint of trade; any restraint, whether reasonable or not, renders the agreement "
            "void to the extent of the restraint."
        ),
        "citation": "Indian Contract Act, 1872 § 27",
        "cross_references": ["Indian Contract Act, 1872 § 26", "Indian Contract Act, 1872 § 28"],
        "page_start": 18,
        "page_end": 19,
        "hierarchy_level": 1,
        "chunk_hash": "con004z2a3b4",
    },
    # ===== Consumer Law (4 chunks) =====
    {
        "chunk_id": "consumer-001",
        "document_id": "doc-cpa-2019",
        "parent_document_id": "doc-cpa-2019",
        "document_title": "Consumer Protection Act, 2019 — Section 2(7)",
        "category": "Acts / Statutes",
        "text": (
            "The Consumer Protection Act, 2019 defines a 'consumer' under Section 2(7) as any "
            "person who buys any goods for a consideration, or hires or avails of any service for "
            "a consideration, and includes any user of such goods or beneficiary of such service "
            "when such use is made with the approval of the buyer. It does not include a person "
            "who obtains goods for resale or for any commercial purpose, except a person who buys "
            "goods and uses them exclusively for self-employment. The Act provides a three-tier "
            "redressal mechanism: District Commission (claims up to one crore rupees), State "
            "Commission (one crore to ten crore rupees), and National Commission (above ten crore)."
        ),
        "citation": "Consumer Protection Act, 2019 § 2(7)",
        "cross_references": ["Consumer Protection Act, 2019 § 34", "Consumer Protection Act, 2019 § 47"],
        "page_start": 3,
        "page_end": 5,
        "hierarchy_level": 1,
        "chunk_hash": "cpa001c5d6e7",
    },
    {
        "chunk_id": "consumer-002",
        "document_id": "doc-cpa-2019",
        "parent_document_id": "doc-cpa-2019",
        "document_title": "Consumer Protection Act, 2019 — Section 2(6) (Consumer Dispute)",
        "category": "Acts / Statutes",
        "text": (
            "A consumer dispute arises when a person against whom a complaint has been made denies "
            "or disputes the allegations contained in the complaint. The Act addresses six types of "
            "unfair trade practices and provides remedies including refund of the price paid, "
            "removal of defects, replacement of goods, compensation for loss or injury, "
            "discontinuance of unfair or restrictive trade practices, and adequate costs. The 2019 "
            "Act introduced provisions for product liability, e-commerce, and mediation as an "
            "alternate dispute resolution mechanism."
        ),
        "citation": "Consumer Protection Act, 2019 § 2(6)",
        "cross_references": ["Consumer Protection Act, 2019 § 83", "Consumer Protection Act, 2019 § 2(47)"],
        "page_start": 2,
        "page_end": 4,
        "hierarchy_level": 1,
        "chunk_hash": "cpa002f8g9h0",
    },
    {
        "chunk_id": "consumer-003",
        "document_id": "doc-cpa-2019",
        "parent_document_id": "doc-cpa-2019",
        "document_title": "Consumer Protection Act, 2019 — Sections 82-87 (Product Liability)",
        "category": "Acts / Statutes",
        "text": (
            "Chapter VI of the Consumer Protection Act, 2019 introduces product liability for "
            "the first time in Indian law. A product liability action may be brought by a "
            "complainant against a product manufacturer, product service provider, or product "
            "seller for any harm caused by a defective product or deficiency in services. A "
            "product manufacturer is liable if the product contains a manufacturing defect, is "
            "defective in design, deviates from manufacturing specifications, does not conform to "
            "the express warranty, or fails to contain adequate instructions or warnings. The "
            "product seller is liable if he has exercised substantial control over the design, "
            "testing, manufacture, or labelling of the product."
        ),
        "citation": "Consumer Protection Act, 2019 §§ 82-87",
        "cross_references": ["Consumer Protection Act, 2019 § 2(34)", "Consumer Protection Act, 2019 § 2(36)"],
        "page_start": 62,
        "page_end": 66,
        "hierarchy_level": 1,
        "chunk_hash": "cpa003i1j2k3",
    },
    {
        "chunk_id": "consumer-004",
        "document_id": "doc-cpa-2019",
        "parent_document_id": "doc-cpa-2019",
        "document_title": "Consumer Protection Act, 2019 — Central Consumer Protection Authority",
        "category": "Acts / Statutes",
        "text": (
            "Sections 10 to 22 of the Consumer Protection Act, 2019 establish the Central "
            "Consumer Protection Authority (CCPA) to promote, protect, and enforce the rights of "
            "consumers. The CCPA has the power to conduct investigations into violations of "
            "consumer rights, institute complaints before the District Commission, order recall "
            "of unsafe goods or withdrawal of unsafe services, impose penalties for misleading "
            "advertisements, and issue directions against false or misleading advertisements. The "
            "CCPA may impose a penalty of up to ten lakh rupees on a manufacturer or endorser for "
            "a first offence of false or misleading advertisement, and up to fifty lakh rupees for "
            "subsequent offences."
        ),
        "citation": "Consumer Protection Act, 2019 §§ 10-22",
        "cross_references": ["Consumer Protection Act, 2019 § 18", "Consumer Protection Act, 2019 § 21"],
        "page_start": 12,
        "page_end": 18,
        "hierarchy_level": 1,
        "chunk_hash": "cpa004l4m5n6",
    },
    # ===== Companies Act (4 chunks) =====
    {
        "chunk_id": "company-001",
        "document_id": "doc-companies-act-2013",
        "parent_document_id": "doc-companies-act-2013",
        "document_title": "Companies Act, 2013 — Section 2(20) (Definition of Company)",
        "category": "Acts / Statutes",
        "text": (
            "Section 2(20) of the Companies Act, 2013 defines a 'company' as a company "
            "incorporated under this Act or under any previous company law. A company is an "
            "artificial person created by law, having a separate legal entity, perpetual "
            "succession, and a common seal. The Act recognises several types of companies "
            "including private companies (minimum two members, maximum two hundred), public "
            "companies (minimum seven members), one person companies (single member), small "
            "companies, and Section 8 companies (not-for-profit). The minimum paid-up capital "
            "requirement has been removed by the Companies (Amendment) Act, 2015."
        ),
        "citation": "Companies Act, 2013 § 2(20)",
        "cross_references": ["Companies Act, 2013 § 3", "Companies Act, 2013 § 2(68)"],
        "page_start": 5,
        "page_end": 7,
        "hierarchy_level": 1,
        "chunk_hash": "comp001o7p8q9",
    },
    {
        "chunk_id": "company-002",
        "document_id": "doc-companies-act-2013",
        "parent_document_id": "doc-companies-act-2013",
        "document_title": "Companies Act, 2013 — Section 166 (Duties of Directors)",
        "category": "Acts / Statutes",
        "text": (
            "Section 166 of the Companies Act, 2013 codifies the duties of directors. A director "
            "shall act in accordance with the articles of the company and in good faith to promote "
            "the objects of the company for the benefit of its members as a whole and in the best "
            "interests of the company, its employees, the shareholders, the community, and for the "
            "protection of the environment. A director shall exercise his duties with due and "
            "reasonable care, skill, and diligence and shall not be involved in any situation in "
            "which he may have a direct or indirect interest that conflicts with the interest of "
            "the company. Contravention is punishable with a fine not less than one lakh rupees "
            "extending to five lakh rupees."
        ),
        "citation": "Companies Act, 2013 § 166",
        "cross_references": ["Companies Act, 2013 § 149", "Companies Act, 2013 § 197"],
        "page_start": 140,
        "page_end": 143,
        "hierarchy_level": 1,
        "chunk_hash": "comp002r0s1t2",
    },
    {
        "chunk_id": "company-003",
        "document_id": "doc-companies-act-2013",
        "parent_document_id": "doc-companies-act-2013",
        "document_title": "Companies Act, 2013 — Section 447 (Fraud)",
        "category": "Acts / Statutes",
        "text": (
            "Section 447 of the Companies Act, 2013 provides stringent punishment for fraud. Any "
            "person who is found guilty of fraud involving an amount of at least ten lakh rupees "
            "or one per cent of the turnover of the company, whichever is lower, shall be "
            "punishable with imprisonment for a term not less than six months extending to ten "
            "years and shall also be liable to a fine not less than the amount involved in the "
            "fraud extending to three times that amount. Where the fraud involves public interest, "
            "the imprisonment shall not be less than three years. The National Financial Reporting "
            "Authority (NFRA) has oversight over auditing standards and may act in cases of fraud."
        ),
        "citation": "Companies Act, 2013 § 447",
        "cross_references": ["Companies Act, 2013 § 448", "Companies Act, 2013 § 132"],
        "page_start": 310,
        "page_end": 312,
        "hierarchy_level": 1,
        "chunk_hash": "comp003u3v4w5",
    },
    {
        "chunk_id": "company-004",
        "document_id": "doc-companies-act-2013",
        "parent_document_id": "doc-companies-act-2013",
        "document_title": "Companies Act, 2013 — Section 135 (Corporate Social Responsibility)",
        "category": "Acts / Statutes",
        "text": (
            "Section 135 of the Companies Act, 2013 mandates that every company having a net worth "
            "of five hundred crore rupees or more, or turnover of one thousand crore rupees or "
            "more, or a net profit of five crore rupees or more during the immediately preceding "
            "financial year shall constitute a Corporate Social Responsibility (CSR) Committee of "
            "the Board. The company shall spend at least two per cent of the average net profits "
            "of the three immediately preceding financial years on CSR activities specified in "
            "Schedule VII, which includes eradicating hunger and poverty, promoting education, "
            "gender equality, environmental sustainability, and rural development."
        ),
        "citation": "Companies Act, 2013 § 135",
        "cross_references": ["Companies Act, 2013, Schedule VII", "Companies (CSR Policy) Rules, 2014"],
        "page_start": 108,
        "page_end": 111,
        "hierarchy_level": 1,
        "chunk_hash": "comp004x6y7z8",
    },
    # ===== Criminal Law (4 chunks) =====
    {
        "chunk_id": "crim-001",
        "document_id": "doc-ipc-1860",
        "parent_document_id": "doc-ipc-1860",
        "document_title": "Indian Penal Code, 1860 — Sections 299-304 (Culpable Homicide & Murder)",
        "category": "Acts / Statutes",
        "text": (
            "Section 299 of the Indian Penal Code defines culpable homicide as causing death by "
            "doing an act with the intention of causing death, or with the intention of causing "
            "such bodily injury as is likely to cause death, or with the knowledge that the act "
            "is likely to cause death. Section 300 elevates culpable homicide to murder when the "
            "act is done with the intention of causing death, or with the intention of causing "
            "bodily injury which the offender knows to be likely to cause death of the person, or "
            "if the bodily injury intended is sufficient in the ordinary course of nature to cause "
            "death. Murder is punishable with death or imprisonment for life under Section 302."
        ),
        "citation": "Indian Penal Code, 1860 §§ 299-304",
        "cross_references": ["IPC § 302", "CrPC § 154", "IPC § 304A"],
        "page_start": 142,
        "page_end": 148,
        "hierarchy_level": 1,
        "chunk_hash": "crim001a9b0c1",
    },
    {
        "chunk_id": "crim-002",
        "document_id": "doc-ipc-1860",
        "parent_document_id": "doc-ipc-1860",
        "document_title": "Indian Penal Code, 1860 — Sections 378-382 (Theft)",
        "category": "Acts / Statutes",
        "text": (
            "Section 378 of the Indian Penal Code defines theft as intending to take dishonestly "
            "any moveable property out of the possession of any person without that person's "
            "consent and moving that property in order to effect such taking. Theft is punishable "
            "under Section 379 with imprisonment of either description for a term which may extend "
            "to three years, or with fine, or with both. Theft in a dwelling house or by a clerk "
            "or servant (Section 380-381) attracts enhanced punishment of up to seven years. "
            "Theft after preparation made for causing death, hurt, or restraint is punishable with "
            "rigorous imprisonment up to ten years under Section 382."
        ),
        "citation": "Indian Penal Code, 1860 §§ 378-382",
        "cross_references": ["IPC § 383 (Extortion)", "IPC § 390 (Robbery)"],
        "page_start": 180,
        "page_end": 184,
        "hierarchy_level": 1,
        "chunk_hash": "crim002d2e3f4",
    },
    {
        "chunk_id": "crim-003",
        "document_id": "doc-crpc-1973",
        "parent_document_id": "doc-crpc-1973",
        "document_title": "Code of Criminal Procedure, 1973 — Section 154 (FIR)",
        "category": "Acts / Statutes",
        "text": (
            "Section 154 of the Code of Criminal Procedure, 1973 provides for the recording of "
            "information in cognizable cases, commonly known as the First Information Report (FIR). "
            "Every information relating to the commission of a cognizable offence, if given orally "
            "to an officer in charge of a police station, shall be reduced to writing by him or "
            "under his direction, read over to the informant, and signed by the informant. A copy "
            "of the information so recorded shall be given forthwith, free of cost, to the "
            "informant. The Supreme Court in Lalita Kumari v. Government of U.P. (2014) held that "
            "registration of an FIR is mandatory under Section 154 when information discloses "
            "commission of a cognizable offence and no preliminary inquiry is permissible."
        ),
        "citation": "CrPC, 1973 § 154",
        "cross_references": ["CrPC § 155", "CrPC § 173", "IPC § 182"],
        "page_start": 85,
        "page_end": 88,
        "hierarchy_level": 1,
        "chunk_hash": "crim003g5h6i7",
    },
    {
        "chunk_id": "crim-004",
        "document_id": "doc-crpc-1973",
        "parent_document_id": "doc-crpc-1973",
        "document_title": "Code of Criminal Procedure, 1973 — Section 438 (Anticipatory Bail)",
        "category": "Acts / Statutes",
        "text": (
            "Section 438 of the CrPC empowers the Court of Session or the High Court to grant "
            "anticipatory bail. When any person has reason to believe that he may be arrested on "
            "accusation of having committed a non-bailable offence, he may apply for a direction "
            "that in the event of arrest he shall be released on bail. The court may impose "
            "conditions including making the applicant available for interrogation, not making any "
            "inducement or threat to witnesses, and not leaving India without prior permission. "
            "The Supreme Court in Sushila Aggarwal v. State (2020) held that anticipatory bail "
            "can be granted without any time limit and need not be limited to a fixed period."
        ),
        "citation": "CrPC, 1973 § 438",
        "cross_references": ["CrPC § 437", "CrPC § 439"],
        "page_start": 260,
        "page_end": 263,
        "hierarchy_level": 1,
        "chunk_hash": "crim004j8k9l0",
    },
    # ===== Labour Law (4 chunks) =====
    {
        "chunk_id": "labour-001",
        "document_id": "doc-id-act-1947",
        "parent_document_id": "doc-id-act-1947",
        "document_title": "Industrial Disputes Act, 1947 — Section 2(k) (Industrial Dispute)",
        "category": "Acts / Statutes",
        "text": (
            "Section 2(k) of the Industrial Disputes Act, 1947 defines an 'industrial dispute' "
            "as any dispute or difference between employers and employers, between employers and "
            "workmen, or between workmen and workmen, which is connected with the employment or "
            "non-employment or the terms of employment or the conditions of labour of any person. "
            "The Act provides for investigation and settlement of disputes through conciliation "
            "officers, boards of conciliation, courts of inquiry, labour courts, industrial "
            "tribunals, and the National Industrial Tribunal. Strikes and lockouts in public "
            "utility services without notice are prohibited under Sections 22 and 23."
        ),
        "citation": "Industrial Disputes Act, 1947 § 2(k)",
        "cross_references": ["ID Act § 10", "ID Act § 25F", "ID Act § 25N"],
        "page_start": 2,
        "page_end": 4,
        "hierarchy_level": 1,
        "chunk_hash": "lab001m1n2o3",
    },
    {
        "chunk_id": "labour-002",
        "document_id": "doc-id-act-1947",
        "parent_document_id": "doc-id-act-1947",
        "document_title": "Industrial Disputes Act, 1947 — Section 25F (Retrenchment)",
        "category": "Acts / Statutes",
        "text": (
            "Section 25F of the Industrial Disputes Act, 1947 provides that no workman employed "
            "in any industry who has been in continuous service for not less than one year under "
            "an employer shall be retrenched by that employer until the workman has been given one "
            "month's notice in writing or wages in lieu of such notice, compensation equivalent to "
            "fifteen days' average pay for every completed year of continuous service, and notice "
            "has been served on the appropriate Government. In establishments employing one hundred "
            "or more workmen, Section 25N requires prior permission of the appropriate Government "
            "before retrenchment."
        ),
        "citation": "Industrial Disputes Act, 1947 § 25F",
        "cross_references": ["ID Act § 25N", "ID Act § 25G"],
        "page_start": 30,
        "page_end": 33,
        "hierarchy_level": 1,
        "chunk_hash": "lab002p4q5r6",
    },
    {
        "chunk_id": "labour-003",
        "document_id": "doc-mw-act-1948",
        "parent_document_id": "doc-mw-act-1948",
        "document_title": "Minimum Wages Act, 1948 — Sections 3-5",
        "category": "Acts / Statutes",
        "text": (
            "The Minimum Wages Act, 1948 empowers the appropriate Government to fix minimum rates "
            "of wages in respect of employments listed in the Schedule to the Act. Section 3 "
            "provides that the Government may fix minimum wages for time work (hourly, daily, or "
            "monthly) and piece work. Section 4 requires that minimum wages shall consist of a "
            "basic rate of wages and a cost of living allowance, or a basic rate of wages with or "
            "without the cost of living allowance and the cash value of concessions in respect of "
            "essential commodities. The Act applies to both organised and unorganised sectors and "
            "provides for penalties for paying wages below the minimum rate."
        ),
        "citation": "Minimum Wages Act, 1948 §§ 3-5",
        "cross_references": ["Payment of Wages Act, 1936", "Equal Remuneration Act, 1976"],
        "page_start": 3,
        "page_end": 6,
        "hierarchy_level": 1,
        "chunk_hash": "lab003s7t8u9",
    },
    {
        "chunk_id": "labour-004",
        "document_id": "doc-pf-act-1952",
        "parent_document_id": "doc-pf-act-1952",
        "document_title": "Employees' Provident Funds and Miscellaneous Provisions Act, 1952",
        "category": "Acts / Statutes",
        "text": (
            "The Employees' Provident Funds and Miscellaneous Provisions Act, 1952 (EPF Act) "
            "provides for the institution of provident funds, pension funds, and deposit-linked "
            "insurance funds for employees in factories and establishments. The Act applies to "
            "establishments employing twenty or more persons. Both the employer and the employee "
            "contribute twelve per cent of the basic wages and dearness allowance to the EPF. Of "
            "the employer's contribution, 8.33 per cent goes to the Employees' Pension Scheme "
            "(EPS) and the remaining 3.67 per cent to the EPF. The employee's entire contribution "
            "goes to the EPF. The fund is administered by the Employees' Provident Fund "
            "Organisation (EPFO) under the Ministry of Labour."
        ),
        "citation": "EPF & MP Act, 1952 §§ 5-6",
        "cross_references": ["EPF Scheme, 1952", "EPS, 1995"],
        "page_start": 8,
        "page_end": 12,
        "hierarchy_level": 1,
        "chunk_hash": "lab004v0w1x2",
    },
    # ===== Evidence Law (4 chunks) =====
    {
        "chunk_id": "evidence-001",
        "document_id": "doc-iea-1872",
        "parent_document_id": "doc-iea-1872",
        "document_title": "Indian Evidence Act, 1872 — Sections 3 and 56-58 (Facts and Judicial Notice)",
        "category": "Acts / Statutes",
        "text": (
            "The Indian Evidence Act, 1872 defines 'evidence' under Section 3 as including all "
            "statements which the Court permits or requires to be made before it by witnesses in "
            "relation to matters of fact under inquiry (oral evidence), and all documents including "
            "electronic records produced for the inspection of the Court (documentary evidence). "
            "Section 56 provides that no fact of which the Court will take judicial notice need be "
            "proved. Section 57 lists facts of which Courts must take judicial notice, including "
            "all laws in force in India, proceedings of Parliament and State Legislatures, and "
            "seals of all Courts. Section 58 permits admission of facts as not requiring proof."
        ),
        "citation": "Indian Evidence Act, 1872 §§ 3, 56-58",
        "cross_references": ["IEA § 101 (Burden of Proof)", "IEA § 65B (Electronic Records)"],
        "page_start": 1,
        "page_end": 5,
        "hierarchy_level": 1,
        "chunk_hash": "evi001y3z4a5",
    },
    {
        "chunk_id": "evidence-002",
        "document_id": "doc-iea-1872",
        "parent_document_id": "doc-iea-1872",
        "document_title": "Indian Evidence Act, 1872 — Section 65B (Admissibility of Electronic Records)",
        "category": "Acts / Statutes",
        "text": (
            "Section 65B of the Indian Evidence Act provides for the admissibility of electronic "
            "records as evidence. Any information contained in an electronic record which is "
            "printed on paper, stored, recorded, or copied in optical or magnetic media produced "
            "by a computer shall be deemed to be a document and shall be admissible as evidence "
            "without further proof, provided the conditions set out in subsection (2) are "
            "satisfied. The Supreme Court in Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal "
            "(2020) held that a Section 65B(4) certificate is mandatory for admissibility of "
            "electronic evidence and oral evidence in lieu of such certificate is not admissible."
        ),
        "citation": "Indian Evidence Act, 1872 § 65B",
        "cross_references": ["IEA § 65A", "IT Act, 2000 § 2(1)(t)"],
        "page_start": 48,
        "page_end": 51,
        "hierarchy_level": 1,
        "chunk_hash": "evi002b6c7d8",
    },
    {
        "chunk_id": "evidence-003",
        "document_id": "doc-iea-1872",
        "parent_document_id": "doc-iea-1872",
        "document_title": "Indian Evidence Act, 1872 — Sections 101-104 (Burden of Proof)",
        "category": "Acts / Statutes",
        "text": (
            "Section 101 of the Indian Evidence Act provides that whoever desires any Court to "
            "give judgment as to any legal right or liability dependent on the existence of facts "
            "which he asserts must prove that those facts exist. The burden of proof lies on the "
            "party who would fail if no evidence were given on either side. Section 102 states "
            "that the burden of proof in a suit or proceeding lies on that person who would fail "
            "if no evidence at all were given on either side. Section 103 deals with the burden "
            "of proof as to a particular fact, and Section 104 provides that the burden of proving "
            "any fact necessary to be proved to enable any person to give evidence of any other "
            "fact is on the person who wishes to give such evidence."
        ),
        "citation": "Indian Evidence Act, 1872 §§ 101-104",
        "cross_references": ["IEA § 105 (Burden on Accused)", "IEA § 106 (Special Knowledge)"],
        "page_start": 72,
        "page_end": 75,
        "hierarchy_level": 1,
        "chunk_hash": "evi003e9f0g1",
    },
    {
        "chunk_id": "evidence-004",
        "document_id": "doc-iea-1872",
        "parent_document_id": "doc-iea-1872",
        "document_title": "Indian Evidence Act, 1872 — Section 27 (Discovery of Facts)",
        "category": "Acts / Statutes",
        "text": (
            "Section 27 of the Indian Evidence Act, 1872 provides an important exception to "
            "Section 25 and Section 26 which otherwise render confessions to police officers and "
            "confessions while in police custody inadmissible. Under Section 27, when any fact is "
            "deposed to as discovered in consequence of information received from a person accused "
            "of any offence while in police custody, so much of such information, whether it "
            "amounts to a confession or not, as relates distinctly to the fact thereby discovered "
            "may be proved. This section is frequently invoked in criminal trials to admit "
            "recovery evidence and discovery statements made by the accused."
        ),
        "citation": "Indian Evidence Act, 1872 § 27",
        "cross_references": ["IEA § 25", "IEA § 26", "CrPC § 162"],
        "page_start": 18,
        "page_end": 20,
        "hierarchy_level": 1,
        "chunk_hash": "evi004h2i3j4",
    },
    # ===== RTI (3 chunks) =====
    {
        "chunk_id": "rti-001",
        "document_id": "doc-rti-act-2005",
        "parent_document_id": "doc-rti-act-2005",
        "document_title": "Right to Information Act, 2005 — Section 3",
        "category": "Acts / Statutes",
        "text": (
            "Section 3 of the Right to Information Act, 2005 provides that all citizens shall "
            "have the right to information subject to the provisions of this Act. 'Information' "
            "under Section 2(f) means any material in any form including records, documents, "
            "memos, e-mails, opinions, advices, press releases, circulars, orders, logbooks, "
            "contracts, reports, papers, samples, models, data material held in any electronic "
            "form, and information relating to any private body which can be accessed by a public "
            "authority under any other law for the time being in force. The Act requires every "
            "public authority to designate a Central Public Information Officer (CPIO) and "
            "maintain records that facilitate the right to information."
        ),
        "citation": "RTI Act, 2005 § 3",
        "cross_references": ["RTI Act, 2005 § 2(f)", "RTI Act, 2005 § 6"],
        "page_start": 3,
        "page_end": 4,
        "hierarchy_level": 1,
        "chunk_hash": "rti001k5l6m7",
    },
    {
        "chunk_id": "rti-002",
        "document_id": "doc-rti-act-2005",
        "parent_document_id": "doc-rti-act-2005",
        "document_title": "Right to Information Act, 2005 — Section 8 (Exemptions)",
        "category": "Acts / Statutes",
        "text": (
            "Section 8 of the RTI Act, 2005 specifies the exemptions from disclosure of "
            "information. A public authority is not obligated to disclose information that would "
            "prejudicially affect the sovereignty and integrity of India, the security or strategic "
            "interests of the State, India's relations with foreign States, information received "
            "in confidence from a foreign Government, information that would endanger the life or "
            "physical safety of any person, information that would impede the process of "
            "investigation or prosecution, Cabinet papers including records of deliberations of "
            "the Council of Ministers, and personal information disclosure of which has no "
            "relationship to any public activity or interest."
        ),
        "citation": "RTI Act, 2005 § 8",
        "cross_references": ["RTI Act, 2005 § 9", "RTI Act, 2005 § 24"],
        "page_start": 8,
        "page_end": 11,
        "hierarchy_level": 1,
        "chunk_hash": "rti002n8o9p0",
    },
    {
        "chunk_id": "rti-003",
        "document_id": "doc-rti-act-2005",
        "parent_document_id": "doc-rti-act-2005",
        "document_title": "Right to Information Act, 2005 — Section 6 (Request Procedure)",
        "category": "Acts / Statutes",
        "text": (
            "Section 6 of the RTI Act, 2005 provides that a person who desires to obtain any "
            "information under this Act shall make a request in writing or through electronic "
            "means in English, Hindi, or the official language of the area, to the Central Public "
            "Information Officer or State Public Information Officer, accompanied by the prescribed "
            "fee. The applicant is not required to give any reason for requesting the information "
            "or any other personal details except those necessary for contacting the applicant. "
            "The CPIO shall provide the information within thirty days of receipt of the request, "
            "or within forty-eight hours if the information concerns the life or liberty of a "
            "person. An appeal against refusal lies to the First Appellate Authority within thirty "
            "days, and a second appeal to the Information Commission within ninety days."
        ),
        "citation": "RTI Act, 2005 § 6",
        "cross_references": ["RTI Act, 2005 § 7", "RTI Act, 2005 § 19"],
        "page_start": 5,
        "page_end": 7,
        "hierarchy_level": 1,
        "chunk_hash": "rti003q1r2s3",
    },
    # ===== Additional Coverage Chunks (4 chunks) =====
    {
        "chunk_id": "const-006",
        "document_id": "doc-constitution-india",
        "parent_document_id": "doc-constitution-india",
        "document_title": "Constitution of India — Article 12 (Definition of State)",
        "category": "Acts / Statutes",
        "text": (
            "Article 12 of the Constitution of India defines the term 'State' for the purpose of "
            "Part III (Fundamental Rights). The 'State' includes the Government and Parliament of "
            "India, the Government and Legislature of each of the States, all local authorities, "
            "and other authorities within the territory of India or under the control of the "
            "Government of India. The Supreme Court in Ajay Hasia v. Khalid Mujib (1981) laid "
            "down tests including financial control, functional control, and deep and pervasive "
            "State control to determine whether a body falls within the definition of 'other "
            "authorities' and is therefore bound by fundamental rights obligations."
        ),
        "citation": "Constitution of India, Art. 12",
        "cross_references": ["Constitution of India, Art. 13", "Constitution of India, Art. 226"],
        "page_start": 7,
        "page_end": 8,
        "hierarchy_level": 0,
        "chunk_hash": "const006t4u5v6",
    },
    {
        "chunk_id": "gst-006",
        "document_id": "doc-cgst-act-2017",
        "parent_document_id": "doc-cgst-act-2017",
        "document_title": "Central Goods and Services Tax Act, 2017 — Section 17 (Blocked Credits)",
        "category": "Acts / Statutes",
        "text": (
            "Section 17(5) of the CGST Act enumerates categories of input tax credit that are "
            "blocked and cannot be availed by a registered person. These include ITC on motor "
            "vehicles and conveyances (except for specified purposes), supply of food and beverages "
            "and outdoor catering, beauty treatment, health services, cosmetic and plastic surgery, "
            "membership of a club or health and fitness centre, life insurance and health insurance "
            "(except where the Government mandates as an employer), travel benefits for employees "
            "on vacation, works contract services for construction of immovable property, and goods "
            "or services used for personal consumption. Understanding blocked credits is essential "
            "for proper GST compliance and accurate input tax credit computation."
        ),
        "citation": "CGST Act, 2017 § 17(5)",
        "cross_references": ["CGST Act, 2017 § 16", "CGST Act, 2017 § 18"],
        "page_start": 36,
        "page_end": 39,
        "hierarchy_level": 1,
        "chunk_hash": "gst006w7x8y9",
    },
    {
        "chunk_id": "contract-005",
        "document_id": "doc-sra-1963",
        "parent_document_id": "doc-sra-1963",
        "document_title": "Specific Relief Act, 1963 — Section 10 (Specific Performance)",
        "category": "Acts / Statutes",
        "text": (
            "Section 10 of the Specific Relief Act, 1963 provides that specific performance of a "
            "contract shall be enforced by the court subject to the provisions contained in "
            "Sections 11(2), 14, and 16. The 2018 amendment to the Act made specific performance "
            "the rule rather than the exception, removing the earlier judicial discretion to refuse "
            "it. Specific performance may be granted in respect of contracts relating to immovable "
            "property, or where the act agreed to be done is such that pecuniary compensation for "
            "its non-performance would not afford adequate relief, or where it is not reasonably "
            "practicable to ascertain the actual damage caused by non-performance."
        ),
        "citation": "Specific Relief Act, 1963 § 10",
        "cross_references": ["Specific Relief Act, 1963 § 14", "Indian Contract Act, 1872 § 73"],
        "page_start": 10,
        "page_end": 12,
        "hierarchy_level": 1,
        "chunk_hash": "sra001z0a1b2",
    },
    {
        "chunk_id": "crim-005",
        "document_id": "doc-ipc-1860",
        "parent_document_id": "doc-ipc-1860",
        "document_title": "Indian Penal Code, 1860 — Section 420 (Cheating and Dishonestly Inducing Delivery)",
        "category": "Acts / Statutes",
        "text": (
            "Section 420 of the Indian Penal Code provides that whoever cheats and thereby "
            "dishonestly induces the person deceived to deliver any property to any person, or to "
            "make, alter, or destroy the whole or any part of a valuable security, or anything "
            "which is signed or sealed and which is capable of being converted into a valuable "
            "security, shall be punished with imprisonment of either description for a term which "
            "may extend to seven years and shall also be liable to fine. Cheating is defined under "
            "Section 415 as deceiving any person and thereby dishonestly inducing that person to "
            "do or omit to do anything which he would not have done or omitted if not so deceived."
        ),
        "citation": "Indian Penal Code, 1860 § 420",
        "cross_references": ["IPC § 415", "IPC § 417", "IPC § 468"],
        "page_start": 198,
        "page_end": 200,
        "hierarchy_level": 1,
        "chunk_hash": "crim005c3d4e5",
    },
]

_VECTOR_DIM = 1024


def _generate_deterministic_vector(seed_str: str) -> list[float]:
    """Generate a deterministic 1024-dim pseudo-vector from a string seed."""
    import hashlib as _hl
    # Use repeated hashing to fill the vector
    vector: list[float] = []
    block = seed_str.encode("utf-8")
    while len(vector) < _VECTOR_DIM:
        block = _hl.sha512(block).digest()
        for byte in block:
            if len(vector) >= _VECTOR_DIM:
                break
            vector.append((byte - 128) / 128.0)  # normalize to [-1, 1]
    return vector


def _seed_mock_environment(config: HybridConfig):
    """
    Populate mock ES and Qdrant clients with the in-memory corpus.
    Returns (mock_es_client, mock_qdrant_client) pre-loaded with data.
    No filesystem access occurs.
    """
    from es_indexer.client import MockESClient
    from es_indexer.schema import INDEX_MAPPING, INDEX_SETTINGS
    from qdrant_indexer.client import MockQdrantClient
    from qdrant_indexer.models import QdrantPoint

    # --- Elasticsearch ---
    es_client = MockESClient()
    es_client.create_index(config.es_index_name, INDEX_SETTINGS, INDEX_MAPPING)

    es_docs = []
    for chunk in _MOCK_LEGAL_CHUNKS:
        es_docs.append({
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "category": chunk["category"],
            "text": chunk["text"],
            "citation": chunk["citation"],
            "cross_references": chunk.get("cross_references", []),
            "page_start": chunk.get("page_start", 0),
            "page_end": chunk.get("page_end", 0),
            "hierarchy_level": chunk.get("hierarchy_level", 0),
        })
    es_client.bulk_index(config.es_index_name, es_docs)
    logger.info(f"Mock ES seeded with {len(es_docs)} in-memory chunks.")

    # --- Qdrant ---
    qd_client = MockQdrantClient()
    qd_client.create_collection(
        collection_name=config.qdrant_collection_name,
        vector_size=_VECTOR_DIM,
        distance="Cosine",
    )
    # Create payload indices matching production setup
    for field in ["category", "parent_document_id", "citation"]:
        qd_client.create_payload_index(
            config.qdrant_collection_name, field, "keyword"
        )

    points = []
    for chunk in _MOCK_LEGAL_CHUNKS:
        point_id = str(uuid.UUID(hashlib.md5(chunk["chunk_id"].encode("utf-8")).hexdigest()))
        vector = _generate_deterministic_vector(chunk["chunk_id"])
        payload = {
            "chunk_id": chunk["chunk_id"],
            "chunk_hash": chunk.get("chunk_hash", ""),
            "parent_document_id": chunk["document_id"],
            "category": chunk["category"],
            "document_title": chunk.get("document_title", ""),
            "citation": chunk["citation"],
            "page_start": chunk.get("page_start", 0),
            "page_end": chunk.get("page_end", 0),
            "hierarchy_level": chunk.get("hierarchy_level", 0),
            "cross_references": chunk.get("cross_references", []),
            "embedding_model": "mock-deterministic",
        }
        points.append(QdrantPoint(id=point_id, vector=vector, payload=payload))

    qd_client.upsert(config.qdrant_collection_name, points)
    logger.info(f"Mock Qdrant seeded with {len(points)} in-memory vectors.")

    return es_client, qd_client


def run_pipeline(config: HybridConfig | None = None, query: str = "Taxation rules for independent contractors under IRS Section 162") -> dict:
    if config is None:
        config = HybridConfig()
        
    _setup_logging(config)
    
    logger.info("=" * 60)
    logger.info(f"Hybrid Retrieval Pipeline \u2014 Starting")
    logger.info(f"Query: '{query}'")
    logger.info("=" * 60)
    
    # 0. Setup Mock or Production Environment
    if config.use_mock:
        logger.info("Initializing Mock Environment (in-memory, no filesystem)...")
        mock_es, mock_qd = _seed_mock_environment(config)
        es_retriever = ElasticsearchRetriever(config, client=mock_es)
        qd_retriever = QdrantRetriever(config, client=mock_qd)
    else:
        # Production path — uses real indexer pipelines and clients
        from es_indexer.main import run_pipeline as run_es
        from es_indexer.config import ESIndexerConfig
        from qdrant_indexer.main import run_pipeline as run_qd
        from qdrant_indexer.config import QdrantConfig

        logger.info("Initializing Indexers (Production Environment Setup)...")
        logging.getLogger("es_indexer").setLevel(logging.WARNING)
        logging.getLogger("qdrant_indexer").setLevel(logging.WARNING)
        run_es(ESIndexerConfig(use_mock=True))
        run_qd(QdrantConfig(use_mock=True))
        es_retriever = ElasticsearchRetriever(config)
        qd_retriever = QdrantRetriever(config)

    embedder = EmbedderWrapper(config)
    
    total_start = time.monotonic()
    
    # 1. Metadata Filters Extraction
    filters = extract_filters(query)
    if filters:
        logger.info(f"Extracted metadata pre-filters: {filters}")
        
    # 2. Embedding Generation
    query_vector, emb_lat = embedder.embed_query(query)
    logger.info(f"Generated query embedding in {emb_lat:.4f}s")
    
    # 3. Parallel Retrieval (Simulated sequentially here)
    logger.info("Executing Elasticsearch (BM25)...")
    es_hits, es_lat = es_retriever.retrieve(query, filters)
    
    logger.info("Executing Qdrant (Dense Vector)...")
    qd_hits, qd_lat = qd_retriever.retrieve(query_vector, filters)
    
    logger.info(f"Candidate set: {len(es_hits)} lexical hits, {len(qd_hits)} semantic hits")
    
    # 4. Fusion
    logger.info(f"Applying Reciprocal Rank Fusion (k={config.rrf_k})...")
    fused_dict, fuse_lat = reciprocal_rank_fusion(es_hits, qd_hits, config.rrf_k)
    
    # 5. Ranking & Deduplication (Implicit in dictionary keys)
    final_results = rank_and_truncate(fused_dict, config.top_k)
    
    # 6. Verification
    validate_citations(final_results)
    val_res = verify_output(final_results, config.top_k)
    if val_res["is_valid"]:
        logger.info("Hybrid Pipeline Validation PASSED.")
    else:
        logger.error(f"Validation FAILED: {val_res['issues']}")
        
    total_lat = time.monotonic() - total_start
    
    # 7. Trace and Response
    trace = RetrievalTrace(
        query=query,
        embedding_latency=emb_lat,
        es_latency=es_lat,
        qdrant_latency=qd_lat,
        fusion_latency=fuse_lat,
        total_latency=total_lat,
        es_candidate_count=len(es_hits),
        qdrant_candidate_count=len(qd_hits),
        rrf_k=config.rrf_k,
        results=final_results
    )
    
    response = build_response(trace)
    generate_reports(config.report_dir, response, val_res)
    
    logger.info("=" * 60)
    logger.info(f"Hybrid Retrieval complete in {total_lat:.4f}s")
    logger.info(f"Retrieved Top-{len(final_results)} chunks.")
    logger.info("=" * 60)
    
    return response

def _setup_logging(config: HybridConfig) -> None:
    config.log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger("hybrid_retriever")
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | HYBRID | %(message)s"))
    root_logger.addHandler(console_handler)

if __name__ == "__main__":
    run_pipeline()
