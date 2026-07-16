import { ArrowRight, Sparkles } from "lucide-react";

const examples = [
  "Paste a Python traceback and explain the root cause",
  "Drop a GitHub repo URL and draft a README",
  "Optimize this API prompt for fewer tokens",
];

type WorkspaceInputProps = {
  onUseExample: (value: string) => void;
  value: string;
  onChange: (value: string) => void;
};

function WorkspaceInput({ onUseExample, value, onChange }: WorkspaceInputProps): JSX.Element {
  return (
    <section className="mx-auto w-full max-w-6xl px-5 pb-10 pt-14 sm:px-8 lg:pt-20">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-panel sm:p-8">
        <div className="mb-5 flex items-center gap-2 text-sm font-semibold text-primary">
          <Sparkles size={16} />
          Home Workspace
        </div>

        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          Paste anything. Let the workspace route the rest.
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-secondary sm:text-base">
          DevPilot AI classifies your input and sends it through the right pipeline for build, debug, or documentation outcomes.
        </p>

        <label htmlFor="workspace-input" className="sr-only">
          Workspace input
        </label>
        <textarea
          id="workspace-input"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Paste an error, prompt, repository URL, SQL query, API response, or code snippet..."
          className="mt-6 h-44 w-full resize-y rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-primary focus:ring-2 focus:ring-blue-200"
        />

        <div className="mt-4 flex flex-wrap items-center gap-2">
          {examples.map((example) => (
            <button
              key={example}
              onClick={() => onUseExample(example)}
              className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-secondary transition-colors hover:border-slate-300 hover:text-slate-900"
            >
              {example}
            </button>
          ))}
        </div>

        <div className="mt-6 flex items-center gap-3">
          <button className="inline-flex items-center gap-2 rounded-md bg-primary px-5 py-2.5 text-sm font-semibold text-white transition-transform hover:-translate-y-0.5 hover:bg-blue-700">
            Run In Workspace
            <ArrowRight size={15} />
          </button>
          <p className="text-xs text-slate-500">Classifier picks the best pipeline automatically.</p>
        </div>
      </div>
    </section>
  );
}

export default WorkspaceInput;
