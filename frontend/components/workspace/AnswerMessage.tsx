"use client";

import type { ReactNode } from "react";
import type { SourceCitation } from "@/lib/types/paper";

interface AnswerMessageProps {
  answer: string;
  sources: SourceCitation[];
}

function renderInlineMarkdown(text: string, keyPrefix: string): ReactNode[] {
  const tokenPattern =
    /(\*\*[^*]+\*\*|__[^_]+__|\*[^*\n]+\*|_[^_\n]+_|\x60[^\x60]+\x60|\[[^\]]+\]\(https?:\/\/[^)]+\))/g;

  return text.split(tokenPattern).filter(Boolean).map((token, index) => {
    const key = `${keyPrefix}-${index}`;

    if ((token.startsWith("**") && token.endsWith("**")) ||
        (token.startsWith("__") && token.endsWith("__"))) {
      return <strong key={key}>{token.slice(2, -2)}</strong>;
    }

    if ((token.startsWith("*") && token.endsWith("*")) ||
        (token.startsWith("_") && token.endsWith("_"))) {
      return <em key={key}>{token.slice(1, -1)}</em>;
    }

    if (token.startsWith("`") && token.endsWith("`")) {
      return (
        <code key={key} className="rounded bg-gray-100 px-1.5 py-0.5 text-[0.9em] font-mono text-gray-800">
          {token.slice(1, -1)}
        </code>
      );
    }

    const linkMatch = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)]+)\)$/);
    if (linkMatch) {
      return (
        <a
          key={key}
          href={linkMatch[2]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-700 underline underline-offset-2 break-words"
        >
          {linkMatch[1]}
        </a>
      );
    }

    return token;
  });
}

/**
 * Render the common Markdown emitted by LLMs as semantic React elements.
 * Raw HTML is never rendered, so model output remains text rather than markup.
 */
function renderMarkdown(markdown: string): ReactNode[] {
  const lines = markdown.replace(/\r\n?/g, "\n").trim().split("\n");
  const nodes: ReactNode[] = [];
  let index = 0;
  let key = 0;

  const isUnorderedItem = (line: string) => /^\s*[-*+]\s+/.test(line);
  const isOrderedItem = (line: string) => /^\s*\d+[.)]\s+/.test(line);
  const isBlockStart = (line: string) =>
    /^\s*#{1,3}\s+/.test(line) ||
    isUnorderedItem(line) ||
    isOrderedItem(line) ||
    /^\s*>\s?/.test(line) ||
    /^\s*```/.test(line);

  while (index < lines.length) {
    const line = lines[index];

    if (!line.trim()) {
      index += 1;
      continue;
    }

    const heading = line.match(/^\s*(#{1,3})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const className =
        level === 1
          ? "text-xl font-semibold mt-4 mb-2"
          : level === 2
            ? "text-lg font-semibold mt-4 mb-2"
            : "text-base font-semibold mt-3 mb-1";
      const HeadingTag = level === 1 ? "h2" : level === 2 ? "h3" : "h4";
      nodes.push(
        <HeadingTag key={`block-${key++}`} className={className}>
          {renderInlineMarkdown(heading[2], `heading-${key}`)}
        </HeadingTag>
      );
      index += 1;
      continue;
    }

    if (/^\s*```/.test(line)) {
      index += 1;
      const codeLines: string[] = [];
      while (index < lines.length && !/^\s*```/.test(lines[index])) {
        codeLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) index += 1;
      nodes.push(
        <pre key={`block-${key++}`} className="overflow-x-auto rounded-lg bg-gray-900 p-3 text-sm text-gray-100 my-3">
          <code>{codeLines.join("\n")}</code>
        </pre>
      );
      continue;
    }

    if (isUnorderedItem(line) || isOrderedItem(line)) {
      const ordered = isOrderedItem(line);
      const items: { indent: number; text: string; ordered: boolean }[] = [];

      while (index < lines.length && (isUnorderedItem(lines[index]) || isOrderedItem(lines[index]))) {
        const currentLine = lines[index];
        const unorderedMatch = currentLine.match(/^(\s*)[-*+]\s+(.+)$/);
        const orderedMatch = currentLine.match(/^(\s*)\d+[.)]\s+(.+)$/);
        const match = unorderedMatch || orderedMatch;
        if (!match) break;
        items.push({
          indent: match[1].replace(/\t/g, "  ").length,
          text: match[2],
          ordered: Boolean(orderedMatch),
        });
        index += 1;
      }

      const ListTag = ordered ? "ol" : "ul";
      const listClass = ordered
        ? "list-decimal pl-6 space-y-1 my-2"
        : "list-disc pl-6 space-y-1 my-2";
      nodes.push(
        <ListTag key={`block-${key++}`} className={listClass}>
          {items.map((item, itemIndex) => (
            <li
              key={itemIndex}
              className={item.indent > 0 ? "ml-5 marker:text-gray-500" : ""}
              style={item.indent > 0 ? { listStyleType: item.ordered ? "decimal" : "circle" } : undefined}
            >
              {renderInlineMarkdown(item.text, `list-${key}-${itemIndex}`)}
            </li>
          ))}
        </ListTag>
      );
      continue;
    }

    const quote = line.match(/^\s*>\s?(.*)$/);
    if (quote) {
      const quoteLines: string[] = [];
      while (index < lines.length && /^\s*>\s?/.test(lines[index])) {
        quoteLines.push(lines[index].replace(/^\s*>\s?/, ""));
        index += 1;
      }
      nodes.push(
        <blockquote key={`block-${key++}`} className="border-l-4 border-gray-300 pl-4 italic text-gray-700 my-3">
          {quoteLines.map((quoteLine, quoteIndex) => (
            <p key={quoteIndex}>{renderInlineMarkdown(quoteLine, `quote-${key}-${quoteIndex}`)}</p>
          ))}
        </blockquote>
      );
      continue;
    }

    const paragraphLines = [line];
    index += 1;
    while (index < lines.length && lines[index].trim() && !isBlockStart(lines[index])) {
      paragraphLines.push(lines[index]);
      index += 1;
    }

    nodes.push(
      <p key={`block-${key++}`} className="my-2 leading-7">
        {paragraphLines.map((paragraphLine, paragraphIndex) => (
          <span key={paragraphIndex}>
            {paragraphIndex > 0 && " "}
            {renderInlineMarkdown(paragraphLine, `paragraph-${key}-${paragraphIndex}`)}
          </span>
        ))}
      </p>
    );
  }

  return nodes;
}

export default function AnswerMessage({ answer, sources }: AnswerMessageProps) {
  return (
    <div className="flex gap-4 mb-6">
      <div className="w-8 h-8 rounded-full bg-light-blue flex items-center justify-center flex-shrink-0">
        <svg
          className="w-4 h-4 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>

      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-gray-900 mb-1">ResearchMate</div>

        <div className="text-gray-900 mb-4 leading-relaxed break-words">
          {renderMarkdown(answer)}
        </div>

        {sources && sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-sm font-medium text-gray-700 mb-2">
              Sources ({sources.length})
            </div>
            <div className="space-y-2">
              {sources.map((source, idx) => (
                <div
                  key={source.chunk_id}
                  className="flex items-start gap-2 text-sm text-gray-600 bg-gray-50 rounded-lg p-3"
                >
                  <span className="font-medium text-gray-900 flex-shrink-0">
                    [{idx + 1}]
                  </span>
                  <div className="flex-1">
                    <span className="font-medium">Page {source.page_number}</span>
                    {source.section && (
                      <span className="text-gray-500"> · {source.section}</span>
                    )}
                    <span className="text-gray-400 ml-2">
                      (relevance: {(source.similarity * 100).toFixed(0)}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
