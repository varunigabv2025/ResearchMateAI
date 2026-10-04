"use client";

import type { ComparePapersResponse } from "@/lib/types/comparison";

interface ComparisonResultsProps {
  result: ComparePapersResponse;
  onReset: () => void;
}

export default function ComparisonResults({
  result,
  onReset,
}: ComparisonResultsProps) {
  const { papers } = result;

  return (
    <div>
      {/* Header with Reset Button */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="font-serif text-2xl font-bold text-gray-900 mb-1">
            Comparison Results
          </h2>
          <p className="text-gray-600">
            Comparing {papers.length} research papers
          </p>
        </div>
        <button
          onClick={onReset}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          New Comparison
        </button>
      </div>

      {/* Comparison Table - Desktop */}
      <div className="hidden lg:block bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 w-40">
                  Aspect
                </th>
                {papers.map((paper) => (
                  <th
                    key={paper.paper_id}
                    className="px-6 py-4 text-left text-sm font-semibold text-gray-900"
                  >
                    <div className="max-w-xs">
                      <div className="font-medium truncate">
                        {paper.filename}
                      </div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {/* Method */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900 align-top">
                  Method
                </td>
                {papers.map((paper) => (
                  <td
                    key={paper.paper_id}
                    className="px-6 py-4 text-sm text-gray-700 align-top"
                  >
                    {paper.method}
                  </td>
                ))}
              </tr>

              {/* Dataset */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900 align-top">
                  Dataset
                </td>
                {papers.map((paper) => (
                  <td
                    key={paper.paper_id}
                    className="px-6 py-4 text-sm text-gray-700 align-top"
                  >
                    {paper.dataset}
                  </td>
                ))}
              </tr>

              {/* Metrics/Results */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900 align-top">
                  Key Results
                </td>
                {papers.map((paper) => (
                  <td
                    key={paper.paper_id}
                    className="px-6 py-4 text-sm text-gray-700 align-top"
                  >
                    {paper.metric_result}
                  </td>
                ))}
              </tr>

              {/* Limitations */}
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900 align-top">
                  Limitations
                </td>
                {papers.map((paper) => (
                  <td
                    key={paper.paper_id}
                    className="px-6 py-4 text-sm text-gray-700 align-top"
                  >
                    {paper.limitation}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Comparison Cards - Mobile/Tablet */}
      <div className="lg:hidden space-y-6">
        {papers.map((paper) => (
          <div
            key={paper.paper_id}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <h3 className="font-serif text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">
              {paper.filename}
            </h3>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-1">
                  Method
                </h4>
                <p className="text-sm text-gray-700">{paper.method}</p>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-1">
                  Dataset
                </h4>
                <p className="text-sm text-gray-700">{paper.dataset}</p>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-1">
                  Key Results
                </h4>
                <p className="text-sm text-gray-700">{paper.metric_result}</p>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-1">
                  Limitations
                </h4>
                <p className="text-sm text-gray-700">{paper.limitation}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Notice */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm text-blue-800">
            Comparison extracted from paper content using AI. Review the source
            papers for complete context.
          </p>
        </div>
      </div>
    </div>
  );
}
