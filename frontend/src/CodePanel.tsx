import { Check, Clipboard, FileCode2 } from "lucide-react";
import { lazy, Suspense, useEffect, useState } from "react";

const GeneratedCodeEditor = lazy(() => import("./GeneratedCodeEditor"));

export function CodePanel({ code, saveMessage }: { code: string; saveMessage: string }) {
  const [copyMessage, setCopyMessage] = useState("");

  useEffect(() => {
    setCopyMessage("");
  }, [code]);

  async function copyCode() {
    if (!code) {
      return;
    }
    try {
      await navigator.clipboard.writeText(code);
      setCopyMessage("Copied");
    } catch {
      setCopyMessage("Copy failed");
    }
  }

  const statusMessage = copyMessage || saveMessage || "Generated Matplotlib code appears here after preview sync.";

  return (
    <section className="code-panel" data-testid="code-panel">
      <div className="panel-heading">
        <span>
          <FileCode2 size={16} />
          Generated code
        </span>
        <div className="code-panel-actions">
          <small data-testid={copyMessage || saveMessage ? "save-message" : "code-panel-help"}>{statusMessage}</small>
          <button
            type="button"
            className="code-copy-button"
            data-testid="copy-code-button"
            title="Copy code"
            aria-label="Copy code"
            onClick={() => void copyCode()}
            disabled={!code}
          >
            {copyMessage === "Copied" ? <Check size={14} /> : <Clipboard size={14} />}
          </button>
        </div>
      </div>
      <Suspense fallback={<div className="code-loading">Loading code editor</div>}>
        <GeneratedCodeEditor code={code} />
      </Suspense>
    </section>
  );
}
