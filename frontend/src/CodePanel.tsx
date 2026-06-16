import { FileCode2 } from "lucide-react";
import { lazy, Suspense } from "react";

const GeneratedCodeEditor = lazy(() => import("./GeneratedCodeEditor"));

export function CodePanel({ code, saveMessage }: { code: string; saveMessage: string }) {
  return (
    <section className="code-panel" data-testid="code-panel">
      <div className="panel-heading">
        <span>
          <FileCode2 size={16} />
          Generated code
        </span>
        {saveMessage && <small data-testid="save-message">{saveMessage}</small>}
      </div>
      <Suspense fallback={<div className="code-loading">Loading code editor</div>}>
        <GeneratedCodeEditor code={code} />
      </Suspense>
    </section>
  );
}
