# ĐỀ ĐỒ ÁN CUỐI KÌ
Môn: Công nghệ mới

## Agentic AI trong SDLC cho hệ thống dự báo xu hướng cổ phiếu từ tin tức có kiểm chứng bằng chứng

**Câu hỏi nghiên cứu trung tâm:**
Khi một mô hình dự báo stock movement từ news, liệu evidence mà nó đưa ra có thật sự quyết định prediction không?

- **Quy mô nhóm:** 03 sinh viên/nhóm
- **Thang điểm chính:** 10 điểm = 7 điểm cơ bản + 3 điểm nâng cao
- **Điểm cộng:** Tối đa 2 điểm cho dữ liệu thật và GPU
- **Sản phẩm chính:** Prototype + OpenSpec + Dashboard + Báo cáo + Demo
- **Định hướng:** ML/NLP + Agentic SDLC + Explainable/Trustworthy AI

> Tài liệu giao đồ án cho sinh viên - phiên bản dễ hiểu, có ví dụ minh họa và rubric chi tiết.

---

## Mục lục ngắn
1. Bối cảnh và mục tiêu đồ án
2. Bài toán và ví dụ trực quan
3. Kiến trúc hệ thống cần xây dựng
4. Áp dụng Agentic AI vào SDLC và OpenSpec
5. Phần A - Yêu cầu cơ bản: 7 điểm
6. Phần B - Yêu cầu nâng cao: 3 điểm
7. Điểm cộng: tối đa 2 điểm
8. Phân công nhóm 3 sinh viên
9. Sản phẩm cần nộp
10. Rubric tổng hợp và câu hỏi phản biện
11. Kịch bản demo và lưu ý đạo đức

---

## 1. Bối cảnh và mục tiêu đồ án

### Ý tưởng lớn
Đồ án không chỉ hỏi mô hình dự báo đúng hay sai, mà hỏi sâu hơn: mô hình dự báo dựa trên bằng chứng nào, bằng chứng đó có đúng thời điểm không, và nếu bỏ bằng chứng đó thì dự báo có thay đổi không?

Trong tài chính, nhiều hệ thống AI có thể đọc tin tức và dự báo cổ phiếu sẽ tăng, giảm hoặc đi ngang. Tuy nhiên, một mô hình có thể đưa ra lời giải thích nghe rất hợp lí nhưng chưa chắc lời giải thích đó phản ánh đúng nguyên nhân khiến mô hình ra quyết định. Vì vậy, đồ án này yêu cầu sinh viên xây dựng một prototype nhỏ để kiểm chứng tính faithful của evidence trong bài toán dự báo xu hướng cổ phiếu từ tin tức.

Sinh viên không cần xây dựng hệ thống giao dịch thật. Trọng tâm của đồ án là học cách áp dụng Agentic AI vào vòng đời phát triển phần mềm: từ đặc tả yêu cầu, thiết kế, hiện thực, kiểm thử, đánh giá, trực quan hóa, đến phản biện giới hạn của hệ thống.

### 1.1. Chuẩn đầu ra mong đợi
- Hiểu được sự khác nhau giữa prediction accuracy và explanation faithfulness.
- Biết đặc tả một hệ thống ML/NLP theo hướng có kiểm chứng bằng OpenSpec.
- Biết dùng AI agent trong SDLC nhưng vẫn có quality gate, test và kiểm soát của con người.
- Xây dựng được một pipeline nhỏ gồm lọc tin theo thời gian, trích xuất evidence, dự báo, đánh giá faithfulness và visualize kết quả.
- Biết trình bày kết quả bằng dashboard, biểu đồ, bảng cảnh báo và phân tích hạn chế.

---

## 2. Bài toán và ví dụ trực quan
Hệ thống nhận đầu vào là mã cổ phiếu, thời điểm dự báo, dữ liệu giá quá khứ và danh sách tin tức trước thời điểm dự báo. Hệ thống trả về dự báo UP/DOWN/HOLD, độ tự tin, evidence được dùng, rationale và các metric kiểm chứng evidence.

| Thành phần | Ví dụ | Ý nghĩa |
| --- | --- | --- |
| ticker | AAPL | Mã cổ phiếu cần dự báo |
| forecast_time | 2025-03-12 09:00 | Thời điểm hệ thống ra dự báo |
| news_time | 2025-03-11 08:30 | Thời điểm tin tức được công bố |
| news_text | Apple reports weak iPhone sales in China | Nội dung tin tức |
| price_5d_return | -0.02 | Biến động giá 5 ngày gần nhất |
| label | DOWN | Nhãn thực tế dùng để đánh giá |

### 2.1. Ví dụ 1 - Evidence có thể faithful
Mô hình dự báo TSLA giảm. Tin tức được cite là: "Tesla phải thu hồi một lượng lớn xe do lỗi phần mềm an toàn". Khi bỏ tin này khỏi input, confidence giảm từ 0.81 xuống 0.55. Điều này cho thấy evidence có khả năng quan trọng đối với prediction.
- Prediction gốc: DOWN, confidence = 0.81
- Bỏ cited evidence: DOWN, confidence = 0.55
- Confidence drop = 0.26
**Kết luận:** evidence có necessity tương đối cao

### 2.2. Ví dụ 2 - Evidence chỉ là lời giải thích trang trí
Mô hình dự báo NVDA tăng. Evidence được cite là "NVIDIA công bố chip AI thế hệ mới”. Nhưng khi bỏ tin này khỏi input, mô hình vẫn dự báo UP với confidence gần như không đổi: 0.88 xuống 0.86. Evidence nghe hợp lí nhưng có thể chưa thật sự quyết định prediction.
- Prediction gốc: UP, confidence = 0.88
- Bỏ cited evidence: UP, confidence = 0.86
- Confidence drop = 0.02
**Kết luận:** evidence có thể chỉ là rationale hậu nghiệm

### 2.3. Ví dụ 3 - Lỗi temporal leakage
Ngày dự báo là 2025-03-12 lúc 09:00. Nếu hệ thống dùng tin xuất hiện lúc 2025-03-12 lúc 15:30 thì đây là lỗi dùng thông tin tương lai. Trong tài chính, lỗi này làm kết quả thí nghiệm trở nên không đáng tin.
- forecast_time: 2025-03-12 09:00
- news_time: 2025-03-12 15:30
- Vì news_time > forecast_time → loại tin này khỏi input

### 2.4. Ví dụ 4 - Counterevidence
Mô hình dự báo AAPL tăng vì có tin ra mắt sản phẩm mới. Tuy nhiên, cùng ngày cũng có tin doanh số iPhone tại Trung Quốc giảm. Nếu hệ thống chỉ cite tin tích cực mà bỏ qua tin trái chiều, điểm Counterevidence Coverage sẽ thấp.
- Prediction: UP
- Pro evidence: Apple launches new product
- Counterevidence: iPhone sales in China decline
- **Câu hỏi:** mô hình có nhận diện cả hai chiều bằng chứng không?

---

## 3. Kiến trúc hệ thống cần xây dựng

**Pipeline tổng quát**
News + Price Data → Temporal Retriever → Evidence Extractor → Evidence Selector → Forecast Model → Faithfulness Evaluator → Visualization Dashboard

| Khối | Nhiệm vụ | Ví dụ đầu ra |
| --- | --- | --- |
| Temporal Retriever | Chỉ lấy tin trước thời điểm dự báo | valid_news, invalid_future_news |
| Evidence Extractor | Trích xuất bằng chứng nhỏ từ tin tức | weak iPhone sales → negative → DOWN |
| Evidence Selector | Chọn pro evidence và counterevidence | pro: earnings beat; counter: weak guidance |
| Forecast Model | Dự báo UP/DOWN/HOLD | DOWN, confidence = 0.72 |
| Faithfulness Evaluator | Kiểm tra support, necessity, sufficiency, temporal validity | confidence_drop = 0.21 |
| Dashboard | Hiển thị prediction, evidence, cảnh báo và biểu đồ | bar chart, radar chart, table |

### 3.1. Data schema đề xuất
```json
{
  "ticker": "AAPL",
  "forecast_time": "2025-03-12 09:00",
  "news": [
    {
      "news_id": "0001",
      "news_time": "2025-03-11 08:30",
      "title": "Apple reports weak iPhone sales in China",
      "text": "..."
    }
  ],
  "price_features": {
    "price_5d_return": -0.02,
    "volume_change": 0.15
  },
  "label": "DOWN"
}
```

### 3.2. Output dự kiến
```json
{
  "ticker": "AAPL",
  "prediction": "DOWN",
  "confidence": 0.72,
  "evidence": [
    {
      "news_id": "0001",
      "evidence_text": "weak iPhone sales in China",
      "polarity": "negative",
      "expected_direction": "DOWN",
      "support_score": 1.0
    }
  ],
  "faithfulness": {
    "temporal_validity": 1.0,
    "evidence_support": 1.0,
    "confidence_drop": 0.21
  }
}
```

---

## 4. Áp dụng Agentic AI vào SDLC và OpenSpec
Điểm quan trọng của đồ án là sinh viên không chỉ dùng AI để viết code, mà phải dùng AI như một tác nhân hỗ trợ có kiểm soát trong SDLC. Mỗi bước cần có đặc tả, output rõ ràng, test và review của con người.

| Pha SDLC | AI agent có thể hỗ trợ | Sinh viên phải kiểm soát | Minh chứng cần nộp |
| --- | --- | --- | --- |
| Requirement | Tạo user stories, acceptance criteria | Kiểm tra yêu cầu có rõ và test được không | proposal.md, spec.md |
| Design | Đề xuất kiến trúc, schema, dashboard | Chọn thiết kế vừa sức nhóm | design.md |
| Implementation | Sinh code mẫu, gợi ý hàm | Đọc hiểu và chỉnh sửa code | src/, commit log |
| Testing | Sinh test case và dữ liệu lỗi | Tự chạy test, sửa lỗi | tests/, test report |
| Evaluation | Gợi ý metric, phân tích kết quả | Không overclaim, có limitation | result tables, figures |
| Operation | Gợi ý trace/log | Không để agent tự quyết định không kiểm soát | run_log.json, dashboard |

### 4.1. Cấu trúc OpenSpec tối thiểu
```text
openspec/
  changes/
    faithful-evidence-forecasting/
      proposal.md
      design.md
      tasks.md
  specs/
    forecasting/
      spec.md
```

### 4.2. Ví dụ user story và acceptance criteria
**User story:**
Là một nhà phân tích tài chính, tôi muốn xem evidence nào khiến mô hình dự báo có phiếu giảm, để biết dự báo đó có đáng tin hay không.

**Acceptance criteria:**
- Given một prediction DOWN,
- When người dùng mở dashboard,
- Then hệ thống phải hiển thị ít nhất 1 evidence ủng hộ DOWN,
- And hiển thị thời gian xuất bản của evidence,
- And cảnh báo nếu evidence xuất hiện sau thời điểm dự báo.

---

## 5. PHẦN A - Yêu cầu cơ bản: 7 điểm
**Mục tiêu phần cơ bản:** Nhóm trung bình vẫn có thể hoàn thành bằng dataset nhỏ hoặc mô phỏng, rule-based model, metric đơn giản và dashboard dễ hiểu.

**A1. OpenSpec + Agentic SDLC - 1.0 điểm**
- Có `proposal.md`, `design.md`, `tasks.md`, `spec.md`.
- Spec nêu rõ input/output, chức năng và acceptance criteria.
- Có mô tả AI agent được dùng ở bước nào trong SDLC.
- *Ví dụ minh họa:* Ví dụ task: tạo dữ liệu mẫu; viết retriever; viết evidence extractor; viết forecast model; viết dashboard; viết test temporal leakage.

**A2. Dataset nhỏ hoặc dữ liệu mô phỏng - 1.0 điểm**
- Ít nhất 30 dòng dữ liệu.
- Có ticker, forecast_time, news_time, news_text, label UP/DOWN/HOLD.
- Có cả tin hợp lệ và tin vi phạm thời gian để test.
- *Ví dụ minh họa:* AAPL, 2025-03-12 09:00, 2025-03-11 08:00, Apple reports weak iPhone sales, DOWN.

**A3. Temporal Retriever - 1.0 điểm**
- Lọc đúng tin trước/sau thời điểm dự báo.
- Xuất danh sách `valid_news` và `invalid_future_news`.
- Có test case minh họa lỗi temporal leakage.
- *Ví dụ minh họa:* news_time 2025-03-12 15:00 bị loại nếu forecast_time là 2025-03-12 09:00.

**A4. Evidence Extraction đơn giản - 1.0 điểm**
- Trích được `evidence_text` từ news.
- Phân loại positive/negative/neutral hoặc expected_direction UP/DOWN/HOLD.
- Có ít nhất 5 ví dụ đúng/sai.
- *Ví dụ minh họa:* "misses expectations" → negative → expected_direction DOWN.

**A5. Forecast Model cơ bản - 1.0 điểm**
- Chạy được prediction UP/DOWN/HOLD.
- Có confidence hoặc score.
- Có accuracy hoặc confusion matrix.
- Có giải thích một prediction cụ thể.
- *Ví dụ minh họa:* Rule-based: positive_count - negative_count > 0 thì UP; < 0 thì DOWN; = 0 thì HOLD.

**A6. Faithfulness Metrics cơ bản - 1.0 điểm**
- Tính Evidence Support.
- Tính Temporal Validity.
- Tính Confidence Drop khi bỏ cited evidence.
- Có bảng kết quả cho nhiều mẫu.
- *Ví dụ minh họa:* Confidence gốc 0.80, bỏ cited evidence còn 0.55, confidence drop = 0.25.

**A7. Visualization Dashboard và báo cáo - 1.0 điểm**
- Dashboard hoặc notebook chạy được.
- Có ít nhất 4 bảng/hình: prediction distribution, evidence table, confidence drop chart, temporal leakage warning.
- Có báo cáo ngắn 5-8 trang.
- *Ví dụ minh họa:* Dashboard hiển thị: Ticker AAPL, Prediction DOWN, Confidence 0.72, Evidence, Support, Temporal Validity, Confidence Drop.

---

## 6. PHẦN B - Yêu cầu nâng cao: 3 điểm
**Mục tiêu phần nâng cao:** Dùng để phân loại nhóm khá giỏi. Nhóm cần làm sâu hơn về counterfactual, counterevidence, market consistency và maturity của Agentic SDLC.

| Mục | Điểm | Yêu cầu | Ví dụ |
| --- | --- | --- | --- |
| B1. Sufficiency + Counterfactual Perturbation | 0.75 | Chỉ dùng cited evidence để dự báo lại; thay evidence bằng neutral/counterfactual news. | Full input DOWN 0.78; only evidence DOWN 0.69. |
| B2. Counterevidence Coverage | 0.75 | Tách pro evidence và counterevidence; tính coverage. | Prediction UP nhưng vẫn phát hiện “weak guidance" là counterevidence. |
| B3. Market Consistency + Regime Analysis | 0.75 | So sánh evidence với return/volume sau tin; phân tích bull/bear/sideway. | Tin tiêu cực + next-day return -3.2% + volume tăng → consistency cao. |
| B4. Agentic SDLC Maturity | 0.75 | Có ít nhất 3 agent role, trace log, quality gate và reflection. | Research Agent, Coding Agent, Testing/Reviewer Agent. |

### 6.1. Ví dụ counterfactual perturbation
- Gốc: "Tesla misses delivery expectations." → negative → DOWN
- Thay thế counterfactual: "Tesla holds annual investor meeting." → neutral
- Nếu prediction vẫn DOWN với confidence gần như không đổi, mô hình có thể chưa thật sự nhạy với evidence.

### 6.2. Ví dụ trace log Agentic SDLC
```json
{
  "run_id": "R001",
  "agent_role": "Testing Agent",
  "task": "Generate temporal leakage test cases",
  "input": "forecast_time and news_time examples",
  "output": "5 unit tests",
  "human_review": "accepted with edits",
  "quality_gate": "passed"
}
```

---

## 7. Điểm cộng: tối đa 2 điểm
**Nguyên tắc điểm cộng:** Điểm cộng dành cho nhóm có thể thử nghiệm trên dữ liệu thật và/hoặc sử dụng GPU cho mô hình nâng cao. Điểm cuối cùng = min(10, điểm chính + điểm cộng).

| Mục điểm cộng | Điểm tối đa | Yêu cầu chính | Minh chứng |
| --- | --- | --- | --- |
| C1. Dữ liệu thật | 1.0 | Dùng dữ liệu giá/news thật; ít nhất 3 ticker và 300 mẫu; xử lý temporal leakage. | Nguồn dữ liệu, script tiền xử lý, bảng thống kê. |
| C2. GPU/mô hình nâng cao | 1.0 | Dùng FinBERT/Transformer/LLM/LSTM/PatchTST/TimesNet hoặc fusion model. | Môi trường GPU, thời gian chạy, so sánh với baseline, visualization. |

### 7.1. Gợi ý nguồn dữ liệu thật
- Dữ liệu giá: Yahoo Finance, Alpha Vantage, Stooq, Nasdaq Data Link, Kaggle.
- Dữ liệu tin tức: Kaggle financial news, Financial PhraseBank, FiQA, Reuters dataset nếu có quyền sử dụng, hoặc dữ liệu crawl hợp lệ.
- Dữ liệu cần có ticker, trading date, news time, news text, close price và label UP/DOWN/HOLD.

### 7.2. Ví dụ tạo label từ dữ liệu thật
- `return_next_day = (close_t+1 - close_t) / close_t`
- Nếu `return_next_day > 0.005` → UP
- Nếu `return_next_day < -0.005` → DOWN
- Ngược lại → HOLD

### 7.3. Ví dụ bảng minh chứng GPU
| Mô hình | Thiết bị | Số mẫu | Epoch | Thời gian | Accuracy | Avg Confidence Drop |
| --- | --- | --- | --- | --- | --- | --- |
| Rule-based | CPU | 500 | | 5 giây | 48% | 0.08 |
| FinBERT + Logistic | GPU T4 | 500 | inference | 3 phút | 55% | 0.14 |
| FinBERT + LSTM | GPU T4 | 500 | 5 | 12 phút | 58% | 0.18 |

---

## 8. Phân công nhóm 3 sinh viên

| Vai trò | Nhiệm vụ | Sản phẩm chính |
| --- | --- | --- |
| Sinh viên 1 - Research & Spec Owner | Hiểu bài toán, viết OpenSpec, user stories, metric, báo cáo research gap. | proposal.md, spec.md, metric_definition.md, phần 1-3 báo cáo |
| Sinh viên 2 - ML/NLP Engineer | Tạo dataset, retriever, evidence extractor, forecast model, chạy thí nghiệm. | data.csv, retriever.py, evidence_extractor.py, forecast_model.py, results.csv |
| Sinh viên 3 - Visualization & QA Engineer | Dashboard, biểu đồ, test case, kiểm tra temporal leakage, demo. | dashboard.py, visualization.ipynb, tests/, demo video |

**Lưu ý:** Ba sinh viên phải hiểu toàn bộ hệ thống. Không chấp nhận tình trạng mỗi người chỉ biết một file hoặc không giải thích được luồng dữ liệu end-to-end.

---

## 9. Sản phẩm cần nộp
```text
group_id_project/
  README.md
  report.pdf
  demo_video_link.txt
  openspec/
    changes/
      faithful-evidence-forecasting/
        proposal.md
        design.md
        tasks.md
    specs/
      forecasting/spec.md
  data/
    sample_news_price.csv
  src/
    retriever.py
    evidence_extractor.py
    forecast_model.py
    faithfulness_metrics.py
    dashboard.py
  tests/
    test_temporal_retriever.py
    test_metrics.py
  outputs/
    prediction_results.csv
    faithfulness_results.csv
  figures/
    prediction_distribution.png
    confidence_drop.png
    temporal_leakage_warning.png
    faithfulness_radar.png
```

### 9.1. Cấu trúc báo cáo gợi ý
1. Giới thiệu bài toán và động lực.
2. Research gap: accuracy chưa đủ, cần faithful evidence.
3. Thiết kế Agentic SDLC và OpenSpec.
4. Mô tả dữ liệu.
5. Mô tả pipeline kỹ thuật.
6. Metric và cách đánh giá.
7. Kết quả thực nghiệm và visualization.
8. Phân tích case đúng/sai.
9. Limitations và hướng phát triển.
10. Phụ lục: prompt, agent trace, test cases.

---

## 10. Rubric tổng hợp

| Thành phần | Điểm | Ghi chú |
| --- | --- | --- |
| A1. OpenSpec + Agentic SDLC | 1.0 | Bắt buộc |
| A2. Dataset nhỏ hoặc mô phỏng | 1.0 | Bắt buộc |
| A3. Temporal Retriever | 1.0 | Bắt buộc |
| A4. Evidence Extraction | 1.0 | Bắt buộc |
| A5. Forecast Model cơ bản | 1.0 | Bắt buộc |
| A6. Faithfulness Metrics cơ bản | 1.0 | Bắt buộc |
| A7. Visualization Dashboard + báo cáo | 1.0 | Bắt buộc |
| B1. Sufficiency + Counterfactual Perturbation | 0.75 | Nâng cao |
| B2. Counterevidence Coverage | 0.75 | Nâng cao |
| B3. Market Consistency + Regime Analysis | 0.75 | Nâng cao |
| B4. Agentic SDLC Maturity | 0.75 | Nâng cao |
| C1. Dữ liệu thật | +1.0 | Điểm cộng |
| C2. GPU/mô hình nâng cao | +1.0 | Điểm cộng |

### 10.1. Mức phân loại kết quả
| Mức điểm | Đặc điểm sản phẩm |
| --- | --- |
| 5.0-6.5 | Có dataset nhỏ, lọc tin theo thời gian, trích evidence đơn giản, dự báo cơ bản, dashboard tối thiểu. |
| 6.5-8.0 | Có metric faithfulness rõ, confidence drop, test case, OpenSpec tương đối đầy đủ, dashboard dễ hiểu. |
| 8.0-9.0 | Có sufficiency test, counterevidence, temporal leakage cảnh báo tốt, visualization đẹp, agent trace. |
| 9.0-10.0 | Pipeline hoàn chỉnh, thực nghiệm sâu, dashboard sinh động, market consistency/regime analysis, reflection tốt. |
| Điểm cộng tối đa +2 | Dữ liệu thật và/hoặc GPU, nhưng điểm cuối cùng không vượt quá 10. |

---

## 11. Kịch bản demo và câu hỏi phản biện

### 11.1. Kịch bản demo 5 phút
1. Mở dashboard.
2. Chọn ticker, ví dụ AAPL.
3. Chọn forecast date.
4. Hiển thị các tin hợp lệ trước thời điểm dự báo.
5. Hệ thống dự báo UP/DOWN/HOLD.
6. Hiển thị evidence và rationale.
7. Bấm hoặc mô phỏng chức năng "Remove cited evidence".
8. So sánh confidence trước/sau.
9. Kết luận evidence có faithful hay không.
10. Trình bày một limitation quan trọng.

### 11.2. Ví dụ lời trình bày demo
"Ban đầu hệ thống dự báo AAPL giảm với confidence 0.76. Evidence chính là tin doanh số iPhone tại Trung Quốc giảm. Sau khi bỏ evidence này, confidence giảm xuống 0.51. Trong khi đó, nếu bỏ một tin ngẫu nhiên không được cite, confidence chỉ giảm xuống 0.73. Vì vậy, evidence được cite có vai trò quan trọng hơn tin ngẫu nhiên và có dấu hiệu faithful."

### 11.3. Câu hỏi phản biện cho giảng viên
- Vì sao nhóm nói evidence này là faithful?
- Nếu bỏ evidence mà prediction không đổi thì kết luận gì?
- Làm sao biết hệ thống không dùng tin tương lai?
- Counterevidence là gì? Nhóm có phát hiện được không?
- Accuracy cao nhưng faithfulness thấp thì có nên tin mô hình không?
- AI agent đã giúp nhóm ở bước nào?
- Nhóm đã kiểm soát lỗi của AI agent như thế nào?
- Nếu triển khai thật trong tài chính, rủi ro lớn nhất là gì?

---

## 12. Lưu ý đạo đức và giới hạn
- Đồ án chỉ phục vụ mục đích học tập, không được dùng để khuyến nghị mua/bán chứng khoán thật.
- Dữ liệu nhỏ hoặc mô phỏng chưa đại diện cho thị trường thật.
- Evidence extraction có thể sai, đặc biệt khi tin tức mơ hồ hoặc nhiều nghĩa.
- LLM có thể tạo rationale nghe hợp lí nhưng không faithful.
- Accuracy không đồng nghĩa với lợi nhuận.
- Tin tức có thể đã được phản ánh vào giá trước khi mô hình xử lý.
- Tuyệt đối không được dùng tin xuất hiện sau thời điểm dự báo.

---

## 13. Gợi ý công nghệ triển khai

| Hạng mục | Lựa chọn dễ | Lựa chọn nâng cao |
| --- | --- | --- |
| Ngôn ngữ | Python | Python + FastAPI/Streamlit |
| Dataset | CSV mô phỏng | Yahoo Finance + financial news dataset |
| Evidence Extraction | Rule-based keyword | FinBERT/LLM extraction |
| Forecast Model | Rule-based/Logistic Regression | LSTM/PatchTST/Transformer fusion |
| Dashboard | Jupyter/Streamlit | Streamlit + Plotly interactive |
| Testing | pytest đơn giản | pytest + schema validation + experiment tracking |
| Agentic SDLC | ChatGPT/Cursor hỗ trợ spec/code/test | Multi-agent roles + trace + quality gate |

---

## 14. Checklist trước khi nộp
- [ ] Có `README` hướng dẫn chạy dự án.
- [ ] Có OpenSpec proposal/design/tasks/spec.
- [ ] Có dữ liệu mẫu hoặc dữ liệu thật.
- [ ] Có module lọc tin theo thời gian.
- [ ] Có module trích xuất evidence.
- [ ] Có mô hình dự báo UP/DOWN/HOLD.
- [ ] Có ít nhất 3 metric faithfulness cơ bản.
- [ ] Có dashboard hoặc notebook visualize.
- [ ] Có test case cho temporal leakage.
- [ ] Có báo cáo và demo video.
- [ ] Có reflection về việc dùng AI agent trong SDLC.
- [ ] Không dùng dữ liệu tương lai trong thí nghiệm.

---

## 15. Tài liệu tham khảo gợi ý
- OpenSpec - Spec-driven development workflow: https://github.com/Fission-AI/OpenSpec/
- OpenSpec Workflows: proposal, specs, design, tasks, implementation, archive.
- Agentic SDLC: requirement, design, implementation, testing, observability, quality gate.
- FinBERT / Financial NLP datasets: dùng để tham khảo khi nhóm làm phần nâng cao.
- Yahoo Finance hoặc các nguồn dữ liệu hợp lệ để lấy giá cổ phiếu trong phần điểm cộng.

> **Thông điệp cuối cùng**
> Trong đồ án này, dự báo đúng là chưa đủ. Sinh viên cần chứng minh mô hình dự báo dựa trên evidence nào, evidence đó có đúng thời điểm không, có ảnh hưởng đến prediction không, và có được con người kiểm tra qua visualization hay không.
