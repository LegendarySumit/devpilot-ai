import { BookText, Bug, TerminalSquare } from "lucide-react";
import type { LucideIcon } from "lucide-react";

type QuickAction = {
  title: string;
  subtitle: string;
  example: string;
  icon: LucideIcon;
  tone: string;
};

const quickActions: QuickAction[] = [
  {
    title: "Debug Error",
    subtitle: "Paste stack traces and get root-cause-first guidance.",
    example: "TypeError: 'NoneType' object is not subscriptable",
    icon: Bug,
    tone: "text-danger",
  },
  {
    title: "Prompt Assist",
    subtitle: "Refine task prompts for better quality and clarity.",
    example: "Improve this prompt for generating SQL queries",
    icon: TerminalSquare,
    tone: "text-primary",
  },
  {
    title: "Generate Docs",
    subtitle: "Turn repos and code chunks into useful documentation.",
    example: "https://github.com/example/project",
    icon: BookText,
    tone: "text-success",
  },
];

type QuickActionsProps = {
  onSelect: (value: string) => void;
};

function QuickActions({ onSelect }: QuickActionsProps): JSX.Element {
  return (
    <section className="mx-auto w-full max-w-6xl px-5 pb-16 sm:px-8 sm:pb-20">
      <div className="mb-7">
        <h2 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Quick actions</h2>
        <p className="mt-2 text-sm text-secondary sm:text-base">
          Guided entry points for first-time users without forcing multiple pages.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {quickActions.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.title}
              onClick={() => onSelect(item.example)}
              className="group rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition-shadow hover:shadow-panel"
            >
              <Icon size={22} className={item.tone} />
              <h3 className="mt-3 text-lg font-semibold text-slate-900">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-secondary">{item.subtitle}</p>
              <p className="mt-4 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600 group-hover:border-slate-300">
                {item.example}
              </p>
            </button>
          );
        })}
      </div>
    </section>
  );
}

export default QuickActions;
