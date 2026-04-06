# Requriment Documents for Skill
The requirements of this project is to build a reusable claude code skills for Indian Equity and Mutual Fund markets to suggest best investment options, critical stock analysis, fund analysis and future projections based on the Govt of India and State Goverments of India's policy initiatives and directives.
I should be able to copy over this claude skill files to any other project or machine and use it.
All this skill related files should be created in the current directory only.
This skill should do a critical analysis rather than a pleasing analysis of stock. Provide hard facts as it is and the main part of the enhancement is to include the Corporate Governance analysis ( include organization / board structure, corporate governance, tax dispute / penalty issues, related party transaction issues and also any dishonest practices. 
**IMPORTANT** ** This skill should never speculate or depend on unreliable sources or social media commentary on stock price**


### 1. Comprehensive Coverage
- All aspects of Indian market investing covered
- From beginner to intermediate level guidance
- Multiple time horizons (5-20 years)
- All major asset classes (equity, debt, gold)

### 2. Educational Approach
- Explains concepts in simple language
- Teaches "why" behind recommendations
- Includes glossaries and references
- Builds investor knowledge progressively

### 3. Risk-First Philosophy
- Every recommendation includes risk assessment
- Clear disclaimers throughout
- Emphasizes capital preservation
- Promotes disciplined, long-term investing

### 4. Data-Driven Analysis
- References specific metrics and ratios
- Uses publicly available free data sources
- Quantifies impacts where possible
- Provides valuation frameworks

### 5. Practical & Actionable
- Ready-to-use templates
- Step-by-step implementation guides
- Clear next steps
- Real-world scenarios covered

### 6. Fully Portable
- All files in one directory
- Easy installation script
- No external dependencies
- Can be copied to any machine

### 7. Modular Design
- Main skill + 4 specialized sub-skills
- Each sub-skill can be used independently
- Easy to update specific components
- Clear separation of concerns




#### 1. Main Skill- **[indian-markets-advisor.claude-skill.yaml](indian-markets-advisor.claude-skill.yaml)** (1.8KB) - Main skill definition and metadata - Triggers and examples
- **[indian-markets-advisor.md](indian-markets-advisor.md)** (18KB) - Comprehensive investment advisory framework - Analysis methodologies for stocks, funds, policies, portfolios - Output formats and best practices - Risk management guidelines
#### 2. Stock Analysis Sub-Skill- **[stock-analyzer.claude-skill.yaml](stock-analyzer.claude-skill.yaml)** (1KB) - Skill definition for deep stock analysis
- **[stock-analyzer.md](stock-analyzer.md)** (13KB) - Detailed fundamental analysis framework - Financial metrics evaluation (ROE, ROCE, P/E, Debt/Equity) - Valuation methodologies (DCF, PE-based, Graham Number) - Technical analysis layer - Peer comparison templates - Investment recommendation format
#### 3. Mutual Fund Advisor Sub-Skill- **[mutual-fund-advisor.claude-skill.yaml](mutual-fund-advisor.claude-skill.yaml)** (1.2KB) - Skill definition for mutual fund analysis
- **[mutual-fund-advisor.md](mutual-fund-advisor.md)** (19KB) - Fund category selection guide - Performance and risk metrics analysis - Cost analysis (expense ratios) - Portfolio construction strategies - SIP planning and implementation - Fund comparison frameworks
#### 4. Policy Impact Analyzer Sub-Skill- **[policy-impact-analyzer.claude-skill.yaml](policy-impact-analyzer.claude-skill.yaml)** (1.3KB) - Skill definition for policy analysis
- **[policy-impact-analyzer.md](policy-impact-analyzer.md)** (17KB) - Union Budget impact analysis - RBI monetary policy effects - PLI scheme beneficiaries - State government policies - Regulatory changes (SEBI, GST) - Global factors (crude oil, FII flows) - Sectoral impact assessment
#### 5. Portfolio Builder Sub-Skill- **[portfolio-builder.claude-skill.yaml](portfolio-builder.claude-skill.yaml)** (1.3KB) - Skill definition for portfolio construction
- **[portfolio-builder.md](portfolio-builder.md)** (21KB) - Risk profiling questionnaire - Asset allocation strategies (age-based, goal-based, risk-based) - Security selection guidelines - Implementation strategies (SIP vs Lumpsum) - Rebalancing framework - Special scenario portfolios - Ready-to-use portfolio templates