import { Code2 } from "lucide-react";

function Navbar(): JSX.Element {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-5 sm:px-8">
        <a href="#" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white">
            <Code2 size={18} />
          </span>
          <span className="text-base font-semibold text-slate-900">DevPilot AI</span>
        </a>
        <div className="hidden items-center gap-7 text-sm font-medium text-secondary md:flex">
          <a href="#" className="transition-colors hover:text-slate-900">
            Workspace
          </a>
          <a href="#" className="transition-colors hover:text-slate-900">
            Projects
          </a>
          <a href="#" className="transition-colors hover:text-slate-900">
            History
          </a>
        </div>
        <div className="flex items-center gap-2">
          <button className="rounded-md px-3 py-2 text-sm font-medium text-secondary transition-colors hover:bg-slate-100 hover:text-slate-900">
            Log in
          </button>
          <button className="rounded-md bg-primary px-3 py-2 text-sm font-semibold text-white transition-transform hover:-translate-y-0.5 hover:bg-blue-700">
            Get Started
          </button>
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
