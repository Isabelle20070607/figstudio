import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";

export default function GeneratedCodeEditor({ code }: { code: string }) {
  return <CodeMirror value={code} height="220px" extensions={[python()]} basicSetup={{ lineNumbers: true }} editable={false} />;
}
