from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json, math
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, OPENAI_API_KEY

METRICS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]

# Model evaluator của RAGAS: khai báo riêng, tách khỏi GENERATION_MODEL/JUDGE_MODEL trong config.
RAGAS_LLM_MODEL = os.getenv("RAGAS_LLM_MODEL", "gpt-4o-mini")
RAGAS_EMBEDDING_MODEL = os.getenv("RAGAS_EMBEDDING_MODEL", "text-embedding-3-small")
RAGAS_MAX_ATTEMPTS = 3  # số lượt chấm tối đa cho các câu còn metric NaN


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _run_ragas(rows: dict, llm, embeddings) -> list[dict]:
    """Chạy 1 lượt RAGAS → list record (giữ thứ tự của rows), metric lỗi là NaN."""
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from ragas.run_config import RunConfig
    from datasets import Dataset

    result = evaluate(
        Dataset.from_dict(rows),
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=llm, embeddings=embeddings,
        run_config=RunConfig(max_workers=8, timeout=180),
        raise_exceptions=False,
    )
    return result.to_pandas().to_dict("records")


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Run RAGAS evaluation.

    Trả về 4 điểm trung bình, per_question (đúng thứ tự đầu vào) và
    metadata.evaluator_models. Raise khi thiếu key hoặc còn metric NaN sau
    RAGAS_MAX_ATTEMPTS lượt: không thay điểm chưa đo được bằng số giả.
    """
    rows = {"question": questions, "answer": answers,
            "contexts": contexts, "ground_truth": ground_truths}
    if len({len(column) for column in rows.values()}) != 1:
        raise ValueError("questions/answers/contexts/ground_truths phải cùng độ dài.")
    if not questions:
        return {**{m: 0.0 for m in METRICS}, "per_question": [], "metadata": {"evaluator_models": []}}
    if not OPENAI_API_KEY:
        raise RuntimeError("Thiếu OPENAI_API_KEY trong .env: RAGAS cần LLM và embedding để chấm.")

    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    llm = ChatOpenAI(model=RAGAS_LLM_MODEL, api_key=OPENAI_API_KEY, max_retries=6, timeout=120)
    embeddings = OpenAIEmbeddings(model=RAGAS_EMBEDDING_MODEL, api_key=OPENAI_API_KEY)

    # RAGAS trả NaN khi judge lỗi/parse hỏng → chấm lại riêng các câu còn thiếu metric.
    scores: list[dict] = [dict.fromkeys(METRICS) for _ in questions]
    pending = list(range(len(questions)))
    for _ in range(RAGAS_MAX_ATTEMPTS):
        records = _run_ragas({k: [v[i] for i in pending] for k, v in rows.items()}, llm, embeddings)
        if len(records) != len(pending):
            raise RuntimeError(f"RAGAS trả {len(records)} dòng cho {len(pending)} câu hỏi.")
        for i, record in zip(pending, records):
            for m in METRICS:
                value = record.get(m)
                if scores[i][m] is None and value is not None and math.isfinite(value):
                    scores[i][m] = min(1.0, max(0.0, float(value)))  # float Python, chặn sai số ngoài [0,1]
        pending = [i for i in pending if None in scores[i].values()]
        if not pending:
            break
    if pending:
        missing = {i: [m for m in METRICS if scores[i][m] is None] for i in pending}
        raise RuntimeError(f"RAGAS chưa đo được sau {RAGAS_MAX_ATTEMPTS} lượt (index câu → metric): {missing}")

    per_question = [EvalResult(question=q, answer=a, contexts=list(c), ground_truth=g, **s)
                    for q, a, c, g, s in zip(questions, answers, contexts, ground_truths, scores)]
    aggregate = {m: sum(getattr(r, m) for r in per_question) / len(per_question) for m in METRICS}
    return {**aggregate, "per_question": per_question,
            "metadata": {"evaluator_models": [llm.model_name, embeddings.model]}}


# Diagnostic Tree: metric thấp nhất → (chẩn đoán, hướng sửa)
DIAGNOSTIC_TREE = {
    "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature"),
    "context_recall": ("Missing relevant chunks", "Improve chunking or add BM25"),
    "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
    "answer_relevancy": ("Answer doesn't match question", "Improve prompt template"),
}


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    analyzed = []
    for r in eval_results:
        scores = {m: getattr(r, m) for m in METRICS}
        worst_metric = min(scores, key=scores.get)
        diagnosis, suggested_fix = DIAGNOSTIC_TREE[worst_metric]
        analyzed.append({
            "question": r.question,
            "answer": r.answer,
            "ground_truth": r.ground_truth,
            "avg_score": sum(scores.values()) / len(scores),
            "worst_metric": worst_metric,
            "score": scores[worst_metric],
            "scores": scores,
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })
    analyzed.sort(key=lambda f: f["avg_score"])
    return analyzed[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
