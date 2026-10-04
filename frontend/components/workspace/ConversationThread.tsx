"use client";

import QuestionMessage from "./QuestionMessage";
import AnswerMessage from "./AnswerMessage";
import type { QuestionResponse } from "@/lib/types/paper";

export interface ConversationEntry {
  question: string;
  response?: QuestionResponse;
  answer?: QuestionResponse;
}

interface ConversationThreadProps {
  conversation: ConversationEntry[];
}

export default function ConversationThread({
  conversation,
}: ConversationThreadProps) {
  if (conversation.length === 0) {
    return null;
  }

  return (
    <div className="space-y-6 mb-8">
      {conversation.map((entry, idx) => {
        const qaResponse = entry.response || entry.answer;
        return (
          <div key={idx}>
            <QuestionMessage question={entry.question} />
            {qaResponse && qaResponse.has_sufficient_context && (
              <AnswerMessage
                answer={qaResponse.answer}
                sources={qaResponse.sources}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
