"use client";

interface WorkspaceHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export default function WorkspaceHeader({
  title,
  description,
  action,
}: WorkspaceHeaderProps) {
  return (
    <div className="mb-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-serif text-4xl text-gray-900 mb-2">{title}</h1>
          {description && (
            <p className="text-lg text-gray-600">{description}</p>
          )}
        </div>
        {action && <div className="flex-shrink-0 ml-4">{action}</div>}
      </div>
    </div>
  );
}
