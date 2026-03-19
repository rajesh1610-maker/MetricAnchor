"use client";

import { useEffect, useRef, useState } from "react";
import { submitFeedback } from "@/lib/api";

const REASONS = [
  { id: "wrong_metric", label: "Wrong metric used" },
  { id: "wrong_filter", label: "Wrong filter applied" },
  { id: "wrong_date_range", label: "Wrong date range" },
  { id: "wrong_sql", label: "Incorrect SQL" },
  { id: "unclear_explanation", label: "Unclear explanation" },
  { id: "other", label: "Other" },
] as const;

type Reason = (typeof REASONS)[number]["id"];

interface FeedbackModalProps {
  questionId: string;
  questionText: string;
  onClose: () => void;
  onSubmitted?: (type: "correct" | "partial" | "wrong") => void;
}

export default function FeedbackModal({
  questionId,
  questionText,
  onClose,
  onSubmitted,
}: FeedbackModalProps) {
  const [feedbackType, setFeedbackType] = useState<"correct" | "partial" | "wrong" | null>(null);
  const [reasons, setReasons] = useState<Set<Reason>>(new Set());
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const overlayRef = useRef<HTMLDivElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  // Trap focus and handle Escape
  useEffect(() => {
    closeBtnRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  function toggleReason(r: Reason) {
    setReasons((prev) => {
      const next = new Set(prev);
      next.has(r) ? next.delete(r) : next.add(r);
      return next;
    });
  }

  async function handleSubmit() {
    if (!feedbackType) return;
    setSubmitting(true);
    try {
      const noteText = [
        ...(reasons.size > 0 ? [`Reasons: ${[...reasons].join(", ")}`] : []),
        ...(note.trim() ? [note.trim()] : []),
      ].join("\n");

      await submitFeedback(questionId, feedbackType, noteText || undefined);
      setSubmitted(true);
      onSubmitted?.(feedbackType);
      setTimeout(onClose, 1200);
    } catch {
      // Fail silently — feedback is best-effort
      onClose();
    } finally {
      setSubmitting(false);
    }
  }

  const needsReasons = feedbackType === "wrong" || feedbackType === "partial";

  return (
    // Overlay
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="feedback-title"
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose();
      }}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" aria-hidden />

      <div className="relative w-full max-w-md rounded-2xl border border-gray-700 bg-gray-900 shadow-2xl">
        {submitted ? (
          <div className="flex flex-col items-center justify-center py-10 gap-2">
            <span className="text-2xl">✓</span>
            <p className="text-sm text-gray-300">Thanks for the feedback.</p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="flex items-start justify-between p-5 border-b border-gray-800">
              <div>
                <h2 id="feedback-title" className="text-sm font-semibold text-gray-100">
                  Rate this answer
                </h2>
                <p className="mt-0.5 text-xs text-gray-500 line-clamp-2">{questionText}</p>
              </div>
              <button
                ref={closeBtnRef}
                onClick={onClose}
                aria-label="Close feedback dialog"
                className="ml-3 shrink-0 rounded-md p-1.5 text-gray-500 hover:bg-gray-800 hover:text-gray-200 transition-colors"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-5 space-y-5">
              {/* Rating buttons */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-2">How accurate was this answer?</p>
                <div className="flex gap-2">
                  {(["correct", "partial", "wrong"] as const).map((type) => {
                    const config = {
                      correct: { label: "Correct", icon: "✓", active: "bg-green-900/40 border-green-600 text-green-300" },
                      partial: { label: "Partially", icon: "~", active: "bg-yellow-900/30 border-yellow-600 text-yellow-300" },
                      wrong: { label: "Wrong", icon: "✕", active: "bg-red-900/30 border-red-600 text-red-300" },
                    }[type];
                    return (
                      <button
                        key={type}
                        onClick={() => setFeedbackType(type)}
                        className={`flex-1 rounded-lg border py-2.5 text-xs font-medium transition-colors ${
                          feedbackType === type
                            ? config.active
                            : "border-gray-700 text-gray-400 hover:border-gray-600 hover:text-gray-200"
                        }`}
                        aria-pressed={feedbackType === type}
                      >
                        <span className="block text-base mb-0.5">{config.icon}</span>
                        {config.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Reason checkboxes */}
              {needsReasons && (
                <div>
                  <p className="text-xs font-medium text-gray-400 mb-2">What went wrong?</p>
                  <div className="space-y-1.5">
                    {REASONS.map(({ id, label }) => (
                      <label
                        key={id}
                        className="flex items-center gap-2.5 cursor-pointer group"
                      >
                        <div
                          className={`h-4 w-4 shrink-0 rounded border flex items-center justify-center transition-colors ${
                            reasons.has(id)
                              ? "border-anchor-500 bg-anchor-500"
                              : "border-gray-600 group-hover:border-gray-500"
                          }`}
                          onClick={() => toggleReason(id)}
                        >
                          {reasons.has(id) && (
                            <svg className="h-2.5 w-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                        <input
                          type="checkbox"
                          checked={reasons.has(id)}
                          onChange={() => toggleReason(id)}
                          className="sr-only"
                          aria-label={label}
                        />
                        <span className="text-xs text-gray-300 group-hover:text-gray-100 transition-colors">
                          {label}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Notes */}
              <div>
                <label htmlFor="feedback-note" className="block text-xs font-medium text-gray-400 mb-1.5">
                  Additional notes{" "}
                  <span className="text-gray-600 font-normal">(optional)</span>
                </label>
                <textarea
                  id="feedback-note"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  rows={2}
                  placeholder="What should the correct answer have been?"
                  className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none resize-none"
                />
              </div>

              {/* Submit */}
              <button
                onClick={handleSubmit}
                disabled={!feedbackType || submitting}
                className="w-full rounded-lg bg-anchor-500 py-2.5 text-sm font-semibold text-white hover:bg-anchor-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                {submitting ? "Submitting…" : "Submit feedback"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
