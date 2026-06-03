# Project Master Plan: Faithful Evidence-Centric Financial News Forecasting

## 1. Project Strategy & Foundational Overview
This master plan delineates the execution strategy for building a **Faithful Evidence-Centric Financial News Forecasting System** within a compressed six-week timeframe (June 3, 2026 – July 14, 2026). The project shifts focus from traditional surface-level prediction accuracy to **explanation faithfulness**—proving whether the structural evidence cited by an AI system truly drives its financial forecasting decisions or merely acts as post-hoc cosmetic justification.

### 1.1 Target Score & Strategic Boundary
The team is optimized around a 2-member structure. To maximize output efficiency under this constraint, the project targets a specific subset of the rubric designed to balance reliability with academic excellence:
*   **7 Basic Points (Full Clearance):** OpenSpec/Agentic SDLC documentation, Real Data Input Schema setup, Operational Temporal Retriever, Lexicon Rule-Based Evidence Extraction, Base Forecast Model, Baseline Faithfulness Metrics, and an Interactive Streamlit Visualization Dashboard.
*   **1.0 Bonus Point (C1 - Real Data Input):** Immediate ingestion of actual historical equity pricing and verified financial news feeds across at least 3 distinct tickers (AAPL, TSLA, NVDA), targeting a minimum corpus size of 300 data points.
*   **0.75 Advanced Point (B1 - Sufficiency & Counterfactual Perturbation):** Implementing a counterfactual framework to systematically mask or alter cited evidence texts, recalculate forecast confidence metrics, and statistically diagnose model faithfulness.
*   **Target Cumulative Score:** **8.75 / 10.0 Base Target**

---

## 2. Team Structure, Role Allocation & Governance

### 2.1 Role Consolidation Matrix
With the reduction from a 3-person academic group to a tight 2-member development team, roles are consolidated into clear operational tracks:

```
+-------------------------------------------------------------------------+
|                              PROJECT TEAM                               |
+------------------------------------+------------------------------------+
|             MEMBER A               |              MEMBER B              |
|     Research, Specs, & NLP         |       Data, Dashboard, & QA        |
+------------------------------------+------------------------------------+
| - OpenSpec Architecture & Docs     | - Historical Data Ingestion        |
| - Custom Financial Lexicon Rules   | - Temporal Retriever Architecture  |
| - Colab T4 FinBERT Fine-Tuning     | - Streamlit Application Frontend   |
| - Counterfactual Perturbation Logic| - System Integration & QA Testing  |
+------------------------------------+------------------------------------+
```

#### Member A: Research, Specs, & NLP Specialist
*   **Responsibilities:** Owner of the OpenSpec documentation layer (`proposal.md`, `spec.md`, `tasks.md`). Responsible for designing the textual data pre-processing mapping, establishing keyword extraction rules, orchestrating prompt frameworks for conversational LLMs, executing the advanced FinBERT deep-learning workflows inside Google Colab (T4 GPU), and mathematically modeling the baseline and advanced faithfulness equations.

#### Member B: Data, Dashboard, & Integration Engineer
*   **Responsibilities:** Owner of data acquisition pipelines, environment integrity, and cross-module execution. Responsible for orchestrating standard ingestion connectors, constructing the programmatic Temporal Retriever module to block information leakage, implementing unit testing suites via `pytest`, developing the interactive data rendering workspace using Streamlit, and implementing the end-to-end operational code integration.

### 2.2 Simple Human-AI Governance & Quality Gates
Rather than implementing heavy CI/CD infrastructure, human oversight of AI coding agents (GitHub Copilot, VSCode expansions, or Antigravity environments) is enforced using a transparent Markdown-driven validation ledger located inside `openspec/tasks.md`.

*   **Step 1 (Generation):** The assigned member utilizes an AI Agent to construct a module, test sequence, or specification document.
*   **Step 2 (Local Inspection):** The member runs local verification scripts, reviews syntax blocks, and guarantees that edge-cases (e.g., temporal boundaries) are addressed.
*   **Step 3 (Sign-off Ledger):** Upon verification, the developer appends a single tracking entry directly into the project tracking log:
    ```markdown
    - [TASK-ID] [YYYY-MM-DD] [Component Name] Approved by [Member A/B] via [Copilot/Gemini] -> Quality Gate Passed.
    ```
*   **Unreviewed Code Rule:** No code fragment suggested by an AI assistant may be merged into the operational main repository branches without an active local validation run and matching ledger entry.

---

## 3. Real-World Target Data Model

To secure the **C1 Bonus Point**, the project bypasses mock simulations and starts immediately with real market data elements.

### 3.1 Financial Labeling Framework
For each asset ticker, price shifts are computed using next-day close-to-close metrics:

$$\Delta P_{t+1} = rac{	ext{Close}_{t+1} - 	ext{Close}_t}{	ext{Close}_t}$$

Data points are automatically categorized according to structural financial boundaries:
*   **UP:** $\Delta P_{t+1} > 0.005$ (Price expansion exceeding +0.5%)
*   **DOWN:** $\Delta P_{t+1} < -0.005$ (Price contraction exceeding -0.5%)
*   **HOLD:** $-0.005 \le \Delta P_{t+1} \le 0.005$ (Stable sideways market)

### 3.2 Unified Ingestion JSON Schema
The system maps incoming records to a highly predictable JSON model structure, handling text processing pipeline logs natively:

```json
{
  "ticker": "AAPL",
  "forecast_time": "2026-06-03 09:00:00",
  "price_features": {
    "price_5d_return": -0.0152,
    "volume_change_pct": 0.0840
  },
  "news_data": [
    {
      "news_id": "N-AAPL-2026-001",
      "news_time": "2026-06-02 16:30:00",
      "raw_title": "Apple Facing Slower iPhone Shipments in Key Asian Markets Due to Supply Snarls",
      "cleaned_text": "apple facing slower iphone shipments key asian markets due supply snarls"
    },
    {
      "news_id": "N-AAPL-2026-002",
      "news_time": "2026-06-03 11:15:00",
      "raw_title": "Late breaking rumors suggest Apple product launch tonight",
      "cleaned_text": "late breaking rumors suggest apple product launch tonight"
    }
  ],
  "ground_truth": {
    "next_day_return": -0.0082,
    "label": "DOWN"
  }
}
```

---

## 4. Six-Week Phase-by-Phase Roadmap

```
2026-06-03                                2026-06-24                                2026-07-14
    |------- MILESTONE 1: CORE REPO -------|------- MILESTONE 2: ADVANCED & QA ------|
    Week 1: Specs & Ingestion Pipelines    Week 4: FinBERT Colab T4 GPU Model Training
    Week 2: Temporal Retriever & Rules     Week 5: B1 Counterfactual Framework & UI
    Week 3: Rule Forecast & Streamlit MVP  Week 6: Integration Tests, Video, Report
```

### 4.2 Detailed Sprint Breakdown

#### Week 1: Specifications & Ingestion Pipelines (June 3 – June 9, 2026)
*   **Deliverables:** Completed `proposal.md`, `spec.md`, and automated data scraping scripts producing the unified raw corpus.
*   **Member A (Research & Specs):** Draft the foundational OpenSpec definitions. Define explicit system boundaries, edge cases, user personas, and target boundaries. Write the core pre-processing specifications utilizing a pipeline design inspired by `koa-fin/sn2`.
*   **Member B (Data & Infra):** Implement data collectors utilizing `yfinance` to extract historical daily open, high, low, close, and volume matrices for AAPL, TSLA, and NVDA. Build standard news scrapers or integrate open-source datasets to aggregate matching financial text payloads. Ensure all elements map cleanly into the target database schema format.

#### Week 2: Temporal Retriever & Rules Engine (June 10 – June 16, 2026)
*   **Deliverables:** Core functional engines: `retriever.py`, `evidence_extractor.py`, and initial temporal unit testing blocks.
*   **Member A (Research & Specs):** Assemble the deterministic financial lexicons, establishing key token groups categorized by market tone (e.g., *Positive:* "surge", "beats", "expansion"; *Negative:* "misses", "slower", "lawsuit"). Write regex-driven pattern extraction configurations within the text engine.
*   **Member B (Data & Infra):** Construct the algorithmic temporal filter engine. Ensure any news record with a timestamp greater than or equal to the designated forecast execution boundary is flagged and routed directly to an isolated validation array (`invalid_future_news`), protecting the system from lookahead bias. Implement initial validation suites via `pytest`.

#### Week 3: Rule-Based Forecast Engine & Dashboard MVP (June 17 – June 23, 2026)
*   **Deliverables:** Completed `forecast_model.py` (Rule-Based variant), initial calculation formulas for confidence drop metrics, and a minimal working Streamlit canvas.
*   **Member A (Research & Specs):** Code the basic net sentiment model logic. Establish mathematical derivations for basic text confidence scores based on directional consensus margins. Write the foundational framework calculations for measuring baseline confidence drops.
*   **Member B (Data & Infra):** Scaffold the initial functional Streamlit application. Set up asset select boxes, data tables rendering valid vs. invalid news entries, and prominent system alert banners that flag lookahead errors or data integrity gaps. Ensure seamless cross-module data passing from Week 2 engines.

#### Week 4: FinBERT Colab T4 GPU Model Training (June 24 – June 30, 2026)
*   **Deliverables:** Fully functional Jupyter training notebook, fine-tuned model checkpoint parameters, and integrated advanced prediction capabilities in `src/forecast_model.py`.
*   **Member A (Research & Specs):** Establish the deep learning development cluster within Google Colab using a T4 hardware profile. Ingest the data corpus, tokenize headlines using standard HuggingFace packages, format numerical vector inputs (price trends), and fine-tune a sequence-classification model built on top of `ProsusAI/finbert`. Export the resulting weights.
*   **Member B (Data & Infra):** Abstract and bundle the serialized Colab neural network pipeline outputs into the project repo. Modify `src/forecast_model.py` to allow execution switches between the Rule-Based model and the new FinBERT Deep Learning pipeline.

#### Week 5: Counterfactual Framework & Dashboard Upgrade (July 1 – July 7, 2026)
*   **Deliverables:** Functional implementation of Advanced Feature B1 (`faithfulness_metrics.py`) and a polished interactive Streamlit user dashboard.
*   **Member A (Research & Specs):** Code the counterfactual transformation layers. Create masking functions that intercept chosen evidence strings, swap out core sentiment markers with completely neutral tokens, and re-feed the modified payload to the forecast model to compute faithfulness distributions.
*   **Member B (Data & Infra):** Upgrade the interactive Streamlit user terminal. Integrate advanced visualizations using Plotly, including interactive bar comparisons mapping original vs. counterfactual model behavior, prediction probability distribution charts, and summary analytics.

#### Week 6: Verification, Reporting, & Project Hand-off (July 8 – July 14, 2026)
*   **Deliverables:** Final end-to-end testing logs, an analytical engineering presentation report (`report.pdf`), and an uploaded 5-minute technical demo video clip.
*   **Member A (Research & Specs):** Compile the final 5-8 page technical report detailing system architecture, experimental results, and AI agent traces.
*   **Member B (Data & Infra):** Conduct exhaustive end-to-end validation passes. Record the 5-minute project demo video showcasing live data selection, model switches, and counterfactual testing. Pack the repository cleanly for delivery.

---

## 5. Step-by-Step Technical Implementation Guide

### 5.1 Step 1: Data Preparation & Pre-processing (`koa-fin/sn2` Style)
To preserve semantic clarity, raw news strings are normalized using a multi-tiered pipeline:
1.  **Token Normalization:** Lowercase all characters, remove non-alphanumeric punctuation marks, and strip leading/trailing white space.
2.  **Entity Preservation:** Map known market variants to uniform anchor keywords (e.g., "iPhone 17 Pro Max", "iPhones", and "iPhone sales" resolve uniformly to `iphone_sales`).
3.  **Temporal Windowing:** For a given `forecast_time` $T$, slice historical pricing arrays to capture metrics from $[T-5	ext{ days}, T)$ and filter candidate text inputs to those matching timestamps within the window $[T-72	ext{ hours}, T)$.

### 5.2 Step 2: Ingestion & Temporal Retriever Core Engine
The `TemporalRetriever` acts as an absolute information firewall to prevent future leakage. Below is the structural python implementation for `src/retriever.py`:

```python
import datetime
from typing import Dict, List, Tuple

class TemporalRetriever:
    def __init__(self, forecast_time_str: str):
        self.forecast_time = datetime.datetime.strptime(forecast_time_str, "%Y-%m-%d %H:%M:%S")

    def filter_news(self, news_list: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        valid_news = []
        invalid_future_news = []
        
        for news in news_list:
            news_time = datetime.datetime.strptime(news["news_time"], "%Y-%m-%d %H:%M:%S")
            # Strict temporal barrier check
            if news_time < self.forecast_time:
                valid_news.append(news)
            else:
                invalid_future_news.append(news)
                
        return valid_news, invalid_future_news
```

### 5.3 Step 3: Rule-Based Evidence Extraction Engine
The baseline extraction engine maps phrases to polarities using a local financial lexicon. Below is the structural implementation for `src/evidence_extractor.py`:

```python
import re
from typing import Dict, List

class RuleBasedEvidenceExtractor:
    def __init__(self):
        # Local financial lexicon configuration
        self.lexicon = {
            "down": ["slower", "misses", "decline", "weak", "deficit", "drop", "slump"],
            "up": ["growth", "beats", "surge", "expansion", "gain", "profit", "launch"]
        }

    def extract_evidence(self, cleaned_text: str) -> List[Dict]:
        extracted = []
        words = cleaned_text.split()
        
        for word in words:
            for direction, keywords in self.lexicon.items():
                if word in keywords:
                    # Capture immediate sentence window as contextual evidence text
                    match_pattern = rf"([^.
]*?{word}[^.
]*)"
                    match = re.search(match_pattern, cleaned_text)
                    evidence_fragment = match.group(0).strip() if match else word
                    
                    extracted.append({
                        "evidence_text": evidence_fragment,
                        "polarity": "positive" if direction == "up" else "negative",
                        "expected_direction": direction.upper(),
                        "support_score": 1.0
                    })
                    break # Single keyword match maps to one structural direction
        return extracted
```

### 5.4 Step 4: Dual-Model Training Framework

#### 5.4.1 Basic Model Tier (Rule-Based Net Sentiment Classifier)
The baseline model combines tabular market trends with extracted textual sentiment polarities:
*   **Formula:** Net Sentiment Score ($	ext{NSS}$) = $\sum 	ext{Positive Evidence} - \sum 	ext{Negative Evidence}$.
*   **Classification Boundary:**
    *   If $	ext{NSS} > 0$ and `price_5d_return` $\ge 0 ightarrow 	ext{Prediction: UP}$
    *   If $	ext{NSS} < 0$ and `price_5d_return` $< 0 ightarrow 	ext{Prediction: DOWN}$
    *   Otherwise $ightarrow 	ext{Prediction: HOLD}$
*   **Confidence Calculation:** Derived from normalized distribution margins:
    $$	ext{Confidence} = \max\left(0.5, rac{|	ext{NSS}|}{|	ext{NSS}| + 1}ight)$$

#### 5.4.2 Advanced Model Tier (FinBERT Fusion Network on Google Colab)
Executed on a Google Colab T4 GPU cluster, this architecture merges textual context vectors with standard market features. Below is the training and integration pipeline code:

```python
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

class FinBertFusionClassifier(nn.Module):
    def __init__(self, freeze_bert=True):
        super(FinBertFusionClassifier, self).__init__()
        # Load underlying FinBERT model base
        self.bert = AutoModel.from_pretrained("ProsusAI/finbert")
        if freeze_bert:
            for param in self.bert.parameters():
                param.requires_grad = False
                
        # Structural Fusion Layer: 768 BERT hidden tokens + 2 numerical price features
        self.fusion_layer = nn.Linear(768 + 2, 128)
        self.output_layer = nn.Linear(128, 3) # Output map for classes: UP, DOWN, HOLD
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, input_ids, attention_mask, price_features):
        bert_outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_vectors = bert_outputs.last_hidden_state[:, 0, :] # Extract standard CLS tokens
        
        # Concatenate text features with price features
        fused_vectors = torch.cat((cls_vectors, price_features), dim=1)
        x = self.relu(self.fusion_layer(fused_vectors))
        probabilities = self.softmax(self.output_layer(x))
        return probabilities
```

### 5.5 Step 5: Advanced Faithfulness Verification (B1 Counterfactual Framework)
To verify explanation faithfulness, the system uses a counterfactual framework that masks cited evidence keywords and measures the impact on model confidence. Below is the implementation for `src/faithfulness_metrics.py`:

```python
from typing import Dict, Any, Callable

class CounterfactualEvaluator:
    # model_inference_fn accepts a raw text string and returns a dictionary:
    # {"prediction": "UP/DOWN/HOLD", "confidence": float}
    def __init__(self, model_inference_fn: Callable[[str], Dict[str, Any]]):
        self.predict_pipeline = model_inference_fn

    def compute_counterfactual_impact(self, original_text: str, evidence_word: str) -> Dict[str, Any]:
        # Run baseline prediction pass
        orig_res = self.predict_pipeline(original_text)
        orig_pred = orig_res["prediction"]
        orig_conf = orig_res["confidence"]
        
        # Apply counterfactual transformation: replace sentiment keyword with a neutral token
        perturbed_text = original_text.replace(evidence_word, "[MASKED_MARKET_ELEMENT]")
        
        # Run counterfactual prediction pass
        pert_res = self.predict_pipeline(perturbed_text)
        pert_pred = pert_res["prediction"]
        pert_conf = pert_res["confidence"]
        
        # Calculate Confidence Drop metric
        if orig_pred == pert_pred:
            conf_drop = orig_conf - pert_conf
        else:
            conf_drop = orig_conf
        
        # Evaluate explanation faithfulness
        is_faithful = conf_drop > 0.10 or orig_pred != pert_pred
        
        return {
            "original_prediction": orig_pred,
            "original_confidence": orig_conf,
            "perturbed_prediction": pert_pred,
            "perturbed_confidence": pert_conf,
            "confidence_drop": round(conf_drop, 4),
            "evidence_faithfulness_status": "FAITHFUL" if is_faithful else "POST_HOC_DECORATION"
        }
```

---

## 6. AI Prompt Engineering & Coordination Playbook

### 6.1 Prompt Framework for Member A: OpenSpec Specification Drafting
**Context of Use:** Execute inside a conversational LLM workspace to generate initial design documents.

```text
SYSTEM ROLE: Expert Business Analyst & Financial Product Owner
CONTEXT: Working on an OpenSpec requirement model for a Faithful Evidence-Centric Financial News Forecasting framework.
TASK: Draft a structured markdown text block matching 'openspec/specs/forecasting/spec.md'.
REQUIREMENTS:
1. Define clear functional capabilities for the Evidence Extractor.
2. Outline specific Input/Output payload definitions using JSON schemas.
3. Formulate detailed Acceptance Criteria based on the following pattern:
   - GIVEN a prediction of DOWN caused by bad asset news,
   - WHEN the financial analyst opens the system user interface,
   - THEN render the matching headline fragment along with its associated publication timestamp,
   - AND raise an automated alert flag if its publication date occurs after the prediction window boundary.
OUTPUT FORMAT: Provide a clean markdown file structure without any conversational filler text.
```

### 6.2 Prompt Framework for Member B: Generating Test Suites via GitHub Copilot
**Context of Use:** Insert as a structured comment block directly above the file creation boundary inside VSCode.

```python
# Context: Automated testing for an index-driven Temporal Retriever module.
# Task: Construct a suite of pytest functions named 'test_temporal_leakage_rejection'.
# Requirements:
# 1. Initialize a mock system baseline parameter with a forecast_time of '2026-06-03 09:00:00'.
# 2. Append two separate mock headline payloads:
#    - Payload X: Published at '2026-06-02 16:30:00' (Expected output: Categorized as valid_news).
#    - Payload Y: Published at '2026-06-03 09:05:00' (Expected output: Categorized as invalid_future_news).
# 3. Assert that the length of the invalid data collection equals exactly 1.
# 4. Assert that the content of the valid collection matches the identifier properties of Payload X.
```

---

## 7. OpenSpec Directory Structure & Deliverables

The project repository must maintain the structural framework defined below to clear standard delivery checks:

```
group_id_project/
├── README.md                           <- Setup blueprints and local execution guides
├── report.pdf                          <- Detailed 5-8 page research document
├── demo_video_link.txt                 <- URL link to the recorded 5-minute system walkthrough
├── openspec/
│   ├── tasks.md                        <- Central developer task list and quality gates
│   └── faithful-evidence-forecasting/
│       ├── proposal.md                 <- Problem definitions and strategic boundaries
│       ├── design.md                   <- System architecture maps and component definitions
│       └── specs/
│           └── forecasting/
│               └── spec.md             <- Deep interface data specifications
├── data/
│   └── financial_corpus.csv            <- Real collected database (>300 target sample size)
├── src/
│   ├── __init__.py
│   ├── retriever.py                    <- Structural temporal protection logic
│   ├── evidence_extractor.py           <- Lexicon-driven rule parsing tools
│   ├── forecast_model.py               <- Dual Execution Engine (Rule-Based & FinBERT Fusion)
│   ├── faithfulness_metrics.py         <- Counterfactual transformation and evaluation layers
│   └── dashboard.py                    <- Interactive interface built on top of Streamlit
├── tests/
│   ├── test_temporal_retriever.py     <- Verification tests checking future information leakage
│   └── test_metrics.py                 <- Unit testing suites verifying counterfactual logic
└── outputs/
    ├── prediction_results.csv          <- Saved execution predictions
    └── figures/                        <- Plotly data visual assets
        ├── confidence_drop.png
        └── temporal_leakage_warning.png
```
