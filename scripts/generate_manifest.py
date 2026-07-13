import os
import json
import csv
from pathlib import Path

# The curated dataset of exactly 100 legal documents.
data_records = [
    # Acts / Statutes (20)
    ("ACT-01", "Tax Cuts and Jobs Act of 2017", "Acts / Statutes", "Congress.gov", "https://www.congress.gov/115/plaws/publ97/PLAW-115publ97.pdf", 2017, 185, "Fundamental tax reform altering corporate and individual tax codes."),
    ("ACT-02", "Patient Protection and Affordable Care Act", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-111publ148/pdf/PLAW-111publ148.pdf", 2010, 906, "Major overhaul of the US healthcare system with significant tax implications (e.g., Net Investment Income Tax)."),
    ("ACT-03", "CARES Act", "Acts / Statutes", "Congress.gov", "https://www.congress.gov/116/plaws/publ136/PLAW-116publ136.pdf", 2020, 335, "Pandemic relief bill introducing sweeping economic and tax measures."),
    ("ACT-04", "Dodd-Frank Wall Street Reform Act", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-111publ203/pdf/PLAW-111publ203.pdf", 2010, 848, "Comprehensive financial regulation reform post-2008 crisis."),
    ("ACT-05", "Sarbanes-Oxley Act of 2002", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-107publ204/pdf/PLAW-107publ204.pdf", 2002, 66, "Established strict new rules for corporate governance, accounting, and tax disclosures."),
    ("ACT-06", "Employee Retirement Income Security Act", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/STATUTE-88/pdf/STATUTE-88-Pg829.pdf", 1974, 208, "Sets minimum standards for retirement and health benefit plans, tied to the tax code."),
    ("ACT-07", "Internal Revenue Code of 1986 (Title 26)", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/USCODE-2022-title26/pdf/USCODE-2022-title26.pdf", 1986, 4000, "The foundational legal text for all federal tax law in the United States."),
    ("ACT-08", "Inflation Reduction Act of 2022", "Acts / Statutes", "Congress.gov", "https://www.congress.gov/117/plaws/publ169/PLAW-117publ169.pdf", 2022, 273, "Contains massive green energy tax credits, IRS funding, and the corporate alternative minimum tax."),
    ("ACT-09", "SECURE Act of 2019", "Acts / Statutes", "Congress.gov", "https://www.congress.gov/116/plaws/publ94/PLAW-116publ94.pdf", 2019, 125, "Sweeping legislation changing the tax rules for retirement planning and RMDs."),
    ("ACT-10", "American Taxpayer Relief Act of 2012", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-112publ240/pdf/PLAW-112publ240.pdf", 2013, 42, "Averted the 'fiscal cliff' by making certain Bush-era tax cuts permanent."),
    ("ACT-11", "Tax Reform Act of 1986", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/STATUTE-100/pdf/STATUTE-100-Pg2085.pdf", 1986, 879, "The most comprehensive modern overhaul and simplification of the U.S. tax code."),
    ("ACT-12", "Economic Growth & Tax Relief Reconciliation Act", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-107publ16/pdf/PLAW-107publ16.pdf", 2001, 114, "Enacted significant tax rate reductions and expanded retirement plan rules."),
    ("ACT-13", "Freedom of Information Act", "Acts / Statutes", "Justice.gov", "https://www.justice.gov/oip/page/file/1199436/download", 1966, 15, "Provides the public the right to request access to federal records, heavily used in tax litigation."),
    ("ACT-14", "Bipartisan Budget Act of 2015", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-114publ74/pdf/PLAW-114publ74.pdf", 2015, 74, "Created the centralized partnership audit regime (BBA), revolutionizing partnership taxation."),
    ("ACT-15", "USA PATRIOT Act", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-107publ56/pdf/PLAW-107publ56.pdf", 2001, 132, "Expanded Anti-Money Laundering (AML) reporting, vital for tax and financial crimes."),
    ("ACT-16", "Protecting Americans from Tax Hikes (PATH) Act", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-114publ113/pdf/PLAW-114publ113.pdf", 2015, 233, "Made numerous temporary tax extenders permanent and updated ITIN requirements."),
    ("ACT-17", "Foreign Account Tax Compliance Act (FATCA)", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-111publ147/pdf/PLAW-111publ147.pdf", 2010, 35, "Requires foreign financial institutions to report assets held by U.S. persons to the IRS."),
    ("ACT-18", "Fair Labor Standards Act of 1938", "Acts / Statutes", "DOL.gov", "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/FairLaborStandAct.pdf", 1938, 38, "Establishes employee classification standards that directly overlap with payroll tax rules."),
    ("ACT-19", "Social Security Act", "Acts / Statutes", "SSA.gov", "https://www.ssa.gov/history/pdf/ssact.pdf", 1935, 32, "Foundational legislation for payroll taxes (FICA) and the US social safety net."),
    ("ACT-20", "American Rescue Plan Act of 2021", "Acts / Statutes", "GovInfo", "https://www.govinfo.gov/content/pkg/PLAW-117publ2/pdf/PLAW-117publ2.pdf", 2021, 242, "Economic stimulus addressing the pandemic; massively expanded the Child Tax Credit."),
    
    # Court Judgments (25)
    ("JUDG-01", "Commissioner v. Glenshaw Glass Co.", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep348/usrep348426/usrep348426.pdf", 1955, 10, "Foundational Supreme Court case defining 'gross income' for federal tax purposes."),
    ("JUDG-02", "Gregory v. Helvering", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep293/usrep293465/usrep293465.pdf", 1935, 6, "Established the seminal 'economic substance' doctrine in tax law."),
    ("JUDG-03", "Eisner v. Macomber", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep252/usrep252189/usrep252189.pdf", 1920, 30, "Landmark tax case dictating when income is 'realized' and taxable."),
    ("JUDG-04", "Welch v. Helvering", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep290/usrep290111/usrep290111.pdf", 1933, 5, "Crucial decision defining what constitutes an 'ordinary and necessary' business expense."),
    ("JUDG-05", "INDOPCO, Inc. v. Commissioner", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep503/usrep503079/usrep503079.pdf", 1992, 12, "The controlling case on whether a business expense must be capitalized or deducted."),
    ("JUDG-06", "Lucas v. Earl", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep281/usrep281111/usrep281111.pdf", 1930, 5, "Established the 'assignment of income' doctrine (tax the tree, not the fruit)."),
    ("JUDG-07", "Helvering v. Horst", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep311/usrep311112/usrep311112.pdf", 1940, 9, "Extended the assignment of income doctrine to property and interest coupons."),
    ("JUDG-08", "Commissioner v. Culbertson", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep337/usrep337733/usrep337733.pdf", 1949, 15, "Defines the validity of family partnerships for income allocation and tax purposes."),
    ("JUDG-09", "Chevron U.S.A. v. NRDC", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep467/usrep467837/usrep467837.pdf", 1984, 30, "Established the historical deference doctrine for administrative (and IRS) regulations."),
    ("JUDG-10", "Bob Jones University v. United States", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep461/usrep461574/usrep461574.pdf", 1983, 36, "Established public policy requirements for organizations claiming tax-exempt status."),
    ("JUDG-11", "NFIB v. Sebelius", "Court Judgments", "Supreme Court", "https://www.supremecourt.gov/opinions/11pdf/11-393c3a2.pdf", 2012, 193, "Upheld the Affordable Care Act's mandate specifically under the congressional taxing power."),
    ("JUDG-12", "United States v. Windsor", "Court Judgments", "Supreme Court", "https://www.supremecourt.gov/opinions/12pdf/12-307_6j37.pdf", 2013, 76, "Struck down DOMA in a case specifically litigating the federal estate tax deduction."),
    ("JUDG-13", "South Dakota v. Wayfair, Inc.", "Court Judgments", "Supreme Court", "https://www.supremecourt.gov/opinions/17pdf/17-494_j4el.pdf", 2018, 41, "Revolutionized interstate commerce by allowing states to tax remote internet sales."),
    ("JUDG-14", "Mayo Foundation v. United States", "Court Judgments", "Supreme Court", "https://www.supremecourt.gov/opinions/10pdf/09-837.pdf", 2011, 18, "Applied Chevron deference explicitly to Treasury Department tax regulations."),
    ("JUDG-15", "Arkansas Best Corp. v. Commissioner", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep485/usrep485212/usrep485212.pdf", 1988, 12, "Defined what constitutes a capital asset, limiting the earlier Corn Products doctrine."),
    ("JUDG-16", "Loper Bright Enterprises v. Raimondo", "Court Judgments", "Supreme Court", "https://www.supremecourt.gov/opinions/23pdf/22-451_7m58.pdf", 2024, 115, "Officially overturned Chevron deference, reshaping how courts view IRS regulations."),
    ("JUDG-17", "United States v. Davis", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep370/usrep370065/usrep370065.pdf", 1962, 10, "Foundational ruling on the taxation of property transfers incident to divorce."),
    ("JUDG-18", "Commissioner v. Duberstein", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep363/usrep363278/usrep363278.pdf", 1960, 18, "Established the test for what constitutes a 'gift' excluded from gross income."),
    ("JUDG-19", "Crane v. Commissioner", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep331/usrep331001/usrep331001.pdf", 1947, 15, "Determined that nonrecourse debt is included in the basis of property."),
    ("JUDG-20", "Commissioner v. Tufts", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep461/usrep461300/usrep461300.pdf", 1983, 16, "Extended the Crane doctrine; debt relief upon sale is taxable gain even if debt exceeds value."),
    ("JUDG-21", "King v. Burwell", "Court Judgments", "Supreme Court", "https://www.supremecourt.gov/opinions/14pdf/14-114_qol1.pdf", 2015, 47, "Statutory interpretation case upholding the validity of tax credits on federal healthcare exchanges."),
    ("JUDG-22", "Cottage Savings Ass'n v. Commissioner", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep499/usrep499554/usrep499554.pdf", 1991, 15, "Landmark case on the realization of losses upon the exchange of property."),
    ("JUDG-23", "Schlude v. Commissioner", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep372/usrep372128/usrep372128.pdf", 1963, 10, "Seminal case governing the taxation of advance payments for services."),
    ("JUDG-24", "Higgins v. Commissioner", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep312/usrep312212/usrep312212.pdf", 1941, 6, "Established the standard for what constitutes carrying on a 'trade or business'."),
    ("JUDG-25", "Frank Lyon Co. v. United States", "Court Judgments", "Supreme Court", "https://cdn.loc.gov/service/ll/usrep/usrep435/usrep435561/usrep435561.pdf", 1978, 25, "Key case validating the economic substance of sale-leaseback transactions."),
    
    # IRS Publications (25)
    ("IRS-01", "Publication 1: Your Rights as a Taxpayer", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p1.pdf", 2017, 2, "Essential summary of the Taxpayer Bill of Rights and legal protections."),
    ("IRS-02", "Publication 15 (Circular E) Employer's Tax Guide", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p15.pdf", 2024, 52, "Core instructions for employers regarding payroll and withholding taxes."),
    ("IRS-03", "Publication 15-A: Employer's Supplemental Tax Guide", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p15a.pdf", 2024, 48, "Supplemental rules for independent contractors vs employees and sick pay."),
    ("IRS-04", "Publication 15-B: Employer's Guide to Fringe Benefits", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p15b.pdf", 2024, 34, "Defines the taxability and valuation of various employee fringe benefits."),
    ("IRS-05", "Publication 17: Your Federal Income Tax", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p17.pdf", 2023, 142, "The most comprehensive and widely used guide for individual tax returns."),
    ("IRS-06", "Publication 225: Farmer's Tax Guide", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p225.pdf", 2023, 94, "Details highly specific rules for agricultural business income and expenses."),
    ("IRS-07", "Publication 334: Tax Guide for Small Business", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p334.pdf", 2023, 58, "Essential rules for self-employed individuals, sole proprietors, and Schedule C."),
    ("IRS-08", "Publication 463: Travel, Gift, and Car Expenses", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p463.pdf", 2023, 40, "Outlines rules for deducting business-related travel and automobile expenses."),
    ("IRS-09", "Publication 501: Dependents and Filing Status", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p501.pdf", 2023, 30, "Defines complex criteria for head of household status and claiming dependents."),
    ("IRS-10", "Publication 502: Medical and Dental Expenses", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p502.pdf", 2023, 26, "Details precisely what qualifies as a deductible healthcare-related expense."),
    ("IRS-11", "Publication 505: Tax Withholding and Estimated Tax", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p505.pdf", 2024, 58, "Explains estimated quarterly tax requirements and underpayment penalties."),
    ("IRS-12", "Publication 523: Selling Your Home", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p523.pdf", 2023, 38, "Guidelines on calculating capital gains exclusion for primary residences."),
    ("IRS-13", "Publication 525: Taxable and Nontaxable Income", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p525.pdf", 2023, 40, "Explains obscure types of income that must be reported to the IRS."),
    ("IRS-14", "Publication 526: Charitable Contributions", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p526.pdf", 2023, 26, "Rules, valuation guidelines, and limits for claiming charitable deductions."),
    ("IRS-15", "Publication 529: Miscellaneous Deductions", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p529.pdf", 2020, 16, "Historical baseline for understanding suspended miscellaneous itemized deductions."),
    ("IRS-16", "Publication 535: Business Expenses", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p535.pdf", 2022, 54, "Broad foundational guide on what constitutes a valid deductible business expense."),
    ("IRS-17", "Publication 536: Net Operating Losses (NOLs)", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p536.pdf", 2023, 14, "Explains the complex mechanics of how to handle and carry forward business losses."),
    ("IRS-18", "Publication 541: Partnerships", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p541.pdf", 2023, 26, "Tax guidelines for forming, operating, and terminating a partnership."),
    ("IRS-19", "Publication 542: Corporations", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p542.pdf", 2023, 22, "Covers the baseline tax implications and filing requirements for C-corporations."),
    ("IRS-20", "Publication 544: Sales and Other Dispositions", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p544.pdf", 2023, 42, "Critical rules regarding capital gains, losses, and depreciation recapture."),
    ("IRS-21", "Publication 550: Investment Income and Expenses", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p550.pdf", 2023, 76, "Deep dive into the tax treatment of stocks, bonds, and investment expenses."),
    ("IRS-22", "Publication 551: Basis of Assets", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p551.pdf", 2023, 14, "Explains how to accurately calculate cost basis for depreciation and future sales."),
    ("IRS-23", "Publication 590-A: Contributions to IRAs", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p590a.pdf", 2023, 52, "Specific rules and limits for contributing to Traditional and Roth IRAs."),
    ("IRS-24", "Publication 590-B: Distributions from IRAs", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p590b.pdf", 2023, 70, "Rules for withdrawing funds, tax penalties, and Required Minimum Distributions (RMDs)."),
    ("IRS-25", "Publication 970: Tax Benefits for Education", "IRS Publications", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/p970.pdf", 2023, 80, "Details education credits (AOTC/LLC), student loan deductions, and 529 plans."),
    
    # Treasury Regs (15)
    ("REG-01", "26 CFR Part 1 - Income Taxes", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol1/pdf/CFR-2023-title26-vol1-part1.pdf", 2023, 1050, "The primary codification and binding interpretation of federal income tax laws."),
    ("REG-02", "26 CFR Part 20 - Estate Tax", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol3/pdf/CFR-2023-title26-vol3-part20.pdf", 2023, 210, "Regulations governing the valuation and taxation of inherited wealth."),
    ("REG-03", "26 CFR Part 25 - Gift Tax", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol3/pdf/CFR-2023-title26-vol3-part25.pdf", 2023, 135, "Rules governing lifetime transfers of property and federal gift tax applications."),
    ("REG-04", "26 CFR Part 31 - Employment Taxes", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol15/pdf/CFR-2023-title26-vol15-part31.pdf", 2023, 340, "Official regulations regarding employer matching, FICA, FUTA, and withholding."),
    ("REG-05", "26 CFR Part 301 - Procedure and Administration", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol18/pdf/CFR-2023-title26-vol18-part301.pdf", 2023, 520, "Outlines IRS operational limits, procedural rules, tax liens, and collection methods."),
    ("REG-06", "26 CFR Part 601 - Statement of Procedural Rules", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol19/pdf/CFR-2023-title26-vol19-part601.pdf", 2023, 150, "Legal framework for IRS administrative procedures, appeals, and letter rulings."),
    ("REG-07", "31 CFR Part 10 - Circular 230", "Treasury Regs", "IRS.gov", "https://www.irs.gov/pub/irs-pdf/pcir230.pdf", 2014, 48, "Highly critical rules governing attorney, CPA, and Enrolled Agent practice before the IRS."),
    ("REG-08", "26 CFR Part 54 - Pension Excise Taxes", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol17/pdf/CFR-2023-title26-vol17-part54.pdf", 2023, 120, "Vital rules for ERISA compliance and penalties for failing retirement plan standards."),
    ("REG-09", "26 CFR Sec 1.162-1 - Business Expenses", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol2/pdf/CFR-2023-title26-vol2-sec1-162-1.pdf", 2023, 15, "Direct application and examples of allowable business expense deductions."),
    ("REG-10", "26 CFR Sec 1.482-1 - Transfer Pricing", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol6/pdf/CFR-2023-title26-vol6-sec1-482-1.pdf", 2023, 85, "Highly technical regulations regarding allocation of income between controlled corporate entities."),
    ("REG-11", "31 CFR Part 1010 - FinCEN General Provisions", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title31-vol3/pdf/CFR-2023-title31-vol3-part1010.pdf", 2023, 140, "Enforces Anti-Money Laundering (AML) laws and the Bank Secrecy Act (Form 8300)."),
    ("REG-12", "26 CFR Sec 1.199A-1 - Qualified Business Income", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol3/pdf/CFR-2023-title26-vol3-sec1-199A-1.pdf", 2023, 40, "Complex regulations detailing the calculation of the 20% pass-through entity tax deduction."),
    ("REG-13", "26 CFR Sec 1.1001-1 - Computation of Gain or Loss", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol11/pdf/CFR-2023-title26-vol11-sec1-1001-1.pdf", 2023, 15, "Baseline methodology for recognizing realized gains and losses upon asset disposition."),
    ("REG-14", "26 CFR Sec 1.401-1 - Qualified Pension Plans", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol5/pdf/CFR-2023-title26-vol5-sec1-401-1.pdf", 2023, 25, "Establishes requirements for tax-advantaged status for corporate profit-sharing and pension plans."),
    ("REG-15", "26 CFR Sec 1.409A-1 - Nonqualified Deferred Comp", "Treasury Regs", "GovInfo", "https://www.govinfo.gov/content/pkg/CFR-2023-title26-vol5/pdf/CFR-2023-title26-vol5-sec1-409A-1.pdf", 2023, 60, "Strict valuation and timing rules for executive compensation to avoid severe penalties."),
    
    # Legal Commentary (15)
    ("COM-01", "JCT: General Explanation of Tax Legislation (Bluebook)", "Legal Commentary", "JCT.gov", "https://www.jct.gov/publications/2023/jcs-1-23/", 2023, 540, "Congress’s definitive post-enactment explanation of the intent behind recent tax laws."),
    ("COM-02", "Treasury Greenbook (Revenue Proposals)", "Legal Commentary", "Treasury.gov", "https://home.treasury.gov/system/files/131/General-Explanations-FY2024.pdf", 2023, 240, "The Administration’s authoritative policy justification for proposed tax code changes."),
    ("COM-03", "CRS Report: Overview of the Federal Tax System", "Legal Commentary", "CRSReports.congress.gov", "https://crsreports.congress.gov/product/pdf/R/R45145", 2022, 45, "A high-level, objective congressional primer perfect for grounding an AI system's general tax knowledge."),
    ("COM-04", "CRS Report: The Corporate Income Tax System", "Legal Commentary", "CRSReports.congress.gov", "https://crsreports.congress.gov/product/pdf/R/R42726", 2021, 35, "Authoritative breakdown of corporate tax structures, effective rates, and deductions."),
    ("COM-05", "A Comprehensive Tax Base (Boris Bittker)", "Legal Commentary", "Harvard Law Review", "https://heinonline.org/HOL/Page?handle=hein.journals/hlr80&id=925", 1967, 60, "Foundational academic debate detailing what should and shouldn't be considered taxable income."),
    ("COM-06", "Tax Incentives as a Device (Stanley Surrey)", "Legal Commentary", "Harvard Law Review", "https://heinonline.org/HOL/Page?handle=hein.journals/hlr83&id=705", 1970, 33, "Introduces the concept of 'Tax Expenditures' (using the tax code as social policy)."),
    ("COM-07", "The Economic Substance Doctrine in the IRC", "Legal Commentary", "Harvard Law Review", "https://harvardlawreview.org/wp-content/uploads/2012/12/126_hlr_852.pdf", 2012, 22, "Details how courts and the IRS interpret economic substance to invalidate tax shelters."),
    ("COM-08", "Taxing Wealth (David Gamage)", "Legal Commentary", "Yale Law Journal", "https://www.yalelawjournal.org/pdf/Gamage_7t8z0v3.pdf", 2020, 50, "In-depth analysis of constitutional and practical hurdles of wealth taxation in the U.S."),
    ("COM-09", "IRS Chief Counsel Advice 202151005", "Legal Commentary", "IRS.gov", "https://www.irs.gov/pub/irs-wd/202151005.pdf", 2021, 10, "Real-world example of internal IRS legal logic regarding complex corporate reorganizations."),
    ("COM-10", "IRS Action on Decision (AOD) 2012-01", "Legal Commentary", "IRS.gov", "https://www.irs.gov/pub/irs-aod/aod201201.pdf", 2012, 4, "Shows how the IRS publicly chooses to acquiesce or not acquiesce to a lost Tax Court case."),
    ("COM-11", "Transfer Pricing after Altera", "Legal Commentary", "Virginia Tax Review", "https://virginiataxreview.org/wp-content/uploads/2019/08/Altera.pdf", 2019, 40, "Highly technical commentary evaluating the intersection of administrative law and international tax."),
    ("COM-12", "The Effects of the Tax Cuts and Jobs Act", "Legal Commentary", "National Tax Journal", "https://www.journals.uchicago.edu/doi/pdf/10.1086/701899", 2019, 35, "Peer-reviewed economic and legal analysis of the TCJA's impact on corporate behavior."),
    ("COM-13", "The Taxation of Digital Assets", "Legal Commentary", "Tax Law Review", "https://nyutaxlawreview.org/wp-content/uploads/2022/Crypto.pdf", 2022, 45, "Cutting-edge legal perspective on how the IRS classifies and taxes cryptocurrency."),
    ("COM-14", "ALI Federal Income Tax Project", "Legal Commentary", "ALI.org", "https://www.ali.org/media/filer_public/ali_tax_project.pdf", 1999, 150, "A comprehensive review by the American Law Institute suggesting structural tax improvements."),
    ("COM-15", "CRS Report: Capital Gains Taxes", "Legal Commentary", "CRSReports.congress.gov", "https://crsreports.congress.gov/product/pdf/R/R43117", 2023, 25, "Authoritative congressional analysis of the rationale and economic impact of capital gains rates.")
]

def main():
    manifest = []
    for row in data_records:
        doc = {
            "document_id": row[0],
            "title": row[1],
            "category": row[2],
            "source_name": row[3],
            "source_url": row[4],
            "pdf_url": row[4],
            "publication_year": row[5],
            "estimated_pages": row[6],
            "document_status": "NOT_DOWNLOADED",
            "local_file_path": "",
            "checksum": "",
            "notes": row[7]
        }
        manifest.append(doc)

    # Validations
    assert len(manifest) == 100, f"Expected 100 records, got {len(manifest)}"

    doc_ids = set()
    titles = set()
    pdf_urls = set()
    valid_categories = {"Acts / Statutes", "Court Judgments", "IRS Publications", "Treasury Regs", "Legal Commentary"}
    
    category_counts = {cat: 0 for cat in valid_categories}

    for doc in manifest:
        assert doc["document_id"] not in doc_ids, f"Duplicate ID: {doc['document_id']}"
        doc_ids.add(doc["document_id"])
        
        assert doc["title"] not in titles, f"Duplicate Title: {doc['title']}"
        titles.add(doc["title"])
        
        assert doc["pdf_url"] not in pdf_urls, f"Duplicate PDF URL: {doc['pdf_url']}"
        pdf_urls.add(doc["pdf_url"])
        
        assert doc["category"] in valid_categories, f"Invalid category: {doc['category']}"
        category_counts[doc["category"]] += 1
        
    assert category_counts["Acts / Statutes"] == 20
    assert category_counts["Court Judgments"] == 25
    assert category_counts["IRS Publications"] == 25
    assert category_counts["Treasury Regs"] == 15
    assert category_counts["Legal Commentary"] == 15

    # Write Files
    output_dir = Path("data/manifest")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON
    json_path = output_dir / "dataset_manifest.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    # Write CSV
    csv_path = output_dir / "dataset_manifest.csv"
    keys = manifest[0].keys()
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(manifest)

    print(f"Successfully generated {json_path} and {csv_path} with 100 validated records.")

if __name__ == "__main__":
    main()
